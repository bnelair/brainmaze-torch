"""Generate ``seizure_segment_1_golden.npz``: reference outputs of the published code.

The reference is produced by the implementation released as brainmaze-torch 0.1.1
(commit ``fb21964``, ``brainmaze_torch/seizure_detection/_seizure_detect.py``),
extracted from git history, NOT by the current code. ``tests/test_golden.py``
compares the current implementation against it wherever the old code produced an
estimate, so any change in the numbers of the published method fails the tests.

Usage (from the repository root, with git history available)::

    pip install -e . "brainmaze-utils>=2.0.0"   # the old code imports utils.signal.buffer
    python tests/data/make_golden_reference.py

The only utils function the old code needs is ``buffer``. The committed ``.npz`` was
generated with brainmaze-utils 2.0.0; regenerating it with the utils PR #28 branch gives a
bit-identical file (verified, max diff 0.0), so 2.0.0 is not strictly required, any
utils version whose ``buffer`` behaves the same works.

Stored per case (``<case>_...``):
  * ``prob``     : old output, float64, length of the old time axis
  * ``defined``  : bool mask of the points the old code actually evaluated
                   (inside the kept, non-discarded part of one of its windows)
  * ``x_stop_s`` / gap and window parameters to rebuild the input
Plus ``spec_sxx`` / ``spec_prob``: the old ``preprocess_input`` spectrogram and
``infer_seizure_probability`` output for the first 300 s window of the fixture.
"""
import importlib.util
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
from scipy.io import loadmat

OLD_COMMIT = "fb21964"
OLD_PATH = "brainmaze_torch/seizure_detection/_seizure_detect.py"
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / "seizure_segment_1_golden.npz"

# name -> (record length in s or None for full, NaN gap (start_s, stop_s) or None, window kwargs)
DEFAULT_KW = dict(window_s=300, step_s=20, discard_edges_s=10)
EMU_KW = dict(window_s=300, step_s=60, discard_edges_s=60)
CASES = {
    "full": (None, None, DEFAULT_KW),
    "trunc655": (655.0, None, DEFAULT_KW),          # end not on the step grid (review R1)
    "trunc645_5": (645.5, None, DEFAULT_KW),
    "gap500_700": (None, (500.0, 700.0), DEFAULT_KW),  # long gap (review R2)
    "gap100_260": (None, (100.0, 260.0), DEFAULT_KW),  # long gap near the recording start
    "emu_trunc655": (655.0, None, EMU_KW),          # bnel-emu-pipeline parameters
}


def load_old_module():
    src = subprocess.run(["git", "show", f"{OLD_COMMIT}:{OLD_PATH}"], cwd=REPO, check=True,
                         capture_output=True, text=True).stdout
    # The old module imports matplotlib.pyplot without using it in the functions we call.
    sys.modules.setdefault("matplotlib", types.ModuleType("matplotlib"))
    sys.modules.setdefault("matplotlib.pyplot", types.ModuleType("matplotlib.pyplot"))
    tmp = Path(tempfile.mkdtemp()) / "old_seizure_detect.py"
    tmp.write_text(src)
    spec = importlib.util.spec_from_file_location("old_seizure_detect", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def old_defined_mask(n, fs, n_len, window_s, step_s, discard_edges_s):
    """Points inside the kept part of a window of the old buffer() windowing."""
    hop = fs // 2
    w2, s2, e2 = int(window_s * 2), int(step_s * 2), int(discard_edges_s * 2)
    last_reg = ((n - w2 * hop) // (s2 * hop)) * s2
    cov = np.zeros(n_len + w2, dtype=bool)
    for b0 in range(0, last_reg + 1, s2):
        cov[b0 + 1 + e2:b0 + w2 - e2] = True
    return cov[:n_len]


def build_input(x_full, fs, stop_s, gap):
    x = x_full.copy() if stop_s is None else x_full[:int(round(stop_s * fs))].copy()
    if gap is not None:
        x[int(gap[0] * fs):int(gap[1] * fs)] = np.nan
    return x


def main():
    import torch
    old = load_old_module()
    dat = loadmat(HERE / "seizure_segment_1.mat")
    x_full = dat["data"].squeeze().astype(np.float64)
    fs = int(float(dat["fs"].squeeze()))
    model = old.load_trained_model("modelA")

    out = {"fs": fs, "old_commit": OLD_COMMIT,
           "versions": f"numpy {np.__version__}, torch {torch.__version__}"}
    for name, (stop_s, gap, kw) in CASES.items():
        x = build_input(x_full, fs, stop_s, gap)
        _, p = old.predict_channel_seizure_probability(x, fs, model, **kw)
        out[f"{name}_prob"] = p.astype(np.float64)
        out[f"{name}_defined"] = old_defined_mask(x.size, fs, p.size, **kw)
        out[f"{name}_stop_s"] = np.nan if stop_s is None else stop_s
        out[f"{name}_gap"] = np.array(gap if gap is not None else (np.nan, np.nan))
        out[f"{name}_kw"] = np.array([kw["window_s"], kw["step_s"], kw["discard_edges_s"]], dtype=float)
        print(f"{name}: {p.size} points, {out[f'{name}_defined'].sum()} defined")

    xw = x_full[:300 * fs].reshape(1, -1)
    sxx = old.preprocess_input(xw, fs)
    out["spec_sxx"] = sxx.astype(np.float32)
    out["spec_prob"] = old.infer_seizure_probability(sxx, model).astype(np.float32)
    np.savez_compressed(OUT, **out)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
