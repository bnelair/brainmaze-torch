"""Removed in brainmaze-torch 0.3.0: importing this module raises ``ImportError``.

``ResLayer1D``, ``ResLayer2D`` and ``Attention1D_MIL`` were generic PyTorch (``torch.nn.Module``)
building blocks for training models. brainmaze-eeg-models is inference only (ONNX Runtime, no
PyTorch) and has no equivalent; none of the bundled models needs them.
"""
from brainmaze_torch._removed import removed_error

raise removed_error(
    "brainmaze_torch.models_generic (ResLayer1D, ResLayer2D, Attention1D_MIL)",
    "these were generic PyTorch training building blocks (torch.nn.Module) and brainmaze-eeg-models "
    "is inference only, so there is no replacement.",
    "If you train models with them, copy the classes (about 50 lines of plain PyTorch) from the "
    "0.2.0 source into your project, or pin brainmaze-torch==0.2.0.",
)
