
"""
Seizure detection module
available trained models - 'modelA', 'modelB'
modelA is the model from the published work.
modelB had extended training dataset.
Optimal input for the model is 300 second. It is recommended to use only middle part of the signal.

Example
............

.. code-block:: python

    from best.seizure_detection import seizure_detect import load_trained_model
    # load model
    modelA =  load_trai ned_model('modelA')
    # load data
    fs = 500
    x_len = 300
    channels = 3
    # create fake data
    x_input = rand(channels, fs * x_len)
    # preprocess; from raw data to spectrogram
    x = best.deep_learning.seizure_detect.preprocess_input(x_input, fs)
    # get seizure probability; model has 4 output classes, seizure probability is class 4.
    # output is in shape (batch_size, x_len * 2 - 1); probability value for every half-second
    y = best.deep_learning.seizure_detect.infer_seizure_probability(x, modelA)



Sources
............
The seizure detection and training of the model is described in add website.

"""

from brainmaze_torch.seizure_detection._seizure_detect import infer_seizure_probability, preprocess_input, predict_channel_seizure_probability
from brainmaze_torch.seizure_detection._models import load_trained_model

__all__ = [
    'load_trained_model',
    'preprocess_input',
    'infer_seizure_probability',
    'predict_channel_seizure_probability'
]


