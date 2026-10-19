# Releasing `brainmaze-torch`

This package follows the BrainMaze family release process. The full guide (how a release
works, recovering from a failed release, one-time setup, branch protection, dependency order,
compatibility policy, troubleshooting) is in
**[bnelair/brainmaze-sphinx RELEASING.md](https://github.com/bnelair/brainmaze-sphinx/blob/main/RELEASING.md)**.

## 0.3.0 is the FINAL release

brainmaze-torch is retired; its successor is
[brainmaze-eeg-models](https://github.com/bnelair/brainmaze-eeg-models) (ONNX Runtime, no PyTorch).
0.3.0 is a compatibility shim: it depends only on `brainmaze-eeg-models>=0.1.0`, re-exports its
seizure functions under the 0.2.0 names, emits one `FutureWarning` on import (shown by default to every user) and raises
`ImportError` with advice for the PyTorch-only names (`models_generic`, `SeizureDetectModel`). No
`torch`, no `.pt` models: the wheel and sdist are Python code only (`dist-check: error`, no
`required-assets` / `allowed-assets` in `ci.yml` and `release.yml`).

To release it: **Prepare release → `minor`** (0.2.0 → 0.3.0), check that the bot's PR changes only the
version line, merge it, and watch *Actions → Release* (publishes with the org token
`PYPI_Token_General`, then tags `v0.3.0` and creates the GitHub Release). Afterwards, **in this order**
(once the repository is archived it is read-only and no workflow can run any more):

1. **Check the release** on PyPI and in a fresh venv: `pip install brainmaze-torch==0.3.0` installs no
   `torch`, and `python -c "from brainmaze_torch.seizure_detection import predict_channel_seizure_probability"`
   prints the `FutureWarning`.
2. **Check that the docs carry the superseded notice.** The merge of the release PR (and of this PR)
   triggers *Actions → Docs* on `main`:

   ```bash
   gh run list --repo bnelair/brainmaze-torch --workflow docs.yml --branch main --limit 3   # latest: success
   curl -s https://bnelair.github.io/brainmaze-torch/ | grep -c "superseded by"               # must be > 0
   ```

   If the run failed, re-run it (`gh run rerun <run-id> --repo bnelair/brainmaze-torch`) before going on.
3. **Replace the stale `models_generic` page on `gh-pages`.** The shared docs workflow deploys with
   `keep_files: true`, so pages that are no longer built (here `models_generic.html`, which documents the
   removed PyTorch classes without any notice) stay online forever. Replace it with a stub that carries the
   notice and redirects to the landing page, and drop its sources:

   ```bash
   git clone --branch gh-pages --single-branch https://github.com/bnelair/brainmaze-torch.git bt-pages
   cd bt-pages
   git rm -q --ignore-unmatch .doctrees/models_generic.doctree _sources/models_generic.rst _sources/models_generic.rst.txt
   cat > models_generic.html <<'HTML'
   <!doctype html>
   <html lang="en"><head><meta charset="utf-8">
   <meta http-equiv="refresh" content="5; url=index.html">
   <title>Removed: brainmaze_torch.models_generic</title></head>
   <body>
   <p><strong>brainmaze-torch is superseded by
   <a href="https://github.com/bnelair/brainmaze-eeg-models">brainmaze-eeg-models</a>.</strong>
   <code>brainmaze_torch.models_generic</code> (PyTorch building blocks) was removed in 0.3.0, the final release.
   See the <a href="https://bnelair.github.io/brainmaze-eeg-models/seizure.html#moving-from-brainmaze-torch">migration notes</a>.
   Redirecting to the <a href="index.html">brainmaze-torch documentation</a>...</p>
   </body></html>
   HTML
   git add models_generic.html
   git commit -m "Replace the removed models_generic page with a superseded notice"
   git push origin gh-pages
   cd .. && rm -rf bt-pages
   curl -s https://bnelair.github.io/brainmaze-torch/models_generic.html | grep -c "superseded by"   # > 0 after Pages redeploys
   ```

4. **Update the repository "About" text**, which still says "written in PyTorch":

   ```bash
   gh repo edit bnelair/brainmaze-torch --description "DEPRECATED, superseded by brainmaze-eeg-models (https://github.com/bnelair/brainmaze-eeg-models). Final release 0.3.0 is a compatibility shim; archived."
   ```

5. **Archive the GitHub repository** (Settings → General → Danger Zone → Archive, or
   `gh repo archive bnelair/brainmaze-torch --yes`), as agreed with the maintainer. There are no further
   releases: do not run Prepare release again. 0.2.0 (the last PyTorch version) stays on PyPI; do not
   yank it.

## Quick steps

1. Make sure `main` has what you want to release and CI is green.
2. **Actions → Prepare release → Run workflow**, pick `patch` / `minor` / `major`
   (changed numerical results and API changes count as breaking; while the version is 0.x a
   breaking change bumps `minor`). **The next (and final) release is `0.3.0` (pick
   `minor`)**: see "0.3.0 is the FINAL release" above.
3. Review the bot's **"Release vX.Y.Z"** PR and check that its diff is exactly the one
   `version = "X.Y.Z"` line in `pyproject.toml`. CI and the Version guard don't run on it
   (PRs opened with `GITHUB_TOKEN` trigger no workflows), so this check is yours. Then
   squash-merge it.
4. The merge triggers the **Release** workflow automatically (it has no manual trigger). It
   tests, builds, publishes to [PyPI](https://pypi.org/project/brainmaze-torch/) with the
   organisation API token `PYPI_Token_General`, pushes tag `vX.Y.Z` and creates the GitHub
   Release. Watch it under *Actions → Release*. Only one Release run executes at a time
   (concurrency group `release-caller-bnelair/brainmaze-torch`).

Never edit `[project].version` in a normal PR. The **Version guard** check flags it (it parses
`[project].version` from `pyproject.toml` on both sides, and for the bot's bump PR checks that
nothing else changed). The check is **advisory**: no ruleset requires it (maintainer decision;
making it required would block the bot's bump PRs, on which no workflow runs), so reviewers must
not merge a PR it flags.

## Recovering from a failed release

If the Release run fails part-way, **don't wait for the next push to `main`** (that would
publish and tag a different commit) and **don't run Prepare release again** (that would skip
the version). Go by the step that failed (full table:
[Recovering from a failed release](https://github.com/bnelair/brainmaze-sphinx/blob/main/RELEASING.md#recovering-from-a-failed-release)):

| failed step | state | what to do |
|---|---|---|
| guard / test / build, or the token check / upload | nothing published or tagged | Fix the cause (e.g. the token secret), then **Re-run failed jobs** on that same run (possible for 30 days; the `dist` artifact is kept 90 days). |
| tag push, after a successful upload | PyPI has X.Y.Z, no tag | Do **not** re-run: PyPI files are immutable, so the upload step would fail. Tag the commit that run built (the run's head SHA) by hand: `git tag vX.Y.Z <sha> && git push origin vX.Y.Z`, then `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --generate-notes`. |
| upload half-succeeded (some files on PyPI, e.g. wheel but not sdist) | PyPI has some files of X.Y.Z, no tag | **Re-run failed jobs** fails (PyPI rejects the files already there) and the workflow deliberately has no `skip-existing`. Download the `dist` artifact of the failed run (`gh run download <run-id> -n dist -D dist`; it is the exact build) and upload only the missing files: `twine upload dist/<missing-file>` (token `PYPI_Token_General`, user `__token__`). Check on PyPI that all files are present, then tag the run's head SHA by hand and create the release as in the tag-push row. |
| `gh release create`, after the tag push | PyPI + tag, no GitHub Release | `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --generate-notes`. |

## Breaking changes since 0.1.1 (released as 0.2.0)

`predict_channel_seizure_probability`:

- **NaN for unevaluated time.** `t = 0` and every 1 s segment that contains a NaN/inf sample or a
  flat signal are NaN (0.1.1 returned numbers there, and 0 where nothing was evaluated). Downstream
  code must use NaN-aware functions (`np.nanmax`, `np.isfinite`) and must not `fillna(0)`.
- **Output length** is `len(x) // (fs // 2)`: one point shorter than 0.1.1's `ceil(t_max * 2)`
  whenever the recording is not a whole number of half-seconds (the dropped point lay beyond the
  data and was always 0).
- **Full coverage**: the first/last `discard_edges_s` and the tail after the last regular window
  now get values (0.1.1: 0). Everywhere 0.1.1 produced an estimate, the values are unchanged
  (golden-value tests against 0.1.1, `tests/test_golden.py`).
- **Stricter inputs (raise `ValueError` instead of silently misbehaving):** `fs` must be a whole,
  even number >= 200 Hz (`500.0` is accepted); `discard_edges_s == window_s` raises instead of
  being auto-corrected; `step_s > window_s - 2 * discard_edges_s - 0.5` raises; the recording
  must be at least `window_s` long.
- **New keyword arguments** `min_valid_fraction` (default 0.0 = 0.1.1 behaviour) and
  `fill_recording_edges` (default True).

Packaging (0.2.0): the runtime dependencies were reduced to `numpy>=1.24`, `scipy>=1.10` and `torch>=2.3`
(torch < 2.3 cannot use numpy 2). 0.1.1 also pulled in `brainmaze_utils`, `torchvision`,
`torchaudio`, `pandas`, `scikit-learn`, `matplotlib`, `sphinx` and others; code that relied on
them arriving transitively must now depend on them itself. The private module
`brainmaze_torch._config` was removed.

## This repository

| | |
|---|---|
| PyPI | [`brainmaze-torch`](https://pypi.org/project/brainmaze-torch/) |
| import | `import brainmaze_torch` (`brainmaze_torch.__version__` comes from installed metadata) |
| thin callers of [brainmaze-sphinx](https://github.com/bnelair/brainmaze-sphinx) | `ci.yml` (tests), `docs.yml` (GitHub Pages), `prepare-release.yml` |
| with local logic | `release.yml`: calls the shared guard + test + build, then its own `publish` job checks the token, uploads to PyPI, pushes the tag and creates the GitHub Release. `version-guard.yml`: entirely local. |
| PyPI upload | org-level Actions secret `PYPI_Token_General` (API token), used only by the publish job in `release.yml` |

## Publishing credentials

`brainmaze-torch` is already on PyPI (0.0.1 to 0.2.0; 0.2.0 was published by the Release workflow), uploaded with the API token `PYPI_Token_General`.
By maintainer decision, `release.yml` keeps using that token (brainmaze-eeg and brainmaze-utils use Trusted Publishing).
The repository itself has no Actions secrets, so the token is an organisation-level secret that must be shared
with this repository. The publish job first checks that the secret is non-empty and fails with a clear error
otherwise; nothing is published or tagged in that case.

If the upload fails, nothing is tagged: see "Recovering from a failed release" above.

**Optional switch to Trusted Publishing:** add a GitHub publisher on
<https://pypi.org/manage/project/brainmaze-torch/settings/publishing/> (owner `bnelair`, repository
`brainmaze-torch`, workflow `release.yml`, environment empty), then in `release.yml` remove the `password:`
input and the token check and give the publish job `id-token: write`.

*Prepare release* needs **Settings → Actions → General → "Allow GitHub Actions to create and approve pull
requests"** (organisation and repository level); it is enabled for this repository as of 2026-10-01.
