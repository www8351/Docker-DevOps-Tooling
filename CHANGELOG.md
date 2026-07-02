# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Observability compose profile**: Prometheus (pinned `v3.13.0`, read-only
  scrape config), Grafana (`12.3.8`, provisioned datasource + committed
  container dashboard — zero click-ops), cAdvisor, and nginx-prometheus-exporter
  (via a non-host-mapped `stub_status` endpoint). All four follow the existing
  hardening baseline. CI boots the profile and fails if any Prometheus target
  is down.

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

[Unreleased]: https://github.com/www8351/Docker-DevOps-Tooling/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/www8351/Docker-DevOps-Tooling/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/www8351/Docker-DevOps-Tooling/compare/c6c601e...v0.2.0
[0.1.0]: https://github.com/www8351/Docker-DevOps-Tooling/compare/12b18a5...c6c601e
