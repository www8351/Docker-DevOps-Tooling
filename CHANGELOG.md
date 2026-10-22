# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-10-18

Hardening, supply chain, CLI correctness, a Helm chart and documentation,
shipped in five reviewed phases. Several changes are breaking; see Changed.

### Security

- **The CLI ends option parsing before every positional argument** (`--`), so
  a container, image or service name starting with a dash can never be read
  by docker as a flag.
- **No default admin passwords.** Portainer (`--admin-password-file`) and
  Grafana (`GF_SECURITY_ADMIN_PASSWORD__FILE`) read generated compose secrets
  from `compose/secrets/` (`scripts/gen-secrets.sh`, `task secrets`). Portainer's
  open first-run setup page and Grafana's `admin/admin` fallback are gone.
- **Loopback by default.** Published ports bind to `WEB_BIND_ADDR` /
  `ADMIN_BIND_ADDR`, both `127.0.0.1` unless overridden.
- **cAdvisor holds no engine socket.** It mounted `/var/run` (docker.sock and
  the containerd socket), the host rootfs and `/var/lib/docker`, and kept every
  capability. It now mounts only `/sys` read-only and drops all capabilities.
- **Network split.** `nginx-exporter` no longer bridges the public `web` tier to
  the docker.sock tier: networks are now `web`, internal `nginx-status`,
  `metrics` and `mgmt`; counter and dockerctl run without a network.
- nginx runs unprivileged (UID 101, no capabilities); Portainer gains a
  read-only root filesystem.
- **Publishing scans what it ships.** A shared `_publish.yml` pushes by digest,
  scans that digest on both platforms with Trivy, signs it, and only then
  moves tags (verifying each resolves to the signed digest). Before, tags
  moved at push time and the arm64 image was never scanned.
- **Releases are gated.** `release.yml` checks the tag against the package
  version, the chart `appVersion` and the changelog, runs the full CI suite
  on the tagged commit, and no longer tags prereleases `latest`.
- **Locked dependencies.** `cli/uv.lock` pins every Python dependency with
  hashes; CI, the image and the hooks install from it.
- Workflows: actionlint and zizmor in CI, CodeQL for Python and Actions,
  Trivy SARIF to code scanning, job timeouts, no persisted checkout tokens,
  and a 7 day Dependabot cooldown. Jobs run on `ubuntu-24.04`, uv is pinned
  to the version `cli/Dockerfile` uses (CI fails if they differ), and the
  kind namespace enforces a fixed Pod Security Standard version.

### Added

- **Observability compose profile**: Prometheus (read-only scrape config),
  Grafana (provisioned datasource + committed container dashboard), cAdvisor,
  and nginx-prometheus-exporter (via a non-host-mapped `stub_status`
  endpoint). CI boots the profile and fails if any Prometheus target is down.
- Taskfile `secrets` and `obs:up`; `up` now waits for health, and `down` /
  `clean` also stop the observability profile and remove its volumes.
- Dependabot now watches the compose image pins (`docker-compose`
  ecosystem).
- CI asserts loopback binding, fail-closed startup without secrets, working
  admin secrets, and per-container cAdvisor metrics;
  `scripts/wait-prom-targets.sh` replaces a fixed sleep.
- CI `test` matrix (Python 3.12, 3.13, 3.14), `workflow-lint` job, and a
  `publish-dry-run` job that runs the full publish against a local registry
  on every pull request.
