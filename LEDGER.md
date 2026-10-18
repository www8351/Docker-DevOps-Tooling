# LEDGER

Single management file for this project. Three sections: ISSUES (current state),
ACTIONS (dated log, newest first, append only), DECISIONS (locked log).
Every entry uses the same three lines: Issue, Action, Status.

---

## ISSUES

### Next action: Phase 2, CI and supply chain

Issue:  Phase 2 of the 0.3.0 roadmap (Track B) is in progress on branch ccr-1ddb6a39-8xlw9d, restarted from main at b0ca5ed.
Action: Ship commits 2.1 to 2.14, open a draft PR, drive CI green, stop for owner merge.
Status: IN PROGRESS

### Security and correctness

Issue:  CLI passes positional arguments without a -- separator. containers deploy runs containers with none of the repo hardening.
Action: Phase 3.3 and 3.4 (D12).
Status: OPEN

### CI and reproducibility

Issue:  publish job and release.yml duplicate build and sign logic; release.yml has no gates and tags latest on prereleases; Trivy scans only the amd64 build, not the published multi-arch images.
Action: Phase 2.10 and 2.11 (D11).
Status: OPEN

### Code quality

Issue:  The same try, DockerError, echo, Exit(1) block is copied 16 times across containers.py and images.py. Test helpers are duplicated with no conftest.py.
Action: Phase 3.1 and 3.2.
Status: OPEN

### Documentation

Issue:  README layout tree, CLI command counts and remaining tables predate this roadmap.
Action: Phase 5.3 refreshes layout, counts and the Kubernetes and CI sections.
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

---

## ACTIONS

### 2026-10-18

Issue:  No code scanning: no CodeQL and Trivy results only in job logs.
Action: New codeql.yml (python and actions, build-mode none, codeql-action v4.39.0 commit 6f2ac81f) on pushes to main, pull requests, weekly and on dispatch. The image job uploads a Trivy SARIF (MEDIUM and up, never gating) per image with continue-on-error for tokens that cannot write alerts; job gains security-events write. Repository is public, so code scanning needs no extra licence. Local: actionlint clean, zizmor No findings.
Status: DONE

Issue:  Workflows had no static analysis; zizmor flagged softprops/action-gh-release as superfluous (gh ships on the runner).
Action: New workflow-lint job: actionlint from rhysd/actionlint:1.7.12 pinned by digest b1934ee5 (bundles shellcheck), then zizmor 1.31.1 with online audits using the read-only job token. Release notes now come from gh release create --verify-tag --generate-notes with the notes passed through an env var. Local: actionlint v1.7.7 and the 1.7.12 image clean, zizmor offline No findings (15 suppressed by the regular persona).
Status: DONE

Issue:  Dependabot tracked pip (now replaced by uv.lock), opened one PR per action, watched each Dockerfile through a separate entry, and had no release cooldown (zizmor dependabot-cooldown, 5 findings).
Action: Dependabot ecosystems: github-actions (grouped into one PR), uv for /cli (minor and patch grouped), docker with directories /cli and /images/counter (also tracks the pinned uv stage), docker-compose for /compose; every ecosystem waits 7 days (cooldown default-days 7). Local: check-jsonschema vendor.dependabot ok, zizmor No findings.
Status: DONE

Issue:  lint failed on c554a50: hadolint-action v3.5.0 bundles hadolint v2.15.1, which reports DL3066 info: Non-numeric user-id may not be resolvable by host system, on USER app in both Dockerfiles, and the action fails at threshold info.
Action: Reproduced locally with hadolint/hadolint:v2.15.1-alpine (v2.14.0 does not have the rule). Both Dockerfiles now use USER 10001:10001, which Kubernetes runAsNonRoot also needs to verify a non-root user. Pre-commit hadolint pin moved to v2.15.1. Local: hadolint v2.15.1 with --failure-threshold info clean on both Dockerfiles.
Status: DONE

Issue:  Pre-commit pinned ruff v0.8.0, mypy v2.1.0 with unpinned stubs and a hadolint beta tag, all drifting from CI; Taskfile installed with pip and had no lock, scan or sbom tasks.
Action: ruff, ruff format and mypy are local hooks running uv run --locked --project cli --extra dev. hadolint runs from hadolint/hadolint:v2.14.0-alpine, shellcheck-precommit v0.11.0, actionlint v1.7.12, zizmor v1.31.1 (offline locally). Taskfile test, fmt, typecheck and cli use uv run --locked; lint runs compose config plus all hooks; new lock, scan and sbom tasks (aquasec/trivy:0.75.0 pinned by digest). CONTRIBUTING updated. Local: every hook passes except zizmor, whose 5 dependabot-cooldown and 1 superfluous-actions findings are fixed in the next commits; task test 45 passed, task typecheck Success, task cli -- version 0.2.1.
Status: DONE

Issue:  CI installed ruff unpinned and the CLI from pyproject.toml ranges, and tested only Python 3.12.
Action: lint job runs on Python 3.11 with astral-sh/setup-uv v10.3.0 (commit 1c37ad07), uv sync --locked --extra dev, then ruff, ruff format, dockerctl version, mypy and pytest through uv run --locked. New test job runs the suite from the lock on 3.12, 3.13, 3.14; publish needs it. Local run of the lint commands on 3.11: All checks passed, 10 files already formatted, 0.2.1, mypy Success, 45 passed.
Status: DONE

