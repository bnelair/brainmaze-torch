BrainMaze: Brain Electrophysiology, Behavior and Dynamics Analysis Toolbox - Torch
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. warning::

   **DEPRECATED: brainmaze-torch is retired. Use** `brainmaze-eeg-models <https://github.com/bnelair/brainmaze-eeg-models>`_
   **instead** (``pip install brainmaze-eeg-models``, ``import brainmaze_eeg_models.seizure``).

   Version 0.3.0 is the **final release**: a compatibility shim. It no longer contains PyTorch code or
   model weights and no longer installs ``torch``; it depends on brainmaze-eeg-models and re-exports its
   seizure-detection functions, which run the same models on ONNX Runtime. Importing ``brainmaze_torch``
   emits a ``FutureWarning`` (shown by default, so that everyone still using it sees the notice).
   **The GitHub repository will be archived (read-only) after this release**: there will be no further
   releases, fixes or support here. Please open issues and pull requests in `brainmaze-eeg-models <https://github.com/bnelair/brainmaze-eeg-models>`_.

   Migration notes: https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch


Migrating to brainmaze-eeg-models
"""""""""""""""""""""""""""""""""""

Change the import; the function names, arguments and outputs are the same:

.. code-block:: python

    # before (brainmaze-torch)
    from brainmaze_torch.seizure_detection import predict_channel_seizure_probability
    # after (brainmaze-eeg-models)
    from brainmaze_eeg_models.seizure import predict_channel_seizure_probability

    t, p = predict_channel_seizure_probability(x, fs, model='modelA')   # unchanged call

.. list-table:: brainmaze-torch 0.2.0 -> brainmaze-eeg-models (and what the 0.3.0 shim does)
   :header-rows: 1
   :widths: 34 33 33

   * - brainmaze-torch 0.2.0
     - brainmaze-eeg-models
     - notes
   * - ``brainmaze_torch.seizure_detection.predict_channel_seizure_probability``
     - ``brainmaze_eeg_models.seizure.predict_channel_seizure_probability``
     - same signature and output (also positional ``use_cuda``, ``cuda_number``); CPU by default as in
       0.2.0; new keyword ``device='cpu' | 'cuda' | 'auto'``
   * - ``...seizure_detection.preprocess_input``
     - ``brainmaze_eeg_models.seizure.preprocess_input``
     - identical code and output
   * - ``...seizure_detection.infer_seizure_probability``
     - ``brainmaze_eeg_models.seizure.infer_seizure_probability``
     - same; ``model`` may also be a name (default ``'modelA'``); a ``torch.nn.Module`` raises ``TypeError``
   * - ``...seizure_detection.load_trained_model('modelA' | 'modelB')``
     - ``brainmaze_eeg_models.seizure.load_trained_model``
     - returns an ``OnnxModel`` (not a ``torch.nn.Module``); new ``device`` (default ``'cpu'``),
       ``threads``, ``cuda_device_id``
   * - ``...seizure_detection._models.TRAINED_MODELS``
     - ``brainmaze_eeg_models.seizure.TRAINED_MODELS``
     - same keys; values are now ``(onnx_file, sha256)`` instead of the ``.pt`` file name
   * - ``...seizure_detection._seizure_detect`` (module path)
     - ``brainmaze_eeg_models.seizure``
     - the four functions and ``N_FREQ_BINS``, ``MIN_FS``, ``SEIZURE_CLASS_INDEX`` still import from the old path
   * - ``...seizure_detection._models.SeizureDetectModel`` (PyTorch class), ``_ModelsSeizureDetect``,
       ``_MODEL_DIR``, the ``.pt`` weights
     - none (the ONNX export of the same weights ships with brainmaze-eeg-models)
     - raise ``ImportError`` with migration advice; ``hasattr`` / ``getattr(module, name, default)`` on
       these names raise too (instead of returning False / the default)
   * - ``brainmaze_torch.models_generic`` (``ResLayer1D``, ``ResLayer2D``, ``Attention1D_MIL``)
     - none: generic PyTorch training building blocks; brainmaze-eeg-models is inference only
     - importing the module raises ``ImportError``; copy the classes from the
       `0.2.0 source <https://github.com/bnelair/brainmaze-torch/blob/v0.2.0/brainmaze_torch/models_generic.py>`_
       or pin ``brainmaze-torch==0.2.0``

**One 0.2.0 pattern now raises** ``ValueError`` (loudly, never silently): loading a model and then
asking for the GPU per call,

.. code-block:: python

    m = load_trained_model('modelA')                                # 0.2.0: always a CPU model
    predict_channel_seizure_probability(x, fs, m, use_cuda=True)    # 0.2.0: ran on cuda:0; now ValueError

An ONNX Runtime session cannot move between devices. Choose the device when loading, or pass the
model name:

.. code-block:: python

    m = load_trained_model('modelA', device='cuda', cuda_device_id=0)   # GPU k: cuda_device_id=k
    predict_channel_seizure_probability(x, fs, m)
    # or
    predict_channel_seizure_probability(x, fs, 'modelA', use_cuda=True, cuda_number=0)

Numbers: the ONNX models are exported from the 0.2.0 weights and give the same probabilities as
PyTorch to float32 rounding (typically ~1e-6, at most ~2e-5), with identical NaN masks; the golden
tests of this repository (outputs of the published 0.1.1 code, tolerance 1e-4) pass unchanged on the
shim. For a GPU, install ``onnxruntime-gpu`` in place of ``onnxruntime`` as described in the
`brainmaze-eeg-models README <https://github.com/bnelair/brainmaze-eeg-models#nvidia-gpu>`_.

Silencing the warning while you migrate (better: migrate):

.. code-block:: python

    import warnings
    warnings.filterwarnings("ignore", message="brainmaze-torch is retired", category=FutureWarning)
    import brainmaze_torch.seizure_detection          # the filter must be set before the first import


Installation
"""""""""""""""""""""""""""

