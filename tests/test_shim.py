"""brainmaze-torch 0.3.0 is a shim over brainmaze-eeg-models: pin down that contract.

- every public 0.2.0 name still imports and IS the brainmaze-eeg-models object;
- 0.2.0-style calls give the brainmaze-eeg-models outputs (golden fixture, both models);
- exactly one DeprecationWarning per process, naming the successor and the migration page,
  attributed to the importing code (so it is shown by default for scripts);
- the names without an equivalent raise ImportError with migration advice;
- no PyTorch anywhere (not imported, not a dependency).
"""
import importlib
import importlib.metadata as md
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

import brainmaze_eeg_models.seizure as successor
import brainmaze_torch
import brainmaze_torch.seizure_detection as sd
from brainmaze_torch.seizure_detection import _models as sd_models
from brainmaze_torch.seizure_detection import _seizure_detect as sd_detect

DATA = Path(__file__).resolve().parent / "data"
MIGRATION_URL = "https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch"
# The shim calls the very same functions, so the outputs are bit-identical; 1e-4 is the
# family's golden tolerance (as required for the shim) and documents the contract.
ATOL = 1e-4

API_020 = ['load_trained_model', 'preprocess_input', 'infer_seizure_probability',
           'predict_channel_seizure_probability']


def _run(code, *args):
    """Run ``code`` in a fresh interpreter (module imports and warnings start clean)."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONWARNINGS"}
    return subprocess.run([sys.executable, *args, "-c", textwrap.dedent(code)],
                          capture_output=True, text=True, env=env, timeout=300)


@pytest.fixture(scope="module")
def fixture_signal():
    dat = loadmat(DATA / "seizure_segment_1.mat")
    return dat["data"].squeeze().astype(np.float64), int(float(dat["fs"].squeeze()))


# --------------------------------------------------------------------------- #
# re-exports
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("name", API_020)
def test_public_names_are_the_successor_objects(name):
    assert name in sd.__all__
    assert getattr(sd, name) is getattr(successor, name)
    assert getattr(sd_detect, name) is getattr(successor, name)


def test_private_020_module_paths_still_work():
    assert sd_models.load_trained_model is successor.load_trained_model
    assert sd_models.TRAINED_MODELS is successor.TRAINED_MODELS
    assert sd.TRAINED_MODELS is successor.TRAINED_MODELS
    assert set(sd.TRAINED_MODELS) == {'modelA', 'modelB'}   # same keys as 0.2.0
    assert (sd_detect.N_FREQ_BINS, sd_detect.MIN_FS, sd_detect.SEIZURE_CLASS_INDEX) == (100, 200, 3)


def test_star_import():
    ns = {}
    exec("from brainmaze_torch.seizure_detection import *", ns)
    assert set(API_020) <= set(ns)


def test_version_and_migration_url():
    assert brainmaze_torch.__version__ == md.version("brainmaze-torch")
    assert brainmaze_torch.MIGRATION_URL == MIGRATION_URL


# --------------------------------------------------------------------------- #
# 0.2.0-style calls == brainmaze-eeg-models
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("model_name", ["modelA", "modelB"])
@pytest.mark.parametrize("gap_s", [None, (500, 700)])
def test_020_style_call_matches_successor(fixture_signal, model_name, gap_s):
    x, fs = fixture_signal
    x = x.copy()
    if gap_s is not None:
        x[gap_s[0] * fs:gap_s[1] * fs] = np.nan

    # 0.2.0 positional style: (x, fs, model, use_cuda, cuda_number, n_batch)
    t_old, p_old = sd.predict_channel_seizure_probability(x, fs, model_name, False, 0, 128)
    t_new, p_new = successor.predict_channel_seizure_probability(x, fs, model=model_name)

    np.testing.assert_array_equal(t_old, t_new)
    np.testing.assert_array_equal(np.isnan(p_old), np.isnan(p_new))
    assert np.isfinite(p_new).sum() > 1000
    np.testing.assert_allclose(p_old, p_new, rtol=0, atol=ATOL, equal_nan=True)


def test_020_style_low_level_matches_successor(fixture_signal):
    x, fs = fixture_signal
    windows = np.stack([x[:300 * fs], x[300 * fs:600 * fs]])
    model = sd.load_trained_model('modelA')                    # 0.2.0: no device argument
    sxx = sd.preprocess_input(windows, fs)
    y_old = sd.infer_seizure_probability(sxx, model, use_cuda=False, cuda_number=0)
    y_new = successor.infer_seizure_probability(
        successor.preprocess_input(windows, fs), successor.load_trained_model('modelA'))
    assert y_old.shape == (2, 599)
    np.testing.assert_allclose(y_old, y_new, rtol=0, atol=ATOL)


def test_020_gpu_per_call_pattern_raises_with_replacement():
    """The one documented 0.2.0 pattern that no longer works must fail loudly."""
    model = sd.load_trained_model('modelA')
    x = np.random.default_rng(0).standard_normal(30 * 256)
    with pytest.raises(ValueError, match=r"load_trained_model\(\.\.\., device='cuda'\)"):
        sd.predict_channel_seizure_probability(x, 256, model, use_cuda=True, window_s=10, step_s=1,
                                               discard_edges_s=0.5)
    with pytest.raises(ValueError, match="device='cuda'"):
        sd.infer_seizure_probability(sd.preprocess_input(x[:10 * 256], 256), model, use_cuda=True)


def test_torch_module_model_raises_type_error():
    class FakeTorchModel:  # stands in for a torch.nn.Module from brainmaze-torch 0.2.0
        pass
    sxx = sd.preprocess_input(np.random.default_rng(1).standard_normal(10 * 256), 256)
    with pytest.raises(TypeError, match="PyTorch models"):
        sd.infer_seizure_probability(sxx, FakeTorchModel())


# --------------------------------------------------------------------------- #
# DeprecationWarning
# --------------------------------------------------------------------------- #
def test_deprecation_warning_fires_exactly_once():
    res = _run("""
        import importlib, warnings
        with warnings.catch_warnings(record=True) as rec:
            warnings.simplefilter("always")
            for name in ["brainmaze_torch", "brainmaze_torch.seizure_detection",
                         "brainmaze_torch.seizure_detection._models",
                         "brainmaze_torch.seizure_detection._seizure_detect"]:
                importlib.import_module(name)
            import brainmaze_torch
            from brainmaze_torch.seizure_detection import predict_channel_seizure_probability
        dep = [w for w in rec if issubclass(w.category, DeprecationWarning)
               and "brainmaze-torch is retired" in str(w.message)]
        print(len(dep))
        print(dep[0].filename)
        print(str(dep[0].message))
    """)
    assert res.returncode == 0, res.stderr
    count, filename, message = res.stdout.splitlines()[:3]
    assert count == "1"
    # attributed to the importing code, not to importlib or brainmaze_torch itself
    assert "brainmaze_torch" not in filename and "importlib" not in filename
    assert "brainmaze-eeg-models" in message
    assert "brainmaze_eeg_models.seizure" in message
    assert MIGRATION_URL in message
    assert "load_trained_model(name, device='cuda', cuda_device_id=k)" in message


@pytest.mark.parametrize("stmt", [
    "import brainmaze_torch",
    "import brainmaze_torch.seizure_detection",
    "from brainmaze_torch.seizure_detection import predict_channel_seizure_probability",
])
def test_deprecation_warning_shown_by_default_for_scripts(stmt):
    # Python's default filters show DeprecationWarning only when it is attributed to __main__:
    # the shim's stacklevel must point at the user's import line for every import form.
    res = _run(stmt)
    assert res.returncode == 0, res.stderr
    assert res.stderr.count("DeprecationWarning: brainmaze-torch is retired") == 1, res.stderr


def test_deprecation_warning_can_be_turned_into_error():
    res = _run("import brainmaze_torch", "-W", "error::DeprecationWarning")
    assert res.returncode != 0 and "brainmaze-torch is retired" in res.stderr


# --------------------------------------------------------------------------- #
# names without an equivalent
# --------------------------------------------------------------------------- #
UNMAPPABLE = [
    ("brainmaze_torch.models_generic", "ResLayer1D"),
    ("brainmaze_torch.models_generic", "ResLayer2D"),
    ("brainmaze_torch.models_generic", "Attention1D_MIL"),
    ("brainmaze_torch.seizure_detection", "SeizureDetectModel"),
    ("brainmaze_torch.seizure_detection._models", "SeizureDetectModel"),
    ("brainmaze_torch.seizure_detection._models", "_ModelsSeizureDetect"),
    ("brainmaze_torch.seizure_detection._models", "_MODEL_DIR"),
]


def _assert_advice(err):
    msg = str(err)
    assert "removed in brainmaze-torch 0.3.0" in msg
    assert "brainmaze-eeg-models" in msg
    assert "brainmaze-torch==0.2.0" in msg
    assert MIGRATION_URL in msg


@pytest.mark.parametrize("module, name", UNMAPPABLE)
def test_unmappable_from_import_raises_with_advice(module, name):
    with pytest.raises(ImportError) as exc:
        exec(f"from {module} import {name}", {})
    _assert_advice(exc.value)


@pytest.mark.parametrize("module, name", [u for u in UNMAPPABLE if "models_generic" not in u[0]])
def test_unmappable_attribute_access_raises_with_advice(module, name):
    mod = importlib.import_module(module)
    with pytest.raises(ImportError) as exc:
        getattr(mod, name)
    _assert_advice(exc.value)
    assert name not in dir(mod)


def test_models_generic_module_import_raises_every_time():
    for _ in range(2):  # a failed import is not cached: it must raise again, not half-import
        with pytest.raises(ImportError, match="ResLayer1D, ResLayer2D, Attention1D_MIL") as exc:
            importlib.import_module("brainmaze_torch.models_generic")
        _assert_advice(exc.value)
        assert "no replacement" in str(exc.value)


def test_unknown_attribute_is_a_plain_attribute_error():
    assert not hasattr(sd, "no_such_name")
    assert not hasattr(sd_models, "no_such_name")


# --------------------------------------------------------------------------- #
# no PyTorch
# --------------------------------------------------------------------------- #
def test_torch_is_not_imported():
    res = _run("""
        import sys, warnings
        warnings.simplefilter("ignore")
        import brainmaze_torch.seizure_detection._models, brainmaze_torch.seizure_detection._seizure_detect
        print("torch" in sys.modules)
    """)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == "False"


def test_dependencies_are_the_successor_only():
    reqs = [r for r in (md.requires("brainmaze-torch") or []) if "extra ==" not in r]
    assert [r.replace(" ", "") for r in reqs] == ["brainmaze-eeg-models>=0.1.0"]
    assert not any(r.lower().startswith("torch") for r in md.requires("brainmaze-torch") or [])


def test_no_pytorch_weights_in_the_package():
    pkg = Path(brainmaze_torch.__file__).resolve().parent
    assert not list(pkg.rglob("*.pt"))
