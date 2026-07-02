# 4-Phase Production Upgrade — Docker-DevOps-Tooling

## Context

The repo is a solid hardened Docker toolkit (multi-stage non-root images, Trivy-gated CI, 23 CLI tests) but is missing production pillars: no healthchecks/resource-limits/networks in compose, `latest` tags, unpinned CI actions, no registry publish, no release automation, no mypy/coverage, no dependabot, no hygiene docs. User wants a phased upgrade, **each phase = one large commit pushed directly to `main`** (user's explicit choice), so git history shows the progression. Each commit must leave CI green and be self-contained.

Verified facts:
- Remote: `https://github.com/www8351/Docker-DevOps-Tooling.git` → GHCR images: `ghcr.io/www8351/docker-devops-tooling/<name>`. README CI badge points at wrong repo (`www8351/Bash`) — fix in phase 4.
- `cli/dockerctl/containers.py:112` — `exec_` uses `Annotated[...] = ...` (ellipsis default), fails strict mypy; fix in phase 3.
- Per repo `CLAUDE.md` protocol: every phase commit also updates `STATUS.md`/`PROGRESS.md` (+ `DECISIONS.md` when choices made). NOTE: these files are currently git-ignored — lifecycle updates happen locally, do NOT un-ignore them.
- Windows dev box; Docker daemon may not run locally. Local verification = `docker compose config`, pytest, ruff, mypy. Runtime/publish verification = GitHub Actions after push (`gh run watch`). Publish failures → fix-forward commits.

---

## Phase 1 — Compose hardening (commit 1)

**Files:** `compose/docker-compose.yml` (rewrite), `compose/.env.example`

`docker-compose.yml`:
- `x-logging: &default-logging` anchor: json-file, `max-size: "10m"`, `max-file: "3"`; apply to all services.
- Two networks: `web` (nginx, httpd, counter), `mgmt` (portainer, dockerctl — socket consumers isolated from web tier).
- Pin tags in compose fallbacks too: `nginx:${NGINX_TAG:-1.27-alpine}`, `httpd:${HTTPD_TAG:-2.4-alpine}`, `portainer/portainer-ce:${PORTAINER_TAG:-2.27.4}` (verify newest 2.27.x patch at implementation).
- Per-service hardening:

| Service | healthcheck | read_only/tmpfs | caps | extra |
|---|---|---|---|---|
| nginx | `wget -q --spider http://127.0.0.1/`, 30s/5s/3 retries/10s start_period (busybox wget — needs alpine variant) | `read_only: true`, tmpfs `/var/cache/nginx,/var/run,/tmp` | drop ALL, add CHOWN,SETGID,SETUID,NET_BIND_SERVICE | `no-new-privileges:true` |
| httpd | same wget probe | `read_only: true`, tmpfs `/usr/local/apache2/logs,/tmp` | same as nginx | same |
| portainer | **none** — scratch image, no shell/wget; comment why | skip read_only (writes /data) | drop ALL | socket stays rw (needed to manage engine; comment why) |
| counter | `CMD-SHELL pgrep -f counter.sh` | `read_only: true` | drop ALL | `init: true` (sleep loop ignores SIGTERM otherwise) |
| dockerctl | none (one-shot tool) | `read_only: true`, tmpfs `/tmp` | drop ALL | `no-new-privileges:true` |

- Resource limits via `deploy.resources.limits`: nginx/httpd 0.50cpu/128M, portainer 0.50/256M, counter 0.10/32M, dockerctl 0.50/128M.

`.env.example`: `NGINX_TAG=1.27-alpine`, `HTTPD_TAG=2.4-alpine`, `PORTAINER_TAG=2.27.4`; comment that alpine variants are load-bearing (busybox wget healthchecks).

**Verify:** `docker compose -f compose/docker-compose.yml config --quiet` + full render eyeball. Commit → push → CI green.

---

## Phase 2 — CI/CD + supply chain (commit 2)

**Files:** `.github/workflows/ci.yml` (restructure), `.github/dependabot.yml` (new)

`ci.yml`:
- Workflow-level: `permissions: contents: read`; `concurrency: group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true`.
- Pin ALL actions to full commit SHAs with `# vX.Y.Z` comments (checkout, setup-python, hadolint-action, action-shellcheck, trivy-action, plus new docker/setup-buildx-action, docker/login-action, docker/metadata-action, docker/build-push-action, actions/upload-artifact, all latest — look up SHAs at implementation).
- `lint` job: steps unchanged, actions pinned.
- `image` job (same matrix): setup-buildx → build-push-action with `load: true`, `tags: <name>:ci`, `cache-from/to: type=gha, scope=<name>, mode=max` → Trivy scan (existing gating) → Trivy SBOM step (`format: cyclonedx`, `output: <name>-sbom.cdx.json`, `exit-code: "0"`) → upload-artifact `sbom-<name>` retention 30d.
- New `publish` job: `needs: [lint, image]`, `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`, job perms `contents: read, packages: write`, same matrix. Steps: checkout → buildx → ghcr login (`github.actor` / `secrets.GITHUB_TOKEN`) → metadata-action `images: ghcr.io/www8351/docker-devops-tooling/<name>`, tags `type=raw,value=latest,enable={{is_default_branch}}` + `type=sha` → build-push `push: true`, cache-from gha scope.

`dependabot.yml`: weekly — github-actions `/`, pip `/cli`, docker `/images/counter`, docker `/cli`.

**Manual follow-up:** first GHCR push creates private packages — flip both to public in GitHub package settings.

**Verify:** push → `gh run watch` → 3 jobs green, packages appear on GHCR, SBOM artifacts downloadable, second run shows `CACHED` layers.

---

## Phase 3 — CLI quality (commit 3)

**Files:** `cli/pyproject.toml`, `cli/dockerctl/__init__.py`, `cli/dockerctl/__main__.py`, `cli/dockerctl/containers.py`, `cli/dockerctl/images.py`, `cli/tests/*`, `.github/workflows/ci.yml` (mypy step), `.pre-commit-config.yaml` (mypy hook), `Taskfile.yml` (typecheck task)

- `pyproject.toml`: `test` extra += `pytest-cov>=6`; new `dev` extra (`dockerctl[test]`, `mypy>=1.14`, `ruff>=0.8`); `[tool.mypy]` `strict = true`, `python_version = "3.10"`, `warn_unreachable`, `pretty`; override `tests.*` `disallow_untyped_defs = false`; pytest `addopts = "--cov=dockerctl --cov-report=term-missing --cov-fail-under=90"` (rides into existing CI pytest step and `task test` automatically).
- `__init__.py`: single-source version via `importlib.metadata.version("dockerctl")`, fallback `"0.0.0+unknown"` on PackageNotFoundError. pyproject stays sole version source.
- `__main__.py`: root `@app.callback()` with eager `--version/-V` flag; keep `version` subcommand for back-compat; test no-args still prints help.
- `containers.py`: fix `exec_` ellipsis default (line 112) → required annotated argument, no default. New commands: `restart` (`--time/-t`), `stats` (always `--no-stream`; `--json` → `--format {{json .}}`, capture+echo). Follow existing try/DockerError/typer.Exit(1) pattern.
- `images.py`: new `tag <source> <target>`, `push <name>`.
- Tests: existing monkeypatch-`run` + CliRunner pattern; arg-construction + error-path test per new command; `--version`/`-V` tests.
- CI lint job: fold install to `pip install -e 'cli[dev]'`, add `mypy --config-file cli/pyproject.toml cli/dockerctl cli/tests` after ruff.
- pre-commit: `mirrors-mypy` hook, `files: ^cli/.*\.py$`, `additional_dependencies: [typer, pytest]`.
- Taskfile: `typecheck` task (dir cli, `mypy dockerctl tests`), wire into `lint`.

**Risk:** typer decorators under strict mypy — targeted `# type: ignore[...]` last resort. Fully verifiable locally.

**Verify (local, pre-push):** `cd cli && pip install -e .[dev] && ruff check . && ruff format --check . && mypy dockerctl tests && pytest` (coverage ≥90); `dockerctl --version`, `-V`, `version` all print 0.1.0.

---

## Phase 4 — Release + repo hygiene (commit 4 + tag)

**Files:** `.github/workflows/release.yml` (new), `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md` (new), `README.md` (major update), `cli/pyproject.toml` (version → 0.2.0)

- `release.yml`: trigger `push: tags: ["v*"]`; top `permissions: contents: read`; matrix build job (perms `packages: write`): checkout → tag/version guard (`grep -q "^version = \"${GITHUB_REF_NAME#v}\"" cli/pyproject.toml`, POSIX sh) → buildx → ghcr login → metadata-action semver tags (`{{version}}`, `{{major}}.{{minor}}`, `latest`) → build-push. Final `github-release` job `needs: build`, perms `contents: write`, `softprops/action-gh-release` (SHA-pinned) with `generate_release_notes: true`.
- `CHANGELOG.md`: Keep a Changelog. `[Unreleased]`, `[0.2.0]` (the 4 phases), `[0.1.0]` backfilled from git history (`0b2295c`→`99e8b6f` modernization, `b6216a2` tests, `197d3a4` hardening). Compare links at bottom.
- `CONTRIBUTING.md`: setup (`pip install -e 'cli[dev]'`, `pre-commit install`), gates (`task lint/typecheck/test`), conventions (POSIX sh, hadolint-clean, ruff 100, non-interactive, env-driven ports).
- `SECURITY.md`: supported versions, GitHub Security Advisories reporting, posture (Trivy, non-root, read-only, pinned actions), docker.sock mount = root-equivalent by design note.
- `README.md`: **fix CI badge repo** (`Bash` → `Docker-DevOps-Tooling`), add release/GHCR badges, GHCR pull snippet, updated stack table (healthchecks/networks/limits/pins), CLI section (new commands, `--version`), CI section (3 jobs + release + dependabot + SBOM), link new docs in TOC.
- Bump `cli/pyproject.toml` version 0.1.0 → 0.2.0 (`__version__` follows via phase-3 mechanism).

**Sequence:** commit → push → CI green → `git tag v0.2.0 && git push origin v0.2.0` → release workflow.

**Verify:** local pytest/mypy/ruff green after bump; post-tag: Release created, GHCR `:0.2.0`/`:0.2`/`:latest` present, badges render.

---

## Cross-phase

- Order matters: phase 2 publish plumbing (login/metadata/cache) proven on main before phase 4 tags depend on it; phase 3 single-source version before phase 4 bump.
- Each commit: normal-style conventional commit message, plus local lifecycle-file updates (STATUS/PROGRESS/DECISIONS — git-ignored, not in commits).
- Look up live at implementation: newest portainer 2.27.x tag, action SHAs, mirrors-mypy rev, trivy-action version.
- Brainstorming protocol: also save spec copy to `docs/superpowers/specs/2026-07-02-production-upgrade-design.md` in phase-1 commit (or skip if user prefers — plan default: include).