Issue:  The dockerctl image resolved dependencies with pip at build time and reinstalled them on every source change.
Action: Builder copies uv from ghcr.io/astral-sh/uv:0.11.32 pinned by index digest df4cae8f, runs uv sync --frozen --no-install-project on pyproject.toml plus uv.lock (cached layer), then uv sync --frozen --no-editable after copying the package. Local simulation in the pinned base with uv 0.11.32 from PyPI: typer 0.27.3 from the lock, no pip, no pytest, dockerctl version prints 0.2.1 after /src is removed. hadolint clean. GHCR blob host is blocked here, so the real image build is verified in CI.
Status: DONE

Issue:  No lockfile; lower bound only dependencies; requires-python >=3.10 with 3.10 reaching end of life; Dependabot floor bumps #41, #61, #63, #64 open.
Action: cli/uv.lock generated with uv 0.11.32 (23 packages, 434 sha256 hashes). Floors raised: typer>=0.27.3, mypy>=2.4.0, ruff>=0.17.0, setuptools>=84.0.0; requires-python >=3.11, ruff py311, mypy 3.11. Locked: ruff 0.17.1, mypy 2.4.0, typer 0.27.3. No code changes needed for the new linters. Local: uv lock --check resolved, ruff and format clean, mypy Success no issues in 10 files, pytest 45 passed on 3.11, 3.12, 3.13 and 3.14, coverage 100.00%.
Status: DONE

Issue:  Dependabot action bumps #49, #50, #56, #57, #58 open since August and September.
Action: Applied the exact SHAs from each Dependabot branch: hadolint-action v3.5.0, action-gh-release v3.0.3, setup-buildx-action v4.4.1, build-push-action v7.4.0, setup-qemu-action v4.4.0. Dependabot closes those PRs once main carries the versions.
Status: DONE

Issue:  CI ran twice per PR push (push on every branch plus pull_request), cancel-in-progress could cancel a publish on main, no job had a timeout, and checkouts kept the token in .git/config.
Action: ci.yml triggers on push to main, pull_request, workflow_dispatch and workflow_call; concurrency group per PR number or ref, cancelling only pull_request runs; timeout-minutes on every job in ci.yml and release.yml; persist-credentials false on all six checkouts. actionlint v1.7.7 with shellcheck: clean.
Status: DONE

Issue:  Phase 1 PR #65.
Action: Owner merged PR #65 into main as b0ca5ed (head c2afef7, all required checks green). Dependabot #38 closed. Branch ccr-1ddb6a39-8xlw9d restarted from main.
Status: DONE

Issue:  Adversarial review of the phase 1 diff: docs said Dependabot bumps compose pins but no docker-compose ecosystem existed; the fail-closed CI step passed on any up failure and skipped Grafana; task down and clean left the observability containers and volumes running; wait-prom-targets.sh curl had no timeout; the counter heartbeat silently made --tmpfs /tmp mandatory under --read-only; docs understated docker.sock holders and the stub_status residual.
Action: Added the Dependabot docker-compose ecosystem (moved forward from Phase 2.12). Fail-closed step now pulls first, checks portainer and grafana, requires the secret path in the error and no running container. down and clean pass --profile observability; obs:down removed. curl -m 10. README, SECURITY.md, CHANGELOG, Dockerfile comment and gen-secrets.sh header corrected. Local: step prints portainer refused and grafana refused, exit 0; with secrets present it fails with portainer started without its admin secret; task clean after obs:up leaves 0 containers and 0 volumes.
Status: DONE

Issue:  README claimed every long-running container was read-only and non-root and that the observability services shared the full baseline; pip was said never to ship; SECURITY.md listed only Portainer as a socket holder.
Action: README intro (English and Hebrew), highlights, console sample (real CI output from run 39140747430), quick start, stack and observability tables (with runs as column), image suite, counter and dockerctl hardening notes, task list, CI section and troubleshooting rewritten to match the stack. SECURITY.md lists socket holders, root services, loopback defaults and the first volume caveat for secrets. CONTRIBUTING.md describes digest pins and secrets. CHANGELOG Unreleased gains Security, Added and breaking Changed entries.
Status: DONE

