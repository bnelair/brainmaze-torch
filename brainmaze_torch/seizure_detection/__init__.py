"""
Deprecated: re-exports :mod:`brainmaze_eeg_models.seizure` (brainmaze-torch 0.3.0, final release).

Seizure probability from intracranial EEG with a CNN + bidirectional LSTM applied to
spectrograms (Sladky et al. 2022, Brain Communications, doi:10.1093/braincomms/fcac115).
Every function here **is** the brainmaze-eeg-models function (same object, ONNX Runtime, no
PyTorch); the names, arguments and outputs are those of brainmaze-torch 0.2.0. Change the import:

.. code-block:: python

    # before
    from brainmaze_torch.seizure_detection import predict_channel_seizure_probability
    # after
    from brainmaze_eeg_models.seizure import predict_channel_seizure_probability

Differences from 0.2.0 (details in the migration notes,
https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch):

- :func:`load_trained_model` returns a ``brainmaze_eeg_models.runtime.OnnxModel``, not a
  ``torch.nn.Module``; passing a PyTorch model to the inference functions raises ``TypeError``.
- ``m = load_trained_model(name)`` followed by ``use_cuda=True`` raises ``ValueError`` (an ONNX
  session cannot move to the GPU per call). Use ``load_trained_model(name, device='cuda',
  cuda_device_id=k)``, or pass the model name with ``use_cuda=True, cuda_number=k``.
- Probabilities equal the PyTorch ones to float32 rounding (typically ~1e-6, at most ~2e-5);
  NaN masks are identical.
- ``TRAINED_MODELS`` has the same keys (``'modelA'``, ``'modelB'``); its values are now
  ``(onnx_file, sha256)`` instead of the ``.pt`` file name.
"""
from brainmaze_eeg_models.seizure import (
    TRAINED_MODELS,
    infer_seizure_probability,
    load_trained_model,
    predict_channel_seizure_probability,
    preprocess_input,
)

from brainmaze_torch._removed import SEIZURE_MODEL_CLASS_ADVICE, removed_getattr

__all__ = [
    'TRAINED_MODELS',
    'load_trained_model',
    'preprocess_input',
    'infer_seizure_probability',
    'predict_channel_seizure_probability'
]

__getattr__ = removed_getattr(__name__, {
    'SeizureDetectModel': ("the PyTorch model class is gone.", SEIZURE_MODEL_CLASS_ADVICE),
})
