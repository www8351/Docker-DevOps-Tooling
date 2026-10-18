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

Issue:  README layout tree, CLI command counts and remaining tables predate this roadmap.
Action: Phase 5.3 refreshes layout, counts and the Kubernetes and CI sections.
Status: OPEN

Issue:  Taskfile has no scan or sbom tasks.
Action: Phase 2.7.
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
