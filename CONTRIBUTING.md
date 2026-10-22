# Contributing

Thanks for considering a contribution. This repo is deliberately small and
strict, and the gates below keep it that way.

## Setup

```bash
# 1. Task runner (optional but recommended): https://taskfile.dev/installation/
# 2. uv: https://docs.astral.sh/uv/  (manages the locked Python environment)
cd cli && uv sync --locked --extra dev && cd ..   # dockerctl + pytest/pytest-cov + mypy + ruff

# 3. Local git hooks (ruff and mypy run from cli/uv.lock)
uv tool install pre-commit
pre-commit install
```

`pip install -e 'cli[dev]'` still works, but resolves unpinned versions; CI
and the hooks always use the lockfile. After changing dependencies in
`cli/pyproject.toml`, run `task lock` and commit `cli/uv.lock`.

## Quality gates

Everything that CI runs is available locally:

| Command | What it checks |
|---------|----------------|
| `task lint` | compose config, then every pre-commit hook: ruff, mypy, hadolint (both Dockerfiles), shellcheck, actionlint, zizmor |
| `task typecheck` | mypy strict mode on `cli/dockerctl` and `cli/tests` |
| `task test` | pytest with a 90% coverage gate (`--cov-fail-under=90`) |
| `task fmt` | ruff auto-format + autofix |
| `task scan` / `task sbom` | Trivy scan / CycloneDX SBOMs of both images (pinned Trivy image) |
| `task chart:lint` | `helm lint --strict` on `deploy/chart` against its values schema |
| `task kind:test` | the CI `helm` job on a local kind cluster (needs helm, kind, kubectl) |

A change is mergeable when `task lint` and `task test` pass, plus
`task chart:lint` when it touches the chart. CI also runs the test suite on
every supported Python (3.11 to 3.14) and installs the chart on kind.

## Conventions

- **Non-interactive everything**: flags and env vars only, no prompts.
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
- **The Helm chart** keeps every pod admissible under the restricted Pod
  Security Standard. nginx and httpd in `deploy/chart/values.yaml` use the
  same tag and digest as compose, and `deploy/chart/files/httpd.conf` is an
  exact copy of `compose/httpd/httpd.conf`; CI fails if either drifts, so a
  compose image bump must update the chart values in the same PR. Bump
  `version` in `deploy/chart/Chart.yaml` whenever the chart changes.
- **GitHub Actions** are pinned to full commit SHAs with a version comment.
- **Decisions**: a change that makes or reverses a significant trade-off adds
  a record under [`docs/adr/`](docs/adr/README.md), starting from its
  template.

## Releases

1. Add your changes under `[Unreleased]` in `CHANGELOG.md` as you go.
2. To release `X.Y.Z`: move the notes to a `## [X.Y.Z] - YYYY-MM-DD`
   section and add its compare link, set `version` in `cli/pyproject.toml`
   and run `task lock`, set `appVersion` in `deploy/chart/Chart.yaml`, then
   commit, tag `vX.Y.Z` and push the tag.
3. The release workflow refuses a tag that does not match
   `cli/pyproject.toml` and the chart's `appVersion`, or a stable tag without
   its changelog section. It then runs the full CI suite on the tagged
   commit, publishes semver-tagged, signed images and creates the GitHub
   Release. A tag with a prerelease part (`v0.4.0-rc.1`) never moves
   `latest`.
