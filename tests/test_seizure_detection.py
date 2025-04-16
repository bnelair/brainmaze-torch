import pytest

from brainmaze_torch.seizure_detection import infer_seizure_probability, preprocess_input, load_trained_model

import torch
import numpy as np

def test_seizure_detector():
    fs = 250
    length = 60

    model = load_trained_model('modelA')

    x = np.random.randn(1, length * fs)
    xinp = preprocess_input(x, fs)
    y = infer_seizure_probability(xinp, model, use_cuda=False)

    assert y.shape[1] == xinp.shape[2]
    assert y.shape[0] == xinp.shape[0]


