# Releasing `brainmaze-torch`

This package follows the BrainMaze family release process. The full guide (one-time setup,
dependency order, compatibility policy, troubleshooting) is in
**[bnelair/brainmaze RELEASING.md](https://github.com/bnelair/brainmaze/blob/main/RELEASING.md)**.

## Quick steps

1. Make sure `main` has what you want to release and CI is green.
2. **Actions → Prepare release → Run workflow**, pick `patch` / `minor` / `major`
   (changed numerical results count as breaking).
3. Review and squash-merge the bot's **"Release vX.Y.Z"** PR (it only changes the
   `version =` line in `pyproject.toml`).
4. **Actions → Release** then tests, builds, publishes to
   [PyPI](https://pypi.org/project/brainmaze-torch/) with Trusted Publishing, pushes tag `vX.Y.Z`
   and creates the GitHub Release.

Never edit `version =` in a normal PR; the **Version guard** check rejects it.

## This repository

| | |
|---|---|
| PyPI | [`brainmaze-torch`](https://pypi.org/project/brainmaze-torch/) |
| import | `import brainmaze_torch` (`brainmaze_torch.__version__` comes from installed metadata) |
| workflows | `ci.yml` (tests), `docs.yml` (GitHub Pages), `prepare-release.yml`, `release.yml`, `version-guard.yml`, all thin callers of [brainmaze-sphinx](https://github.com/bnelair/brainmaze-sphinx) |
| PyPI Trusted Publisher | owner `bnelair`, repo `brainmaze-torch`, workflow `release.yml`, no environment |

## One-time setup still needed for this repository

`brainmaze-torch` is already on PyPI (0.0.1, 0.1.0 and 0.1.1). Releases before #8 were uploaded by the old
`test_publish.yml` workflow with `twine` and the API token `PYPI_Token_General`. The repository itself has no
Actions secrets, so that token is most likely an organisation-level secret. The current `release.yml` uses
**Trusted Publishing** instead, like brainmaze-eeg and brainmaze-utils, and does not read that token.
Before the first release with this flow, a PyPI owner of `brainmaze-torch` must add the publisher once:

1. <https://pypi.org/manage/project/brainmaze-torch/settings/publishing/> → **Add a new publisher → GitHub**.
2. Owner `bnelair`, repository `brainmaze-torch`, workflow `release.yml`, environment: leave **empty**.

Without it the **Publish to PyPI** step fails with an `invalid-publisher` error. Nothing is tagged or released in
that case, so the release can be retried by re-running the failed jobs of that Release run.
After the first successful Trusted Publishing release, this repository no longer needs `PYPI_Token_General`;
the organisation secret can be removed once no other repository uses it.

Also needed once: **Settings → Actions → General → "Allow GitHub Actions to create and approve pull requests"**
(organisation and repository level), otherwise *Prepare release* cannot open the bump PR.