Issue:  Portainer first run admin page could be claimed by whoever reached it first (#13, closed as completed without code). Portainer also had no read-only rootfs.
Action: Implements #13. Portainer runs with --admin-password-file from a compose secret, read_only true and tmpfs /tmp. stack-test asserts portainer refuses to start without the secret, then that POST /api/auth with the secret returns a jwt. Local: fail-closed refused, auth with secret returns jwt, wrong password 422, no errors in the log under read_only.
Status: DONE

Issue:  Grafana admin password defaulted to admin.
Action: scripts/gen-secrets.sh creates 32 character password files under gitignored compose/secrets (dir 0700, files 0644 so Grafana UID 472 can read). Grafana reads GF_SECURITY_ADMIN_PASSWORD__FILE from a compose secret, no default. Taskfile gains secrets, obs:up, obs:down; up waits for health. stack-test generates secrets and asserts 200 with the secret and 401 with admin:admin. Local: config valid without secret files, up grafana without the file fails with bind source path does not exist, /api/user with secret 200, with admin:admin 401.
Status: DONE

Issue:  nginx-exporter bridged the web and mgmt tiers; grafana and prometheus shared mgmt with portainer's docker.sock.
Action: Networks split into web, nginx-status (internal), metrics and mgmt; counter and dockerctl use network_mode none. Local probes: nginx to prometheus blocked, nginx to portainer blocked, grafana to portainer blocked, grafana to nginx blocked, prometheus to stub_status blocked, grafana to prometheus reachable, all 3 targets up. Known residual: httpd shares web with nginx and can read stub_status counters.
Status: DONE

Issue:  cAdvisor mounted /var/run (docker.sock and the containerd socket), the host rootfs and /var/lib/docker, kept all capabilities, and CI waited a fixed 20 seconds before checking Prometheus targets.
Action: cAdvisor now mounts only /sys:ro with cgroup: host and cap_drop ALL. Prometheus derives container_id from the cgroup path; the dashboard groups by it and swaps the per-container network panel for nginx requests per second. scripts/wait-prom-targets.sh polls targets instead of sleeping. stack-test asserts the cadvisor mounts are exactly /sys and that the nginx container has memory series under its container_id. Local run: targets 3 down [], mounts /sys, CapDrop [ALL], nginx memory series 1.
Status: DONE

Issue:  Compose image references sat in *_TAG variables Dependabot cannot follow; Portainer 2.27 and Grafana 12.3 no longer receive patches.
Action: Commit 74fa41b. Every image written literally as tag@digest, *_TAG variables removed. portainer-ce 2.39.8 (LTS), grafana 12.4.13, prometheus v3.13.4, nginx-prometheus-exporter 1.5.3, httpd 2.4.69-alpine3.24, cadvisor v0.55.1. Local boot of the stack minus counter: all healthchecks pass, all endpoints 200, all Prometheus targets up.
Status: DONE

Issue:  nginx 1.27 is unmaintained and needed four re-added capabilities to bind port 80.
Action: Commit 46bcab4. nginxinc/nginx-unprivileged 1.30.6 on port 8080, no capabilities, tmpfs /tmp only. Local check: healthy, HTTP 200, uid=101, CapEff 0, stub_status answers on 8082.
Status: DONE

Issue:  Every published port bound 0.0.0.0, including Portainer over HTTP and unauthenticated Prometheus.
Action: Commit b52420c. WEB_BIND_ADDR and ADMIN_BIND_ADDR default to 127.0.0.1; the lint job asserts loopback binding in the rendered config. Local check: published 5, off loopback [].
Status: DONE

Issue:  counter ran on end of life alpine:3.20 and its pgrep healthcheck could never fail.
Action: Commit 4158312. Shared digest pinned alpine:3.24 base, heartbeat file and counter.sh --healthcheck, image HEALTHCHECK, exec form probe in compose, network_mode none. Local check on alpine 3.24: running loop exit 0, frozen loop exit 1, old pgrep probe on the frozen loop exit 0, read-only rootfs without tmpfs makes the loop exit 1.
Status: DONE

Issue:  dockerctl image copied a glibc venv into a musl runtime; Dependabot PR #38 failed with ModuleNotFoundError: No module named 'dockerctl'.
Action: Commit 03d59ac. One digest pinned python:3.13-alpine3.24 base for builder and runtime, explicit COPY of pyproject.toml and the package, pip removed from venv and runtime, CI image job smoke runs the entrypoint. Local simulation in the pinned base: venv imports, dockerctl version prints 0.2.1, pip absent. Full image build left to CI because this environment blocks dl-cdn.alpinelinux.org.
Status: DONE

Issue:  Local verification inside the cloud environment.
Action: Started dockerd locally with mirror.gcr.io as registry mirror (Docker Hub answers 429). Image builds that run apk cannot complete here because the network policy blocks dl-cdn.alpinelinux.org; those builds are verified in CI.
Status: DONE

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

Issue:  D1 cAdvisor access to the container engine. cAdvisor v0.55.1 registers its Docker factory only with both docker.sock and a containerd client (container/docker/factory.go calls containerd.Client unconditionally), and the containerd API is root-equivalent and cannot be filtered by a proxy.
Action: Owner ruling 2026-10-18: no engine sockets at all. cAdvisor mounts only /sys read-only, uses cgroup: host, cap_drop ALL. Containers are identified by a short container_id derived from the cgroup path; per-container network counters are dropped. Rejected: GET only Docker proxy plus raw containerd socket (still root-equivalent), keeping the /var/run mount with documentation.
Status: FINAL

Issue:  D2 network layout.
Action: web (nginx, httpd), nginx-status internal (nginx, exporter), metrics (prometheus, grafana, cadvisor, exporter), mgmt (portainer). counter and dockerctl use network_mode none. The docker-api network was dropped with the socket proxy (see D1).
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
