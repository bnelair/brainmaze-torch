# Releasing `brainmaze-torch`

This package follows the BrainMaze family release process. The full guide (how a release
works, recovering from a failed release, one-time setup, branch protection, dependency order,
compatibility policy, troubleshooting) is in
**[bnelair/brainmaze-sphinx RELEASING.md](https://github.com/bnelair/brainmaze-sphinx/blob/main/RELEASING.md)**.

## Quick steps

1. Make sure `main` has what you want to release and CI is green.
2. **Actions → Prepare release → Run workflow**, pick `patch` / `minor` / `major`
   (changed numerical results and API changes count as breaking; while the version is 0.x a
   breaking change bumps `minor`). **The next release must be at least `0.2.0` (pick
   `minor`)**: see "Breaking changes since 0.1.1" below.
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
| `gh release create`, after the tag push | PyPI + tag, no GitHub Release | `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --generate-notes`. |

## Breaking changes since 0.1.1 (release as ≥ 0.2.0)

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

Packaging: the runtime dependencies are now only `numpy>=1.24`, `scipy>=1.10` and `torch>=2.3`
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

`brainmaze-torch` is already on PyPI (0.0.1, 0.1.0 and 0.1.1), uploaded with the API token `PYPI_Token_General`.
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
