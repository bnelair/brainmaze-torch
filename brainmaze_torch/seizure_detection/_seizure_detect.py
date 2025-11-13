# Copyright 2020-present, Mayo Clinic Department of Neurology
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram
from scipy.stats import zscore
from torch import from_numpy

from brainmaze_torch.seizure_detection._models import load_trained_model
from brainmaze_utils.signal import buffer

def preprocess_input(x, fs, return_axes=False):
    """
    This function will calculate a spectrogram. The spectrogram has shape [batch_size, 100, len(x) in seconds * 2 - 1]
    :param x: raw data input in batch form [batch_size, n-samples]
    :type x: iterable
    :param fs: sampling rate of the input signal
    :return: batch of spectrograms from the input
    :rtype: np.array
    """
    x = np.array(x)

    if x.ndim == 1:
        x = x.reshape((1, -1))

    ii, jj = x.shape
    mu = np.nanmean(x, axis=1)
    std = np.nanstd(x, axis=1)
    x = (x - mu.reshape((ii, 1))) / std.reshape((ii, 1))
    x = np.nan_to_num(x)
    f, t, x = spectrogram(x, fs, nperseg=fs, noverlap=fs / 2, axis=1)
    x2 = x[:, :100, :]
    x = np.empty(x2.shape)
    for kk, xx in enumerate(x2):
        idx = np.sum(xx, axis=0) == 0
        xx[:, ~idx] = zscore(xx[:, ~idx], axis=1)
        x[kk, :, :] = xx
    if return_axes:
        return t, f[:100], x
    return x


def infer_seizure_probability(x, model, use_cuda=False, cuda_number=0):
    """
    infers seizure probability for a given input x; recommended signal len is 300 seconds.
    :param x: output from preprocess_input function, should be in shape [batch_size, 100, time_in_half-seconds]
    :param model: loaded seizure model
    :param use_cuda: if true x is loaded to cuda with cuda_number
    :param cuda_number:
    :return: seizure probability for input x in shape [batch_size, x.shape[2]]
    :rtype: np.array
    """
    x = from_numpy(x)
    batch_size = x.shape[0]
    x = x.float()
    if use_cuda:
        x = x.cuda(cuda_number)

    outputs, probs = model(x)
    probs = probs[:, :, 3].data.cpu().numpy().flatten()
    y = probs.reshape(x.shape[2], batch_size).T
    return y


def predict_channel_seizure_probability(x, fs, model='modelA', use_cuda=False, cuda_number=0, n_batch=128, window_s=300, step_s=20, discard_edges_s=10):
    """Predict seizure probability for a single-channel signal.

    The signal is buffered into overlapping windows, converted to spectrograms,
    run through the seizure model in batches, and the window-level probabilities
    are realigned to the original time axis.

    Args:
        x (array-like): 1D single-channel signal (samples, not channels).
        fs (int | float): Sampling frequency in Hz.
        model (str | object, optional): Model identifier passed to load_trained_model()
            or a preloaded model object. Default is 'modelA'.
        use_cuda (bool, optional): If True, move input to CUDA device for inference.
            Default is False.
        cuda_number (int, optional): CUDA device index when use_cuda is True. Default is 0.
        n_batch (int, optional): Number of buffered windows processed per batch.
            Default is 128.
        window_s (int, optional): Window length in seconds for buffering. Default is 300.
        step_s (int, optional): Step size in seconds between windows. Default is 20.
        discard_edges_s (int, optional): Seconds to discard at each window edge to
            avoid boundary artifacts introduced by buffering/spectrogram and a model. Default is 10.

    Returns:
        tuple:
            txx (numpy.ndarray): Time vector (in seconds) corresponding to the first
                buffered window after alignment (1D array).
            prob (numpy.ndarray): Per-half-second seizure probability values aligned
                to the original time axis. Length is approximately ceil(t_max * 2).

    Raises:
        ValueError: If `x` is not a 1D array (function expects a single channel signal).

    Notes:
        - Recommended input length is at least `window_s` seconds for reliable coverage.
        - Returned probabilities are in [0, 1].
        - The function uses `preprocess_input`, `infer_seizure_probability` and
          `load_trained_model` internally; `model` may be a model name or an already-loaded model.

    Example:
        >>> t, p = predict_channel_seizure_probability(signal, 200, model='modelA')
        >>> # t: time vector for first window; p: probability per half-second

    """
    if x.ndim > 1:
        raise ValueError("input x should be single channel signal (1D array)")

    if discard_edges_s == window_s:
        discard_edges_s = int((window_s/2) - 1)
        warnings.warn("discard_edges_s should NOT be equal to window_s; set to (window_s/2)-1")

    edge = int(np.round(discard_edges_s * 2))

    idx_arr = np.arange(x.shape[0])
    t = idx_arr / fs

    xb = buffer(x, fs, segm_size=window_s, overlap=window_s-step_s, drop=True)
    tb = buffer(t, fs, segm_size=window_s, overlap=window_s-step_s, drop=True)

    valid_buffer_windows = (tb == -1).sum(1) < tb.shape[1]
    xb = xb[valid_buffer_windows]
    tb = tb[valid_buffer_windows]

    if isinstance(model, str):
        model = load_trained_model(model)

    prob = []
    for b in range(0, xb.shape[0], n_batch):
        xb_ = xb[b:b+n_batch]
        txx, f, pxx = preprocess_input(xb_, fs, return_axes=True)
        prob_ = infer_seizure_probability(pxx, model, use_cuda=use_cuda, cuda_number=cuda_number)
        prob += [prob_]

    prob = np.concatenate(prob, 0)

    txx_matrix = np.stack([txx]*prob.shape[0], axis=0)
    txx_matrix = txx_matrix + tb[:, 0].reshape((-1, 1))
    txx_matrix[txx_matrix > t[-1]] = -1

    prob_realigned = np.zeros((prob.shape[0], int(np.ceil(t.max()*2))))
    txx_ref = np.arange(int(np.ceil(t.max()*2))) / 2
    for i in range(0, prob.shape[0]):
        txx_ = txx_matrix[i]
        prob_ = prob[i]

        txx_ = txx_[edge:-edge]
        prob_ = prob_[edge:-edge]

        idx = np.where(txx_ref == txx_[0])[0][0]

        prob_realigned[i, idx:idx+prob_.shape[0]] = prob_



    return txx_ref, prob_realigned.max(0)