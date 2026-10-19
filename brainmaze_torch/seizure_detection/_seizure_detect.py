"""Deprecated 0.2.0 module path: re-exports :mod:`brainmaze_eeg_models.seizure`."""
from brainmaze_eeg_models.seizure import (
    infer_seizure_probability,
    load_trained_model,
    predict_channel_seizure_probability,
    preprocess_input,
)

#: Number of spectrogram frequency bins (1 Hz each, 0..99 Hz) the model expects.
N_FREQ_BINS = 100
#: Minimum supported sampling rate in Hz (needs >= 100 one-Hz bins below Nyquist).
MIN_FS = 200
#: Index of the seizure class in the model's 4-class softmax output.
SEIZURE_CLASS_INDEX = 3

__all__ = [
    'N_FREQ_BINS', 'MIN_FS', 'SEIZURE_CLASS_INDEX',
    'load_trained_model', 'preprocess_input', 'infer_seizure_probability',
    'predict_channel_seizure_probability',
]
