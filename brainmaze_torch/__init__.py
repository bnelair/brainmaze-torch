"""brainmaze-torch is retired: this final release (0.3.0) is a compatibility shim.

The seizure-detection functions now live in **brainmaze-eeg-models**
(``brainmaze_eeg_models.seizure``; ONNX Runtime, no PyTorch). ``brainmaze_torch`` only
re-exports them and emits one ``DeprecationWarning`` when it is imported. Migrate by
changing the import::

    # before
    from brainmaze_torch.seizure_detection import predict_channel_seizure_probability
    # after
    from brainmaze_eeg_models.seizure import predict_channel_seizure_probability

Migration notes: https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch
"""
import sys as _sys
import warnings as _warnings
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("brainmaze-torch")
except PackageNotFoundError:
    __version__ = "0.0.0"

#: Where the migration from brainmaze-torch is documented.
MIGRATION_URL = "https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch"

_DEPRECATION_MESSAGE = (
    "brainmaze-torch is retired; this is its final release, a compatibility shim that re-exports "
    "brainmaze-eeg-models (ONNX Runtime, no PyTorch). Install brainmaze-eeg-models and change "
    "'brainmaze_torch.seizure_detection' to 'brainmaze_eeg_models.seizure' (same function names "
    "and outputs). One behaviour change: a model from load_trained_model(name) is now an ONNX "
    "session that cannot move to a GPU per call, so load_trained_model(name) followed by "
    "use_cuda=True raises ValueError; use load_trained_model(name, device='cuda', "
    "cuda_device_id=k) instead (or pass the model name with use_cuda=True). The PyTorch building "
    "blocks of brainmaze_torch.models_generic are gone. Migration: " + MIGRATION_URL
)


def _caller_stacklevel():
    """``stacklevel`` that attributes the warning to the code that imported brainmaze_torch.

    ``warnings.warn`` already skips the import machinery's frames (``importlib._bootstrap``)
    when it counts ``stacklevel``; this also skips the frames of this package's own modules and of ``importlib.import_module``
    (e.g. ``import brainmaze_torch.seizure_detection`` runs this module from inside the
    import of the subpackage). The warning then points at the user's ``import`` line and is
    shown by default when that line is in ``__main__``.
    """
    def internal(frame):  # same rule as warnings._is_internal_frame
        filename = frame.f_code.co_filename
        return 'importlib' in filename and '_bootstrap' in filename

    level = 1
    frame = _sys._getframe(1)  # the module body that calls warn() = stacklevel 1
    while frame is not None:
        if not internal(frame):
            name = frame.f_globals.get("__name__", "")
            if not (name.startswith("brainmaze_torch") or name == "importlib"):  # importlib.import_module
                break
            level += 1
        frame = frame.f_back
    return level


# Emitted once per process: a module body runs only on its first import.
_warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=_caller_stacklevel())

__all__ = ['__version__', 'MIGRATION_URL']
