
BrainMaze: Brain Electrophysiology, Behavior and Dynamics Analysis Toolbox - Torch
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

This toolbox provides tools for processing of intracranial EEG recordings. Specifically, this tool comprises Pytorch modules and utilities developed within this project. See below and documentation for specific sections. This tool was separated from the BrainMaze toolbox to support a convenient and lightweight sharing of these tools across projects.

This project was originally developed as a part of the `BEhavioral STate Analysis Toolbox (BEST) <https://github.com/bnelair/best-toolbox>`_ project. However, the development has transferred to the BrainMaze project.



Documentation
"""""""""""""""

Documentation is available `here <https://bnelair.github.io/brainmaze-torch/>`_.


Installation
"""""""""""""""""""""""""""

.. code-block:: bash

    pip install brainmaze-torch

Requirements: Python >= 3.10, ``numpy >= 1.24`` (1.24, 1.26 and 2.x are tested), ``scipy >= 1.10`` and
``torch >= 2.3`` (older torch wheels cannot use numpy 2: ``torch.from_numpy`` fails with "Numpy is not
available"). The CPU build of PyTorch is sufficient; CUDA is optional.


Seizure probability: quick start
"""""""""""""""""""""""""""""""""""""

.. code-block:: python

    import numpy as np
    from brainmaze_torch.seizure_detection import predict_channel_seizure_probability

    fs = 500                                  # Hz; whole, even number >= 200 (500.0 is fine)
    x = np.random.randn(fs * 600)             # one channel, 10 min; NaN marks missing data
    t, p = predict_channel_seizure_probability(x, fs, model='modelA')
    # t[k] = k * 0.5 s; p[k] = seizure probability of the 1 s of signal centred on t[k]

What the output means:

- One value every 0.5 s, ``len(p) == len(x) // (fs // 2)``. The whole recording is covered, including its
  start and end.
- **NaN means "not evaluated", never "no seizure".** ``p`` is NaN at ``t = 0`` and for every 1 s segment that
  contains a NaN/inf sample (a gap) or a flat signal (e.g. a disconnected channel); every other segment has a
  value. Use ``np.nanmax`` / ``np.isfinite`` downstream, and do not replace NaN by 0.
- Wherever version 0.1.1 produced an estimate, the values are identical (pinned by golden-value tests against
  0.1.1's output). Inside an evaluated window, gap samples are zero-filled for the model as before, so valid
  data right next to a long gap can be influenced by it; ``min_valid_fraction > 0`` prefers windows with more
  valid data there (this changes values next to long gaps and is not validated).
- ``fs`` must be a whole, even number of Hz and at least 200 Hz. Other rates raise ``ValueError``; resample first
  (e.g. ``scipy.signal.resample_poly``). Anti-aliasing is up to the caller. These rules come from the spectrogram
  grid (1 s segments, 0.5 s hop, 100 one-Hz bins), not from the training data.
- At 200-256 Hz the anti-alias filter of the amplifier or resampler usually attenuates the top bins (from about
  0.4 x fs, i.e. 80-100 Hz). The model did not see such spectra in training, so this is a silent domain shift;
  prefer higher rates.
- The recording must be at least ``window_s`` (default 300 s) long, and ``step_s`` must not exceed
  ``window_s - 2 * discard_edges_s - 0.5``; otherwise a ``ValueError`` explains what to change.

See the `documentation <https://bnelair.github.io/brainmaze-torch/>`_ for the low-level API
(``preprocess_input``, ``infer_seizure_probability``) and the details of the time grid.

Changes since 0.1.1 (breaking; the next release is >= 0.2.0)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

- ``predict_channel_seizure_probability`` returns **NaN** at ``t = 0`` and for gap / flat 1 s segments
  (0.1.1: a number, or 0 where nothing was evaluated). Use NaN-aware functions; never ``fillna(0)``.
- The output has ``len(x) // (fs // 2)`` points: one fewer than 0.1.1 when the recording is not a whole number of
  half-seconds (that last point lay beyond the data and was always 0).
- The recording edges and the tail after the last regular window now get values (0.1.1: 0). Wherever 0.1.1
  produced an estimate the values are unchanged.
- ``fs`` must be a whole, even number >= 200 Hz; ``discard_edges_s == window_s``, a ``step_s`` that would leave
  uncovered time, and recordings shorter than ``window_s`` raise ``ValueError``.
- New keyword arguments ``min_valid_fraction`` (default 0.0 = 0.1.1 behaviour) and ``fill_recording_edges``.
- Dependencies reduced to ``numpy``, ``scipy`` and ``torch >= 2.3``; packages that 0.1.1 pulled in transitively
  (``brainmaze_utils``, ``torchvision``, ``torchaudio``, ``pandas``, ...) must be required by your own project if
  you use them. The private ``brainmaze_torch._config`` module was removed.

Details: `RELEASING.md <https://github.com/bnelair/brainmaze-torch/blob/main/RELEASING.md>`_.

How to contribute
"""""""""""""""""""""""""""

The project has 2 main protected branches *main* that contains official software releases and *dev* that contains the latest feature implementations shared with developers.
To implement a new feature a new branch should be created from the *dev* branch with name pattern of *developer_identifier/feature_name*.

After the feature is implemented, a pull request can be created to merge the feature branch into the *dev* branch with. Pull requests need to be reviewed by the code owners.
Releasing
'''''''''''''''''''''''''''''''

Releases are automated and never bypass branch protection. To cut a release, a code owner runs the **Prepare release** GitHub Action (*Actions* tab, ``workflow_dispatch``) and selects the bump (*patch* / *minor* / *major*). This opens a small ``Release vX.Y.Z`` pull request that bumps ``[project].version`` in ``pyproject.toml`` on a ``release/bump-*`` branch off *main*. Once a code owner approves and merges that pull request into *main*, the **Release** workflow runs the tests, builds the distributions, publishes them to PyPI (org API token ``PYPI_Token_General``), and then tags the version and creates the GitHub release. ``pyproject.toml`` is the single source of truth for the version.

Promotion of features from *dev* to *main* is independent of releases and **must not change** ``[project].version``: a *Version guard* CI check flags any pull request outside the release flow that edits it. The check is advisory (no ruleset requires it), so reviewers must not merge a pull request it flags.

See `RELEASING.md <RELEASING.md>`_ for the step-by-step guide and publishing credentials and recovery.

Building the documentation
'''''''''''''''''''''''''''''''

New functions need numpy-style docstrings (rendered by Sphinx with ``napoleon``). The documentation is built from ``docs_src/`` and published to GitHub Pages by the **Docs** workflow (``main`` at the site root, ``dev`` under ``/dev/``). To build it locally:

.. code-block:: bash

    pip install -r docs_src/requirements.txt -e .
    sphinx-build -b html docs_src/source docs

``docs/`` is ignored by git and must not be committed.


License
""""""""""""""""""
This software is licensed under BSD-3Clause license. For details see the `LICENSE <https://github.com/bnelair/brainmaze-torch/blob/main/LICENSE>`_ file in the root directory of this project.


Acknowledgment
"""""""""""""""""""
This code was developed and originally published for the first time by (Mivalt 2022, and Sladky 2022). Additionally, codes related to individual projects available in this repository are stated below. When using this toolbox, we appreciate you citing the papers related to the utilized functionality. Please, see the sections below for references to individual submodules.

 | F. Mivalt et V. Kremen et al., “Electrical brain stimulation and continuous behavioral state tracking in ambulatory humans,” J. Neural Eng., vol. 19, no. 1, p. 016019, Feb. 2022, doi: 10.1088/1741-2552/ac4bfd.
 |
 | V. Sladky et al., “Distributed brain co-processor for tracking spikes, seizures and behaviour during electrical brain stimulation,” Brain Commun., vol. 4, no. 3, May 2022, doi: 10.1093/braincomms/fcac115.


Seizure detection
'''''''''''''''''''''''''''''''''''''''''''''''
 | V. Sladky et al., “Distributed brain co-processor for tracking spikes, seizures and behaviour during electrical brain stimulation,” Brain Commun., vol. 4, no. 3, May 2022, doi: 10.1093/braincomms/fcac115.


Funding
""""""""""""""""""

Individual sections of this code were developed under different projects including:

- NIH Brain Initiative UH2&3 NS095495 - *Neurophysiologically-Based Brain State Tracking & Modulation in Focal Epilepsy*,
- NIH U01-NS128612 - *An Ecosystem of Techmology and Protocols for Adaptive Neuromodulation Research in Humans*,
- DARPA - HR0011-20-2-0028 *Manipulating and Optimizing Brain Rhythms for Enhancement of Sleep (Morpheus)*.
- FEKT-K-22-7649 realized within the project Quality Internal Grants of the Brno University of Technology (KInG BUT), Reg. No. CZ.02.2.69/0.0/0.0/19_073/0016948, which is financed from the OP RDE.


