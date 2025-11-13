import pytest

from pathlib import Path


import torch
import numpy as np
from scipy.io import savemat, loadmat
from brainmaze_torch.seizure_detection._seizure_detect import (
    infer_seizure_probability,
    predict_channel_seizure_probability,
    preprocess_input, load_trained_model,
)


def test_seizure_detector():
    fs = 250
    length = 60

    model = load_trained_model('modelA')

    x = np.random.randn(1, length * fs)
    xinp = preprocess_input(x, fs)
    y = infer_seizure_probability(xinp, model, use_cuda=False)

    assert y.shape[1] == xinp.shape[2]
    assert y.shape[0] == xinp.shape[0]












def test_seizure_detection_real_data():
    pth = Path(__file__).resolve()
    pth_data = pth.parent / 'data' / 'seizure_segment_1.mat'
    dat = loadmat(pth_data)

    idx_ref_s = 380*2 # start where needs to be > 0.8 # < 0.8 at 20 s before this
    idx_ref_e = 450*2 # end where needs to be > 0.8 # < 0.8 at 20 s before this

    x = dat['data'].squeeze().copy()
    fs = float(dat['fs'].squeeze())
    fs = int(fs)

    modelA = load_trained_model('modelA')
    modelB = load_trained_model('modelB')

    txx_ref, prob = predict_channel_seizure_probability(x, fs, 'modelA', False, 1)

    # safe clamp helpers to avoid slicing outside array bounds
    idx_ref_s_clamped = max(0, min(idx_ref_s, prob.shape[0]))
    idx_ref_e_clamped = max(0, min(idx_ref_e, prob.shape[0]))

    bl_1 = (np.arange(prob.shape[0]) > idx_ref_s_clamped) & (np.arange(prob.shape[0]) < idx_ref_e_clamped)
    bl_2 = (np.arange(prob.shape[0]) > idx_ref_s_clamped-40) & (np.arange(prob.shape[0]) < idx_ref_e_clamped+40)

    # Assert that within the expected seizure interval there is a high probability (>0.8)
    assert np.all(prob[bl_1] > 0.8)

    # Assert that in the 10 seconds immediately before the seizure interval probabilities are low (<0.8)
    assert np.all(prob[~bl_2] < 0.8)


    # vmin = np.quantile(pxx, 0.05)
    # vmax = np.quantile(pxx, 0.95)
    #
    # plt.figure(figsize=(24, 12))
    # ax = plt.subplot(3, 1, 1)
    # plt.plot(t_, x_)
    # plt.subplot(3, 1, 2, sharex=ax)
    # plt.pcolormesh(txx_, f_, pxx_[0], vmin=vmin, vmax=vmax)
    # plt.subplot(3, 1, 3, sharex=ax)
    # plt.plot(txx_, prob_)
    # # plt.plot(txx_, prob2_)
    # plt.ylim([0, 1])
    # plt.show()

    # t = np.arange(0, x.shape[0]) / fs
    # for k in range(150*fs, 500*fs, 20*fs):
    #     print(k)
    #     x_ = x[k:k + (fs*300)]
    #     t_ = t[k:k + (fs*300)]
    #
    #     txx_ , f_, pxx_ = preprocess_input(x_, fs, return_axes=True)
    #     prob_ = infer_seizure_probability(pxx_, modelA, use_cuda=False)
    #     prob_ = prob_.squeeze()
    #
    #     prob2_ = infer_seizure_probability(pxx_, modelB, use_cuda=False)
    #     prob2_ = prob2_.squeeze()
    #
    #
    #
    #     # prob2_ = predict_channel_seizure_probability(x_, fs, model='modelB', use_cuda=False)
    #
    #
    #     txx_ += t_[0]
    #
    #     plt.figure(figsize=(24, 12))
    #     ax = plt.subplot(3, 1, 1)
    #     plt.plot(t_, x_)
    #     plt.subplot(3, 1, 2, sharex=ax)
    #     plt.pcolormesh(txx_, f_, pxx_[0], vmin=vmin, vmax=vmax)
    #     plt.subplot(3, 1, 3, sharex=ax)
    #     plt.plot(txx_, prob_)
    #     # plt.plot(txx_, prob2_)
    #     plt.ylim([0, 1])
    #     plt.show()

        #
        # x_ = x[340*fs:490*fs]
        # t_ = t[340*fs:490*fs]
        # plt.figure(figsize=(24, 6))
        # plt.plot(t_, x_, linewidth=0.8, color='k')
        # plt.xlabel('time (s)', fontsize=24)
        # plt.show()
        #


def test_process_data_over_multiple_batches():
    fs = 256
    dur_s = 60
    x = np.random.randn(dur_s*fs)
    txx_ref, prob = predict_channel_seizure_probability(x, fs, 'modelA', False, 1, window_s=10, step_s=1, n_batch=16, discard_edges_s=0.5)

    assert txx_ref.shape[0]
    assert prob.shape[0] == txx_ref.shape[0]



def test_process_data_with_nans():
    fs = 256
    dur_s = 60
    x = np.random.randn(dur_s*fs)
    x[15*fs:45*fs] = np.nan

    txx_ref, prob = predict_channel_seizure_probability(x, fs, 'modelA', False, 1, window_s=10, step_s=1, n_batch=16, discard_edges_s=0.5)

    assert np.isnan(prob).sum() == 0