.. code-block:: bash

    pip install brainmaze-eeg-models        # recommended: the successor
    pip install -U brainmaze-torch          # only to keep old code running (0.3.0 shim, no torch)

Requirements: Python >= 3.10 and ``brainmaze-eeg-models >= 0.1.0`` (which brings ``numpy``, ``scipy``,
``onnxruntime`` and ``brainmaze-utils``). Upgrading from 0.2.0 removes the bundled ``.pt`` weights but
leaves an installed ``torch`` in place; uninstall it yourself if nothing else needs it. Projects that
need the PyTorch implementation itself can pin ``brainmaze-torch==0.2.0`` (``torch >= 2.3``); it stays
on PyPI but is not maintained.


History
"""""""""""""""""""

- **0.3.0** (final): compatibility shim over brainmaze-eeg-models (see above); ``torch`` and the ``.pt``
  models removed; the repository is archived after this release.
- **0.2.0**: NaN for unevaluated time, full coverage of the recording, stricter input validation,
  dependencies reduced to ``numpy``, ``scipy``, ``torch >= 2.3``. Details:
  `RELEASING.md <https://github.com/bnelair/brainmaze-torch/blob/main/RELEASING.md>`_.

This project was originally developed as a part of the `BEhavioral STate Analysis Toolbox (BEST)
<https://github.com/bnelair/best-toolbox>`_ project; development then moved to the BrainMaze project and,
for the trained models, to brainmaze-eeg-models.


Releasing
'''''''''''''''''''''''''''''''

0.3.0 is the final release (see `RELEASING.md <https://github.com/bnelair/brainmaze-torch/blob/main/RELEASING.md>`_):
a code owner runs **Prepare release** (*minor*: 0.2.0 -> 0.3.0) and merges the ``Release v0.3.0`` pull
request; the **Release** workflow tests, builds, publishes to PyPI (org API token ``PYPI_Token_General``),
tags and creates the GitHub release. The repository is archived afterwards.


License
""""""""""""""""""
This software is licensed under BSD-3Clause license. For details see the `LICENSE <https://github.com/bnelair/brainmaze-torch/blob/main/LICENSE>`_ file in the root directory of this project.


Acknowledgment
"""""""""""""""""""
This code was developed and originally published for the first time by (Mivalt 2022, and Sladky 2022). Additionally, codes related to individual projects available in this repository are stated below. When using these models (now in brainmaze-eeg-models), we appreciate you citing the papers related to the utilized functionality. Please, see the sections below for references to individual submodules.

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


