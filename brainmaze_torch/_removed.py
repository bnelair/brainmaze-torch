"""Clear errors for the parts of brainmaze-torch 0.2.0 that have no equivalent in brainmaze-eeg-models."""
from brainmaze_torch import MIGRATION_URL

_V020_SOURCE = "https://github.com/bnelair/brainmaze-torch/tree/v0.2.0/brainmaze_torch"


def removed_error(qualname, what, advice):
    """An ``ImportError`` naming a removed 0.2.0 object and what to do instead.

    ``ImportError`` (not ``AttributeError``) is used on purpose: for ``from module import name``
    Python replaces an ``AttributeError`` raised by a module ``__getattr__`` by a generic
    "cannot import name" error, which would lose the advice.
    """
    return ImportError(
        f"{qualname} was removed in brainmaze-torch 0.3.0 (the final release, a shim over "
        f"brainmaze-eeg-models, which runs on ONNX Runtime without PyTorch): {what} {advice} "
        f"The 0.2.0 source stays available at {_V020_SOURCE} and on PyPI "
        f"(pip install 'brainmaze-torch==0.2.0', needs torch). Migration: {MIGRATION_URL}"
    )


SEIZURE_MODEL_CLASS_ADVICE = (
    "load_trained_model() now returns a brainmaze_eeg_models.runtime.OnnxModel; use "
    "brainmaze_torch.seizure_detection.load_trained_model(name, device=...) (better: "
    "brainmaze_eeg_models.seizure.load_trained_model) to run the bundled models."
)


def removed_getattr(module_name, removed):
    """Module ``__getattr__`` raising :func:`removed_error` for the names in ``removed``."""
    def __getattr__(name):
        if name in removed:
            what, advice = removed[name]
            raise removed_error(f"{module_name}.{name}", what, advice)
        raise AttributeError(f"module {module_name!r} has no attribute {name!r}")
    return __getattr__
