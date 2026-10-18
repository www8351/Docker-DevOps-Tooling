# Contributing

Thanks for considering a contribution. This repo is deliberately small and
strict — the gates below keep it that way.

## Setup

```bash
# 1. Task runner (optional but recommended): https://taskfile.dev/installation/
# 2. Python dev environment
pip install -e 'cli[dev]'        # dockerctl + pytest/pytest-cov + mypy + ruff

# 3. Local git hooks
pip install pre-commit
pre-commit install
```

## Quality gates

Everything that CI runs is available locally:

| Command | What it checks |
|---------|----------------|
| `task lint` | compose config, hadolint (both Dockerfiles), shellcheck, ruff, mypy |
| `task typecheck` | mypy strict mode on `cli/dockerctl` and `cli/tests` |
| `task test` | pytest with a 90% coverage gate (`--cov-fail-under=90`) |
| `task fmt` | ruff auto-format + autofix |

A change is mergeable when all three of `task lint`, `task test`, and
`pre-commit run --all-files` pass.

## Conventions

- **Non-interactive everything** — flags and env vars only; no prompts.
  Commands must return meaningful exit codes and write errors to stderr.
- **POSIX `sh` only** for shell scripts (busybox-ash compatible, shellcheck-clean).
- **Dockerfiles** are multi-stage, minimal, non-root (UID/GID 10001), and
  hadolint-clean.
- **Python** is ruff-clean (line length 100) and mypy-strict-clean; the CLI
  version lives only in `cli/pyproject.toml`.
- **Bind addresses and ports** come from `compose/.env` (copy `.env.example`).
  **Images** are pinned as `tag@sha256:digest` directly in
  `compose/docker-compose.yml` so Dependabot can bump them. Keep alpine-based
  images where a healthcheck uses busybox `wget`.
- **Secrets** live only in `compose/secrets/` (gitignored, created by
  `scripts/gen-secrets.sh`). Never add a default password to compose or
  `.env.example`.
- **GitHub Actions** are pinned to full commit SHAs with a version comment.

## Releases

1. Add your changes under `[Unreleased]` in `CHANGELOG.md` as you go.
2. To release: move the notes to a new version section, bump `version` in
   `cli/pyproject.toml` (they must match), commit, then tag `vX.Y.Z` and push
   the tag. The release workflow builds semver-tagged images and creates the
   GitHub Release.
