# LEDGER

Single management file for this project. Three sections: ISSUES (current state),
ACTIONS (dated log, newest first, append only), DECISIONS (locked log).
Every entry uses the same three lines: Issue, Action, Status.

---

## ISSUES

### Next action: Phase 1, harden the stack and images

Issue:  Phase 1 of the 0.3.0 roadmap (Track A plus #13) is in progress on branch ccr-1ddb6a39-8xlw9d.
Action: Ship commits 1.1 to 1.11, push, open a draft PR, drive CI green, stop for owner merge.
Status: IN PROGRESS

### Security and correctness

Issue:  cAdvisor mounts /var/run:/var/run:ro. A read-only bind does not block API calls, so cAdvisor holds full Docker API access. It also keeps all capabilities and runs as root.
Action: Phase 1.9. Route cAdvisor through a GET only socket proxy (D1), drop the mount, cap_drop ALL.
Status: OPEN

Issue:  nginx-exporter joins both web and mgmt, bridging the public tier to the socket tier. Grafana and Prometheus share mgmt with portainer and cadvisor.
Action: Phase 1.10. Split networks per D2.
Status: OPEN

Issue:  Grafana admin password defaults to admin and is published on every interface.
Action: Phase 1.7. Compose secret with GF_SECURITY_ADMIN_PASSWORD__FILE, no default (D4).
Status: OPEN

Issue:  Every published port binds 0.0.0.0, including Portainer over HTTP and unauthenticated Prometheus.
Action: Phase 1.4. WEB_BIND_ADDR and ADMIN_BIND_ADDR default to 127.0.0.1 (D3).
Status: OPEN

Issue:  counter healthcheck pgrep -f counter.sh always matches PID 1 (docker-init runs counter.sh under init: true), so it can never fail.
Action: Phase 1.3. Heartbeat file plus counter.sh --healthcheck (D10).
Status: OPEN

Issue:  dockerctl image copies a glibc venv (python:3.12-slim) into a musl runtime (python:3.12-alpine). Dependabot PR #38 bumps only the runtime and fails stack-test with ModuleNotFoundError: No module named 'dockerctl'.
Action: Phase 1.2. One shared alpine base stage for builder and runtime (D5).
Status: OPEN

Issue:  counter image uses alpine:3.20, which is end of life. nginx:1.27-alpine is an unmaintained branch. No image is pinned by digest. Compose images are not tracked by Dependabot.
Action: Phase 1.3, 1.5, 1.6. alpine 3.24, nginx-unprivileged stable, literal digest pinned refs (D6, D9).
Status: OPEN

Issue:  Portainer first run admin page can be claimed by whoever reaches it first (#13, closed as completed without code).
Action: Phase 1.8. --admin-password-file from a compose secret.
Status: OPEN

Issue:  CLI passes positional arguments without a -- separator. containers deploy runs containers with none of the repo hardening.
Action: Phase 3.3 and 3.4 (D12).
Status: OPEN

Issue:  release.yml publishes and signs without lint, tests or Trivy, and tags latest on every v* tag including prereleases. Trivy scans only the amd64 build; the published multi-arch images are never scanned.
Action: Phase 2.10 and 2.11 (D11).
Status: OPEN

### CI and reproducibility

Issue:  No lockfile. Dependencies have lower bounds only. The Dockerfile resolves latest at build time. CI installs ruff unpinned.
Action: Phase 2.3 and 2.5. uv.lock with hashes (D7).
Status: OPEN

Issue:  Pre-commit revisions drift from CI (ruff v0.8.0, mypy v2.1.0, hadolint beta tag).
Action: Phase 2.7. Drive ruff and mypy from the lockfile.
Status: OPEN

Issue:  requires-python >=3.10 (3.10 reaches end of life October 2026) while CI tests 3.12 only.
Action: Phase 2.3 and 2.6. Floor 3.11, test matrix 3.12 to 3.14 (D8).
Status: OPEN

Issue:  CI runs twice per PR push (push on all branches plus pull_request). cancel-in-progress can cancel a main publish. No job timeouts. stack-test sleeps a fixed 20 seconds.
Action: Phase 1.9 replaces the sleep. Phase 2.1 fixes triggers, concurrency, timeouts.
Status: OPEN

Issue:  No workflow linting (actionlint, zizmor), no CodeQL, no SARIF upload. publish job and release.yml duplicate build and sign logic.
Action: Phase 2.8, 2.9, 2.10.
Status: OPEN

### Code quality

Issue:  The same try, DockerError, echo, Exit(1) block is copied 16 times across containers.py and images.py. Test helpers are duplicated with no conftest.py.
Action: Phase 3.1 and 3.2.
Status: OPEN

### Documentation

Issue:  README claims every long-running container is read-only and non-root, and that the observability services share the full baseline. Portainer has no read_only, several processes run as root, cAdvisor had no cap_drop. README also claims pip never ships, which is false.
Action: Phase 1.11 corrects hardening claims. Phase 5.3 refreshes layout, task list, tables, counts.
Status: OPEN

Issue:  Taskfile has no observability, secrets, scan or sbom tasks, and up does not wait for health.
Action: Phase 1.7 and 2.7.
Status: OPEN

### Features closed as completed without code (milestone v0.3.0)

Issue:  #14 dockerctl compose up, down, ps group does not exist.
Action: Phase 3.5.
Status: OPEN

Issue:  #12 Helm chart for nginx, httpd, counter validated on kind does not exist.
Action: Phase 4.
Status: OPEN

Issue:  #15 ADRs in docs/adr do not exist.
Action: Phase 5.1.
Status: OPEN

Issue:  #17 demo GIF from docs/assets/demo.tape was never rendered or committed.
Action: Phase 5.2.
Status: OPEN

### Open Dependabot PRs

Issue:  #38 python 3.13-alpine runtime only bump, failing.
Action: Superseded by Phase 1.2. Owner closes after merge.
Status: OPEN

Issue:  #41 setuptools, #61 mypy, #63 typer, #64 ruff floor bumps.
Action: Absorbed in Phase 2.3. Owner closes those Dependabot does not auto close.
Status: OPEN

Issue:  #49 hadolint-action, #50 action-gh-release, #56 setup-buildx, #57 build-push, #58 setup-qemu.
Action: Absorbed in Phase 2.2 with the exact SHAs from each PR.
Status: OPEN

---

## ACTIONS

### 2026-10-18

Issue:  No project ledger existed; findings and the roadmap lived only in a session plan.
Action: Created LEDGER.md seeded with the audit findings, the five unimplemented v0.3.0 features, the open Dependabot PRs, owner rulings and the planned technical decisions.
Status: DONE

---

## DECISIONS

Issue:  Scope of the 0.3.0 roadmap.
Action: Owner ruling 2026-10-18: include all four tracks (maintenance and security, CI and supply chain, v0.3.0 features, documentation accuracy and release).
Status: FINAL

Issue:  Which v0.3.0 features to implement.
Action: Owner ruling 2026-10-18: implement all of #12 (Helm on kind), #13 (Portainer secret), #14 (compose group), #15 (ADRs), #17 (demo GIF).
Status: FINAL

Issue:  Push policy in the ephemeral cloud environment.
Action: Owner ruling 2026-10-18: push automatically to the designated branch ccr-1ddb6a39-8xlw9d and open draft PRs. Merging to main stays with the owner.
Status: FINAL

Issue:  Where LEDGER.md lives.
Action: Owner ruling 2026-10-18: create it at the repo root and commit it.
Status: FINAL

Issue:  D1 cAdvisor access to the Docker API.
Action: GET only socket proxy (wollomatic/socket-proxy, digest pinned) allowing _ping, version, info, containers/json, containers/<id>/json. cAdvisor drops the /var/run mount and all capabilities. Rejected: removing the mount (3 of 4 dashboard panels need the name label), keeping it documented (full read-write API).
Status: REVISIT

Issue:  D2 network layout.
Action: web (nginx, httpd), nginx-status internal (nginx, exporter), metrics (prometheus, grafana, cadvisor, exporter), docker-api internal (proxy, cadvisor), mgmt (portainer). counter and dockerctl use network_mode none.
Status: REVISIT

Issue:  D3 bind address for published ports.
Action: WEB_BIND_ADDR and ADMIN_BIND_ADDR, both default 127.0.0.1.
Status: REVISIT

Issue:  D4 admin secrets.
Action: File secrets in gitignored compose/secrets, generated by scripts/gen-secrets.sh. Grafana via GF_SECURITY_ADMIN_PASSWORD__FILE, Portainer via --admin-password-file. No default password; a missing file fails up.
Status: REVISIT

Issue:  D5 dockerctl base image.
Action: One digest pinned python alpine base stage shared by builder and runtime, so Dependabot cannot split them. pip removed from the final image.
Status: REVISIT

Issue:  D6 compose image references.
Action: Literal digest pinned refs, *_TAG variables dropped, Dependabot docker-compose ecosystem added. Overrides move to compose.override.yaml.
Status: REVISIT

Issue:  D7 lockfile tool.
Action: uv with cli/uv.lock, uv sync --locked in CI and the image, Dependabot uv ecosystem.
Status: REVISIT

Issue:  D8 supported Python.
Action: requires-python >=3.11, lint on 3.11, test matrix 3.12, 3.13, 3.14. Image moves to 3.14 only if tests and image smoke pass.
Status: REVISIT

Issue:  D9 unprivileged web servers.
Action: nginxinc/nginx-unprivileged stable alpine on port 8080 in compose and chart. Official httpd:2.4-alpine as uid 82 with a minimal httpd.conf on 8080. counter reaches kind via kind load and pullPolicy Never.
Status: REVISIT

Issue:  D10 counter health signal.
Action: Heartbeat file touched each loop, counter.sh --healthcheck fails when it is stale.
Status: REVISIT

Issue:  D11 publish pipeline.
Action: Reusable _publish.yml: push by digest, Trivy each platform of the pushed digest, cosign sign, tag with imagetools create, assert the digest is unchanged, latest=auto.
Status: REVISIT

Issue:  D12 containers deploy defaults.
Action: Hardened by default with escape hatches (--cap-add, --tmpfs, --writable, --user, --no-harden). Breaking under 0.x.
Status: REVISIT

Issue:  D13 compose plugin inside the dockerctl image.
Action: Not added. dockerctl compose exits 1 with a clear message inside the image.
Status: REVISIT

Issue:  Alertmanager and Loki in the observability profile.
Action: Out of scope, as recorded in compose/docker-compose.yml and README before this ledger existed.
Status: REVISIT

Issue:  Portainer read-write access to docker.sock.
Action: Known design decision recorded in SECURITY.md: a Docker management UI needs the engine.
Status: REVISIT
