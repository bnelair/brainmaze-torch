"""Deprecated 0.2.0 module path: re-exports the model loader of :mod:`brainmaze_eeg_models.seizure`.

The ``.pt`` (PyTorch) weights are no longer shipped; the models are the ONNX exports of the same
weights bundled with brainmaze-eeg-models.
"""
from brainmaze_eeg_models.seizure import TRAINED_MODELS, load_trained_model

from brainmaze_torch._removed import SEIZURE_MODEL_CLASS_ADVICE, removed_getattr

__all__ = ['TRAINED_MODELS', 'load_trained_model']

_PT = ("the PyTorch model class and its .pt weights are gone.", SEIZURE_MODEL_CLASS_ADVICE)
__getattr__ = removed_getattr(__name__, {
    'SeizureDetectModel': _PT,
    '_ModelsSeizureDetect': _PT,
    '_MODEL_DIR': _PT,
})
