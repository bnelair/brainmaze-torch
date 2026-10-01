# Releasing `brainmaze-torch`

This package follows the BrainMaze family release process. The full guide (one-time setup,
dependency order, compatibility policy, troubleshooting) is in
**[bnelair/brainmaze-sphinx RELEASING.md](https://github.com/bnelair/brainmaze-sphinx/blob/main/RELEASING.md)**.

## Quick steps

1. Make sure `main` has what you want to release and CI is green.
2. **Actions → Prepare release → Run workflow**, pick `patch` / `minor` / `major`
   (changed numerical results count as breaking).
3. Review and squash-merge the bot's **"Release vX.Y.Z"** PR (it only changes the
   `version =` line in `pyproject.toml`).
4. **Actions → Release** then tests, builds, publishes to
   [PyPI](https://pypi.org/project/brainmaze-torch/) with the org API token `PYPI_Token_General`, pushes tag `vX.Y.Z`
   and creates the GitHub Release.

Never edit `version =` in a normal PR; the **Version guard** check rejects it.

## This repository

| | |
|---|---|
| PyPI | [`brainmaze-torch`](https://pypi.org/project/brainmaze-torch/) |
| import | `import brainmaze_torch` (`brainmaze_torch.__version__` comes from installed metadata) |
| workflows | `ci.yml` (tests), `docs.yml` (GitHub Pages), `prepare-release.yml`, `release.yml`, `version-guard.yml`, all thin callers of [brainmaze-sphinx](https://github.com/bnelair/brainmaze-sphinx) |
| PyPI upload | org-level Actions secret `PYPI_Token_General` (API token), used only by the publish job in `release.yml` |

## Publishing credentials

`brainmaze-torch` is already on PyPI (0.0.1, 0.1.0 and 0.1.1), uploaded with the API token `PYPI_Token_General`.
By maintainer decision, `release.yml` keeps using that token (brainmaze-eeg and brainmaze-utils use Trusted Publishing).
The repository itself has no Actions secrets, so the token is an organisation-level secret that must be shared
with this repository. The publish job first checks that the secret is non-empty and fails with a clear error
otherwise; nothing is published or tagged in that case.

If an upload fails (missing or expired token, PyPI outage), nothing is tagged. Fix the cause and **re-run the
failed jobs of that same Release run**. Don't wait for a later push to main: that run would release whatever
commit is then at the head of main.

**Optional switch to Trusted Publishing:** add a GitHub publisher on
<https://pypi.org/manage/project/brainmaze-torch/settings/publishing/> (owner `bnelair`, repository
`brainmaze-torch`, workflow `release.yml`, environment empty), then in `release.yml` remove the `password:`
input and the token check and give the publish job `id-token: write`.

*Prepare release* needs **Settings → Actions → General → "Allow GitHub Actions to create and approve pull
requests"** (organisation and repository level); it is enabled for this repository as of 2026-10-01.
