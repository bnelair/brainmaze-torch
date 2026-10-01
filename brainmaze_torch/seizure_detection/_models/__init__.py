# Copyright 2020-present, Mayo Clinic Department of Neurology
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path

from torch import load, nn, zeros, unsqueeze, squeeze
import torch.nn.functional as F

_MODEL_DIR = Path(__file__).resolve().parent

TRAINED_MODELS = {'modelA': 'modelA_paper.pt', 'modelB': 'modelB_full.pt'}


def load_trained_model(model_name):
    """Load one of the bundled, pre-trained seizure-detection models.

    Parameters
    ----------
    model_name : {'modelA', 'modelB'}
        ``'modelA'``: the model from the published work (Sladky et al. 2022).
        ``'modelB'``: the same architecture trained on an extended data set.

    Returns
    -------
    SeizureDetectModel
        A ``torch.nn.Module`` on the CPU, in eval mode, with the weights loaded
        strictly (every parameter must match).

    Raises
    ------
    KeyError
        If ``model_name`` is not one of the bundled models.
    """
    if model_name not in TRAINED_MODELS:
        raise KeyError(f"unknown trained model {model_name!r}; available {list(TRAINED_MODELS)}")
    return _ModelsSeizureDetect.load_model(model_name)


class SeizureDetectModel(nn.Module):
    """CNN + 2-layer bidirectional LSTM seizure classifier (Sladky et al. 2022).

    Input: spectrograms of shape ``(batch_size, 100, n_times)`` (see
    :func:`~brainmaze_torch.seizure_detection.preprocess_input`).
    ``forward`` returns ``(logits, probabilities)``, both of shape
    ``(n_times, batch_size, 4)``; class index 3 is "seizure".
    """

    def __init__(self):
        super().__init__()
        # LSTM layer
        self.lstm_out = 100
        # kernel size
        self.nkernel = 20
        self.conv1 = nn.Conv2d(1, self.nkernel, (5, 5), padding=(0, 2))
        self.conv2 = nn.Conv2d(self.nkernel, self.lstm_out*2, (96, 3), padding=(0, 1))
        self.lstm = nn.LSTM(self.lstm_out*2, self.lstm_out, 2, bidirectional=True, dropout=0.5)
        self.fc1 = nn.Linear(2 * self.lstm_out, 4)

    def forward(self, x):
        bs = x.shape[0]
        h0 = zeros(2 * 2, bs, self.lstm_out).to(x.device)
        c0 = zeros(2 * 2, bs, self.lstm_out).to(x.device)
        x = unsqueeze(x, 1)
        x = F.relu(self.conv1(x))
        x = F.dropout(x, p=0.5, training=self.training)
        x = F.relu(self.conv2(x))
        x = F.dropout(x, p=0.5, training=self.training)
        x = squeeze(x)
        if bs == 1:
            x = unsqueeze(x, 0)
        x = x.permute(2, 0, 1)
        x, (hn, cn) = self.lstm(x, (h0, c0))
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.fc1(x)
        return x, F.softmax(x, dim=2)


class _ModelsSeizureDetect:
    """Loader for the bundled ``.pt`` state dicts (keyed by model name)."""

    @staticmethod
    def load_model(model_name):
        state_dict = load(_MODEL_DIR / TRAINED_MODELS[model_name], map_location='cpu')
        mod = SeizureDetectModel()
        mod.load_state_dict(state_dict, strict=True)
        mod.eval()
        return mod