- Taskfile `lock`, `scan` and `sbom`; pre-commit gains actionlint and zizmor.
- **`dockerctl compose up/down/ps`** (#14): stack lifecycle from the CLI. `up`
  waits for every healthcheck by default; `--file` / `DOCKERCTL_COMPOSE_FILE`
  pick the compose file and `--profile` is repeatable.
- `containers deploy` escape hatches: `--cap-add`, `--tmpfs`, `--writable`,
  `--user`, `--memory`, `--pids-limit`, `--no-harden`. `--no-harden` refuses
  the hardening options with a usage error instead of ignoring them.
- CI drives `inspect`, `logs` and `compose ps` against the live stack.
- **Helm chart** `deploy/chart` (#12) for nginx, httpd and counter: non-root
  with fixed UIDs, seccomp `RuntimeDefault`, read-only root filesystems, no
  capabilities, no service account token, default-deny NetworkPolicies and a
  `helm test` pod, admitted under the restricted Pod Security Standard.
  Taskfile `chart:lint`, `chart:template` and `kind:test`.
- CI `helm` job: installs the chart on kind in a namespace enforcing the
  restricted profile and runs `helm test`; it also fails when the chart's
  images or `httpd.conf` drift from compose.
- **Architecture decision records** in `docs/adr` (#15), backfilled for the
  project's main trade-offs, with a template for new ones.
- **Demo GIF** (#17) rendered from a rewritten `docs/assets/demo.tape` and
  embedded in the README.
- A full Hebrew section in the README, mirroring the English one.

### Changed

- **Breaking:** the `*_TAG` variables are gone. Every image is pinned by tag
  and digest directly in `compose/docker-compose.yml`; use an override file to
  run a different image.
- **Breaking:** `scripts/gen-secrets.sh` must run before `up`, and services are
  reachable only on `127.0.0.1` until the bind addresses are changed.
- **Breaking:** the Grafana dashboard labels containers by short id instead of
  name, and the per-container network panel is replaced by nginx requests per
  second.
- **Breaking:** the counter image writes a heartbeat file to `/tmp`; running it
  with a read-only root filesystem now needs a writable `/tmp`
  (`--tmpfs /tmp`).
- httpd runs as `www-data` (UID 82) on port 8080 from a minimal
  `compose/httpd/httpd.conf`, with no capabilities added back; the host port
  stays 8081.
- nginx moves to `nginxinc/nginx-unprivileged` 1.30 (the stable line) on port 8080;
  Portainer to the 2.39 LTS line; Grafana to 12.4; Prometheus, httpd and
  nginx-prometheus-exporter to their latest patch releases.
- counter exits promptly on SIGTERM when it runs as PID 1 (Kubernetes, or
  `docker run` without `--init`) instead of waiting to be killed.
- counter moves to Alpine 3.24 with a heartbeat healthcheck
  (`counter.sh --healthcheck`) that fails when the loop stalls; the old
  `pgrep` probe always matched docker-init and could never fail.
- dockerctl builds its venv from `cli/uv.lock` and runs it on one shared,
  digest-pinned `python:3.14-alpine3.24` base, and pip no longer ships in the
  image. Both images run as the numeric user `10001:10001`.
- **Breaking:** Python 3.10 is no longer supported (`requires-python >=3.11`).
- **Breaking:** `containers deploy` is hardened by default (`no-new-privileges`,
  all capabilities dropped, read-only root filesystem with `/tmp` on tmpfs,
  `--pids-limit 256`, `--memory 256m`, port bound to `127.0.0.1` unless an
  address is given, including an empty one as in `:8080:80`). Use the escape
  hatches or `--no-harden` for images that need more.
- `task cli` runs from the repository root so `dockerctl compose` finds the
  stack.
- CI runs on pull requests and pushes to `main` only (not on every branch
  push), and never cancels a run on `main`. Pre-commit ruff and mypy run from
  the lockfile; Dependabot tracks `uv` instead of `pip`.
- Dependency floors: typer ≥ 0.27.3, mypy ≥ 2.4.0, ruff ≥ 0.17.0,
  setuptools ≥ 84.0.0. GitHub Actions bumped to their latest releases.
- README layout, task list and counts match the repository; CONTRIBUTING,
  SECURITY and the PR template cover the chart, the ADRs and the release
  steps.

## [0.2.1] - 2026-07-02

### Added

- **CI boots the stack**: a `stack-test` job runs `docker compose up -d --wait`
  (every healthcheck becomes a CI assertion), probes nginx/httpd endpoints,
  and runs the built `dockerctl` image against the runner's live Docker socket.
- **Multi-arch images**: `linux/amd64` + `linux/arm64` on every GHCR push.
- **Signed, attested images**: cosign keyless signing (OIDC) plus BuildKit
  provenance (`mode=max`) and SBOM attestations; verification one-liner
  documented in SECURITY.md.
- PR template, YAML issue forms (bug/feature), and CODEOWNERS.
- VHS tape (`docs/assets/demo.tape`) for reproducing the README terminal demo,
  and a social-preview card image.

### Changed

- README refocused around `dockerctl` as a hardened operations toolkit:
  highlights strip with deep links, real `docker compose ps` output above the
  fold, collapsible reference tables, auto-generated ToC instead of a manual one.
- Dependabot now groups minor/patch Python updates into a single weekly PR.
- Design doc moved to `docs/design/production-upgrade-design.md`.
- Dependency floors raised by Dependabot: typer ≥ 0.26.8, pytest ≥ 9.1.1,
  setuptools ≥ 82.0.1.

## [0.2.0] - 2026-07-02

Production upgrade in four phases.

### Added

- **Compose:** healthchecks on nginx, httpd (busybox `wget`) and counter
  (`pgrep`); two network tiers (`web` / `mgmt`) isolating docker.sock
  consumers; CPU/memory limits; bounded json-file logging; `init: true` on
  counter.
- **CI/CD:** GHCR publish job pushing both images on every main push
  (`latest` + short SHA tags); CycloneDX SBOM per image as a build artifact;
  buildx layer caching; Dependabot for GitHub Actions, pip, and both
  Dockerfiles.
- **CLI:** `containers restart`, `containers stats`, `images tag`,
  `images push`; eager `--version`/`-V` root flag.
- **Release:** this workflow — semver-tagged GHCR images and a GitHub Release
  on every `v*` tag, with a tag/pyproject version guard.
- **Docs:** CONTRIBUTING.md, SECURITY.md, this changelog.

### Changed

- Compose image tags pinned by default (`nginx:1.27-alpine`,
  `httpd:2.4-alpine`, `portainer-ce:2.27.9`); alpine variants chosen so
  busybox `wget` can power the healthchecks.
- All services run read-only with all capabilities dropped (web servers
  re-add only what binding port 80 needs) and `no-new-privileges`.
- Every GitHub Action pinned to a full commit SHA; workflows run under
  least-privilege `permissions` with per-job escalation and per-ref
  concurrency.
- CLI version is single-sourced from `pyproject.toml` via
  `importlib.metadata`; mypy strict mode and a 90% coverage gate (currently
  100%) enforced in CI, pre-commit, and the Taskfile.
- README badges fixed to point at this repository.

### Fixed

- `containers exec` used an ellipsis default on a required argument
  (a strict-mypy violation and a Python anti-pattern).

## [0.1.0] - 2026-06-27

Initial modernization of the 5-year-old interactive bash labs.

### Added

- Declarative compose stack (nginx, httpd, portainer-ce, counter) replacing
  the `docker run` menu scripts.
- `dockerctl`: non-interactive Typer CLI (images pull/rm/ls/build, containers
  ls/rm/deploy/logs/stop/start/exec/inspect) with 23 tests.
- Taskfile single entrypoint; GitHub Actions CI (compose validate, hadolint,
  shellcheck, ruff, pytest, Trivy scan gating HIGH/CRITICAL).
- Multi-stage hardened images: counter (alpine, shellcheck build gate,
  non-root UID 10001), dockerctl (venv builder → python-alpine runtime).
- MIT license, styled landing page, full README.

### Removed

- All legacy interactive bash menu scripts, dead images
  (`abh1nav/dockerui`), and hardcoded AWS IPs.

[Unreleased]: https://github.com/www8351/Docker-DevOps-Tooling/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/www8351/Docker-DevOps-Tooling/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/www8351/Docker-DevOps-Tooling/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/www8351/Docker-DevOps-Tooling/compare/c6c601e...v0.2.0
[0.1.0]: https://github.com/www8351/Docker-DevOps-Tooling/compare/12b18a5...c6c601e
