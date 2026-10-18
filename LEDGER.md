# LEDGER

Single management file for this project. Three sections: ISSUES (current state),
ACTIONS (dated log, newest first, append only), DECISIONS (locked log).
Every entry uses the same three lines: Issue, Action, Status.

---

## ISSUES

### Next action: Phase 5, docs, ADRs, demo GIF and release 0.3.0

Issue:  Phase 5 of the 0.3.0 roadmap (#15, #17, docs accuracy, release prep) is in progress on branch ccr-1ddb6a39-8xlw9d, restarted from main at 3d9c57f.
Action: Ship commits 5.1 to 5.6, open a draft PR, drive CI green, stop for owner merge. The owner pushes the v0.3.0 tag.
Status: IN PROGRESS

### Security and correctness

### CI and reproducibility

Issue:  Every astral-sh/setup-uv step resolves the latest uv (0.13.1 in the Phase 3 runs) while cli/Dockerfile pins uv 0.11.32, so CI and the image can drift.
Action: Pin a uv version in the setup-uv steps, or record why not. Raised in the PR #77 body; not yet decided.
Status: OPEN

### Code quality

### Documentation

Issue:  README layout tree, CLI command counts and remaining tables predate this roadmap.
Action: Phase 5.3 refreshed layout, counts, tasks and links, and added a full Hebrew section.
Status: DONE

### Features closed as completed without code (milestone v0.3.0)

Issue:  #12 Helm chart for nginx, httpd, counter validated on kind does not exist.
Action: Phase 4 shipped deploy/chart and the CI helm job (PR #78, merged as 3d9c57f).
Status: DONE

Issue:  #15 ADRs in docs/adr do not exist.
Action: Phase 5.1 added docs/adr with records 0001 to 0014.
Status: DONE

Issue:  #17 demo GIF from docs/assets/demo.tape was never rendered or committed.
Action: Phase 5.2 rendered docs/assets/demo.gif from a rewritten tape.
Status: DONE

### Open Dependabot PRs

---

## ACTIONS

### 2026-10-18

Issue:  Release 0.3.0 preparation (Phase 5.5); the chart runs counter at its appVersion, but nothing tied that to the release tag (D15).
Action: cli/pyproject.toml 0.3.0 and uv lock (Updated dockerctl v0.2.1 -> v0.3.0; uv lock --check clean); deploy/chart appVersion already 0.3.0. release.yml guard also requires deploy/chart/Chart.yaml appVersion to equal the tag. CHANGELOG: [Unreleased] cut to [0.3.0] - 2026-10-18 with a summary line, Phase 5 items added (ADRs, demo GIF, Hebrew README, contributor docs), the release guard bullet updated, compare links for 0.3.0 and the new Unreleased. README: v0.3.0 in highlights and the releases section, the appVersion check described in English and Hebrew. Local: the guard script extracted from release.yml printed "v0.3.0 matches cli/pyproject.toml (0.3.0) and the chart appVersion" (exit 0), and exited 1 for v0.3.1 (pyproject mismatch), v0.3.0-rc.1 (pyproject mismatch) and appVersion 0.2.1 ("appVersion is 0.2.1, expected 0.3.0"); before the changelog cut it exited 1 with "CHANGELOG.md has no '## [0.3.0]' section". pytest 75 passed, coverage 100.00%, dockerctl --version 0.3.0; actionlint clean; zizmor no findings; helm lint passes.
Status: DONE

Issue:  CONTRIBUTING, SECURITY and the PR template do not cover the chart, the ADRs or the release guard (Phase 5.4).
Action: CONTRIBUTING: chart:lint and kind:test in the gates table, chart conventions (restricted profile, images and httpd.conf in step with compose, bump the chart version), the ADR rule, and release steps naming pyproject version, task lock, chart appVersion, changelog section and compare link. SECURITY: the chart is in scope, a posture bullet for the chart and its CI proof, and a pointer to the ADRs. PR template: chart and ADR checklist items. Em dashes removed. The release guard on the chart appVersion that CONTRIBUTING now describes lands in Phase 5.5.
Status: DONE

Issue:  README predates the roadmap in places (layout tree, task list, test count) and its Hebrew part was a short intro that mixed English words into Hebrew sentences (Phase 5.3).
Action: README: tagline names the Helm chart; demo GIF embedded; highlights updated (75 tests, the chart on kind under restricted, the ADRs); architecture diagram and layer table gain the chart; layout tree rewritten from the actual tree (compose subfolders, deploy/chart, cli modules and tests, scripts, docs/adr, workflows); task list matches every Taskfile task; design principles and links gain the ADRs; every em dash removed. A full Hebrew section now follows the English one and mirrors every section, with tables and the full command reference pointed to the English part; English terms in it sit in backticks only, and the top intro links to it. Local: no em or en dashes; no mention of LEDGER, CLAUDE or AI; every relative link resolves; a scan of Hebrew lines finds no Latin word outside backticks or link targets except the bilingual "What is this? · מה זה?" heading.
Status: DONE

Issue:  #17 demo GIF from docs/assets/demo.tape was never rendered (Phase 5.2); the old tape called dockerctl without installing it and showed none of the hardening.
Action: Rewrote the tape: bash with a plain prompt and Wait on it instead of fixed sleeps, dockerctl from the locked project; task up (secrets, wait for health), compose ps, a hardened dockerctl deploy, docker inspect showing read-only=true cap-drop=[ALL] pids=256, curl returning 200, rm --force, task down. Rendered here with vhs v0.12.1 (Go module proxy), ttyd 1.7.4 (Ubuntu archive), ffmpeg and the preinstalled Playwright Chromium (VHS_NO_SANDBOX=1, running as root). Result docs/assets/demo.gif: 998537 bytes, 38.64s, 1100x620; frames checked by eye. The counter image in the recording was built locally from the runtime stage of images/counter/Dockerfile without its shellcheck stage, because apk mirrors are unreachable from this machine; the script and base image are the same. The first render failed because the wait pattern expected a trailing space after the prompt.
Status: DONE

Issue:  Phase 4 PR #78.
Action: Owner merged PR #78 into main as 3d9c57f (head 229e36c, all 15 run checks green including helm, publish skipped). Branch ccr-1ddb6a39-8xlw9d restarted from main and force pushed with lease. The pending check-in was cancelled.
Status: DONE

Issue:  #15 ADRs in docs/adr do not exist (Phase 5.1).
Action: New docs/adr: README index, template.md (context, decision, alternatives, consequences), and records 0001 to 0014: recording decisions, compose owns state, typed non-interactive CLI, multi-stage Alpine non-root images, SHA-pinned actions, Trivy gate on fixable HIGH and CRITICAL, explicit socket holders, cAdvisor without engine sockets (D1), loopback binds (D3), file secrets (D4), uv lock (D7), unprivileged web servers (D9), publish by digest (D11), Helm chart under the restricted profile. Local: every relative link resolves; no em or en dashes.
Status: DONE

Issue:  helm failed on 8fbd584 at the last assertion: "reached the Kubernetes API: the NetworkPolicy is not enforced". Everything before it passed: the namespace refused a bare pod, the chart installed under enforce=restricted, all three Deployments rolled out, and helm test printed nginx: 200 and httpd: 200. The check was wrong, not the policy: traffic between a pod and its own node is always allowed by the NetworkPolicy model, and on a one-node kind cluster the API server runs on that node.
Action: Dropped tests.checkNetworkPolicy and the API probe from the chart (values, schema, test pod). CI instead execs into nginx, which may open no connection: a fetch of its own page must succeed (wget and exec work), and a fetch of the httpd pod IP on 8080, the pod the test pod just reached, must fail with a network error (timed out, refused, no route or unreachable). README and Taskfile updated. Local: actionlint clean, zizmor no findings, helm lint --strict passes, kubeconform Valid: 11; busybox wget -T 5 against a DROP rule printed "wget: download timed out" with exit 1 after 5s; the step logic passes on timed out and refused, and fails on success and on exec errors.
Status: DONE

Issue:  README and CHANGELOG do not describe the chart (Phase 4.5).
Action: README gains a Kubernetes (Helm chart) section (hardening, shared httpd.conf and images, NetworkPolicy, install and helm test commands, local counter override, chart tasks), a helm job paragraph under CI, deploy/chart and compose/httpd in the layout, a Helm, kind and kubectl requirement row, and the chart tasks in the task list; CHANGELOG Unreleased gains the chart and the helm job under Added. Local: helm v3.22.1 lint --strict passes and, at --kube-version 1.37.0, renders the same objects as helm v4.3.1 apart from blank lines (kubeconform Valid: 11); the README states Helm 3 or 4 on that basis.
Status: DONE

Issue:  No local entry points for the chart (Phase 4.4).
Action: Taskfile gains chart:lint (helm lint --strict), chart:template, and kind:test, which mirrors the CI helm job on a throwaway cluster (create, build and kind load counter:local, restricted namespace, helm install --wait, helm test --logs, deferred cluster delete). Local: task --list shows all three; task chart:lint 1 chart(s) linted, 0 chart(s) failed; task chart:template renders 11 objects; task --dry kind:test prints the expected command sequence. kind:test itself cannot run in this container (see the tooling entry).
Status: DONE

Issue:  The chart needs a real cluster check under the restricted Pod Security Standard (Phase 4.2).
Action: New CI job helm: azure/setup-helm v5.0.1 (9bc31f4e) with helm v4.3.1; asserts compose/httpd/httpd.conf equals deploy/chart/files/httpd.conf and that the rendered nginx and httpd images equal the compose ones (D14); helm lint --strict; helm/kind-action v1.15.1 (1544676c, kind v0.33.0, kindnetd enforces NetworkPolicy); builds counter and kind loads it; creates namespace stack labelled enforce=restricted and first proves enforcement (a bare pod is refused with violates PodSecurity "restricted"); helm install --wait with the local counter and tests.checkNetworkPolicy=true; rollout status for all three Deployments; helm test --logs; diagnostics on failure. publish now also needs helm. Local: actionlint clean, zizmor no findings; the sync step printed both images and exited 0, and exited 1 after changing the nginx tag in values.yaml or appending to the chart httpd.conf. kind itself runs in CI only.
Status: DONE

Issue:  #12 Helm chart for nginx, httpd and counter (Phase 4.1).
Action: New deploy/chart (devops-stack 0.1.0, appVersion 0.3.0, kubeVersion >=1.29): Deployments for nginx (uid 101), httpd (uid 82, files/httpd.conf from a ConfigMap, checksum annotation) and counter (uid 10001, exec probes on counter.sh --healthcheck); ClusterIP Services on 8080; every pod runAsNonRoot with seccomp RuntimeDefault, readOnlyRootFilesystem, allowPrivilegeEscalation false, capabilities drop ALL, a 16Mi in-memory emptyDir on /tmp, limits mirroring compose; one ServiceAccount with no token; NetworkPolicies default-deny, web ingress on 8080, test pod egress to the web pods and kube-dns; a helm test pod that fetches both services and, with tests.checkNetworkPolicy, requires the Kubernetes API to be unreachable; values.schema.json with additionalProperties false. Local: helm lint --strict 1 chart(s) linted, 0 chart(s) failed; kubeconform -strict on the rendered chart Valid: 11, Invalid: 0; the schema rejects nginx.replica (additional properties 'replica' not allowed), httpd.runAsUser=0 (minimum: got 0, want 1) and a non sha256 digest.
Status: DONE

Issue:  counter.sh ignored SIGTERM when it ran as PID 1, as it will in a Kubernetes pod (compose hides this with init: true), so every stop waited out the grace period and ended in SIGKILL.
Action: counter.sh traps INT and TERM and exits 0. Local, alpine 3.24 as 10001 with the script mounted and no init: docker stop took 0.45s with exit 0, against 5.17s and exit 137 for the previous script; --healthcheck still passes; shellcheck clean.
Status: DONE

Issue:  compose httpd still ran its master as root and re-added CHOWN, SETGID, SETUID and NET_BIND_SERVICE to bind port 80 (D9).
Action: New compose/httpd/httpd.conf (Listen 8080, pid and mutexes in /tmp, logs to stdout and stderr, ServerTokens Prod, TraceEnable Off, nosniff header, root directory denied); compose runs httpd as 82:82 with it mounted over the image config, only /tmp on tmpfs and no cap_add. README and SECURITY.md updated. Local: docker compose up --wait reported compose-httpd-1 Healthy, user=82:82 ro=true capadd=[] capdrop=[ALL], every process www-data, :8081 returned 200; under docker run the same config answered TRACE with 405 and a path outside htdocs with 404.
Status: DONE

Issue:  Phase 3 PR #77.
Action: Owner merged PR #77 into main as 8aa5aa9 (head 87f7526, all 14 run checks green, publish skipped). main also carries 09e8956, Dependabot PR #76 (actions/upload-artifact 7.0.1 to 7.0.2). Branch ccr-1ddb6a39-8xlw9d restarted from main and force pushed with lease.
Status: DONE

Issue:  Phase 4 needs helm, kind, kubectl and kubeconform locally; GitHub release downloads and get.helm.sh are blocked here.
Action: Installed through the Go module proxy: helm v4.3.1, kind v0.33.0, kubeconform v0.8.0; kubectl v1.37.1 from dl.k8s.io with its sha256 verified. kind cannot run in this container: the host is cgroup v1, and even with failCgroupV1 false runc fails inside the node ("can't get final child's PID from pipe: EOF"). The chart is validated locally with helm lint, helm template and kubeconform, and each container is run under docker with the chart's user, read-only root and dropped capabilities; the kind install runs in CI only.
Status: DONE

Issue:  lint, test (3.12), test (3.13) and test (3.14) failed on 80ab2c7: 5 failed, 70 passed. The new --no-harden usage error test looked for --no-harden in stderr, but typer forces rich colour when GITHUB_ACTIONS is set, and the ANSI codes split the flag name ("\x1b[1;33mUsage: ..." in the log). Not visible locally without that variable.
Action: Reproduced with GITHUB_ACTIONS=true (same 5 failed). Added plain() to tests/conftest.py to drop ANSI codes; the test now asserts "Invalid value for '--no-harden'" and "cannot be combined with <flag>" on the plain text. Local: 75 passed with and without GITHUB_ACTIONS=true (also at COLUMNS=40), coverage 100.00%, ruff and mypy clean.
Status: DONE

Issue:  Review of PR #77 at aabc156 found: deploy -p :8080:80 (empty host address) was passed through, publishing on every interface; --no-harden silently dropped --cap-add, --tmpfs, --writable, --memory and --pids-limit; a user --tmpfs /tmp:size=... was mounted next to the default /tmp; the --port help claimed loopback even under --no-harden; the CI inspect step printed health without asserting it; the CI check for compose inside the image accepted any failure; the host compose ps parser only read one JSON object per line. The aabc156 stack-test log also showed the in-image error is "unknown shorthand flag: 'f' in -f" (docker-cli 29.8.2), not the "unknown command" text recorded in the compose group entry below.
Action: Tests first (8 failed, 67 passed), then fixed: an empty host address gets 127.0.0.1 (:8080:80 to 127.0.0.1:8080:80, ::80 to 127.0.0.1::80); --memory and --pids-limit default to None and resolve to 256m and 256 only when hardened; --no-harden with any hardening option is a usage error (exit 2, "Invalid value for '--no-harden': cannot be combined with ...") before any docker call; a user tmpfs for /tmp replaces the default; help texts corrected. CI asserts State.Health.Status == healthy, requires exit 1 plus a docker usage error match for compose inside the image, and parses compose ps as an array or one object per line. README, CHANGELOG and the compose docstring updated. Local: 75 passed, coverage 100.00%, ruff and mypy clean, actionlint clean, zizmor no findings; the new shell and parser logic simulated for pass and fail inputs. Live: deploy -p :18081:8080 --tmpfs /tmp:size=16m published {"HostIp":"127.0.0.1","HostPort":"18081"}, Tmpfs /tmp size=16m only, ReadonlyRootfs true, Memory 268435456, PidsLimit 256, HTTP 200; --no-harden --pids-limit 64 exited 2.
Status: DONE

Issue:  stack-test failed on 84e6e30: the new host step ran `dockerctl compose --profile observability ps`, but --profile is an option of each subcommand, so Typer answered No such option: --profile and the service check saw no rows.
Action: Reproduced locally (same error, exit 2). The step now runs `dockerctl compose ps --profile observability --json`; locally it lists the running services. README notes that --file and --profile follow the subcommand, unlike docker compose.
Status: DONE

Issue:  README still showed two command groups, a deploy example that cannot run hardened (nginx:latest needs capabilities), and task cli ran from cli/ where the compose default path does not resolve.
Action: README documents the -- guarantee, the hardened deploy defaults and escape hatches, the compose group (host only, file resolution), and the full reference (3 groups, 19 commands); the deploy example uses nginx-unprivileged. task cli runs from the repo root via uv run --project cli. CHANGELOG Unreleased gains the separator under Security, the compose group and deploy flags under Added, and the hardened deploy as breaking. Local: task cli -- --version 0.2.1, task cli -- compose --help lists up, down, ps.
Status: DONE

Issue:  First publish on main through the shared _publish.yml after merging #72.
Action: CI run 39156291406 on 4d99cfc: publish (counter) and publish (dockerctl) both pushed by digest, passed Trivy on linux/amd64 and linux/arm64, signed with cosign and tagged with every tag verified against the signed digest. All other jobs green.
Status: DONE

Issue:  CI only ran `containers ls` from the dockerctl image, so the -- separator, positional commands and the compose group were never exercised against a real engine.
Action: stack-test now runs containers inspect --json compose-nginx-1 (asserting name and health) and containers logs --tail 1 compose-counter-1 through the image, asserts dockerctl compose ps fails inside the image (no compose plugin, D13), and runs dockerctl compose --profile observability ps --json on the host via uv, requiring nginx, counter and grafana. Local: the inspect and compose ps parsing ran against a live nginx (inspect -> /compose-nginx-1 healthy, compose ps -> ['nginx']). actionlint clean, zizmor No findings.
Status: DONE

Issue:  #14 dockerctl compose up, down, ps group did not exist (closed as completed without code).
Action: Implements #14. New cli/dockerctl/compose.py registered as `dockerctl compose`: up [SERVICES] (-d, --wait by default, --wait-timeout 180, --no-wait), down (--volumes), ps (--all, --json); --file defaults to compose/docker-compose.yml with DOCKERCTL_COMPOSE_FILE override; repeatable --profile; services passed after --. The dockerctl image has no compose plugin (D13), so inside the image these exit 1 with docker's unknown command error. Tests first (collection failed), then implemented: 66 passed, coverage 100.00%, mypy and ruff clean. Live from the repo root: compose up --wait-timeout 90 nginx httpd reached healthy and printed Stack is up; ps and ps --json listed both healthy; a missing file via DOCKERCTL_COMPOSE_FILE exited 1 with compose file is invalid; down --volumes printed Stack is down.
Status: DONE

Issue:  containers deploy ran containers with none of the repo hardening and published ports on every interface.
Action: deploy is hardened by default (D12): no-new-privileges, cap-drop ALL, read-only rootfs with /tmp on tmpfs, pids-limit 256, memory 256m, port bound to 127.0.0.1 unless an address is given. Escape hatches --cap-add, --tmpfs, --writable, --user, --memory, --pids-limit, --no-harden. Tests first (6 failed), then implemented. Local: 53 passed, coverage 100.00%. Live: nginx-unprivileged deployed with defaults ran with ReadonlyRootfs true, CapDrop [ALL], no-new-privileges, tmpfs /tmp, PidsLimit 256, Memory 268435456, bound 127.0.0.1:18080, HTTP 200.
Status: DONE

Issue:  Positional values went straight into docker argv, so a value starting with a dash would be parsed as a docker flag.
Action: Every docker call in containers.py and images.py now puts -- before its positional arguments. Tests updated first (16 failed), then implemented; new test passes a container named -f through as a name. Local: 46 passed, coverage 100.00%, mypy and ruff clean. Live against docker 29.8.2: images pull, build, tag, push (to a local registry), rm and containers deploy, logs, inspect, stats, exec, restart, stop, start, rm all ok.
Status: DONE

Issue:  The same try, DockerError, echo to stderr, Exit(1) block was copied 16 times across containers.py (10) and images.py (6).
Action: New cli/dockerctl/_cli.py with a docker_errors() context manager; every command body now runs under it. Behaviour unchanged. Local: ruff clean, mypy Success no issues in 12 source files, 45 passed, coverage 100.00%.
Status: DONE

Issue:  Test helpers (_record_calls and boom) were copied into test_containers.py and test_images.py with no conftest.py.
Action: cli/tests/conftest.py provides runner, record_calls(module, returns) and docker_fails(module, message) fixtures with RecordCalls and DockerFails type aliases; both test modules use them with full annotations. Local: ruff clean, mypy Success no issues in 11 source files, 45 passed, coverage 100.00%.
Status: DONE

Issue:  Phase 2 PR #72.
Action: Owner merged PR #72 into main as 4d99cfc (head af32474, all 15 checks green). Branch ccr-1ddb6a39-8xlw9d restarted from main.
Status: DONE

Issue:  Adversarial review of the phase 2 diff: the dry-run registry service also ran (and was pulled from Docker Hub) for real publishes; major.minor relied on metadata-action alone to skip prereleases; gh release create failed on a re-run once the release existed; main publish did not wait for workflow-lint while releases did; comments overstated main concurrency and test gating; docs still said CI runs on every push.
Action: Registry now starts in a step gated on dry-run (bound to 127.0.0.1:5000); major.minor explicitly disabled for tags containing a dash; github-release skips when the release exists; publish needs workflow-lint; ci.yml comments state that main runs queue one at a time with a newer merge replacing a waiting one (grouping by sha was rejected because two publishes could race on latest); README and SECURITY.md say pull requests instead of every push. self-repository is a valid zizmor id (zizmor reports 4 ignored). actionlint clean, zizmor No findings.
Status: DONE

Issue:  README, SECURITY.md and CHANGELOG still described per-branch CI, pip installs, Python 3.10, the old publish and an ungated release.
Action: README: Python 3.11+ badge and requirement, uv, lockfile based dockerctl build, CI section with lint, test, workflow-lint, image SARIF, stack-test, shared publish steps and dry run, CodeQL, Dependabot with cooldown, gated release flow. SECURITY.md: cosign identity now _publish.yml@ref (existing regexp still matches), publish order, gated releases, lockfile, CodeQL and workflow linting. CHANGELOG Unreleased gains Security, Added and Changed entries including the Python 3.10 drop as breaking.
Status: DONE

Issue:  The dockerctl image ran Python 3.13; the 3.14 move had been deferred until the venv and typer were verified on 3.14.
Action: Base moved to python:3.14-alpine3.24 pinned by index digest f6a589d4 (3.14.8). Evidence: CI test (3.14) leg passed on 4ee0dd8; local simulation of the uv builder on the pinned 3.14 base: Python 3.14.8, dockerctl version 0.2.1, --help renders, missing docker binary handled. The CI image job smoke run confirms the built image.
Status: DONE

Issue:  release.yml pushed and signed on any v* tag without lint, tests or a scan, tagged latest on prereleases, and only compared the tag string to pyproject.toml.
Action: release.yml now runs guard (packaging normalised tag vs cli/pyproject.toml, stable tags need a CHANGELOG section), then the whole ci.yml via workflow_call with the union of nested permissions, then _publish.yml in release mode, then gh release create with --prerelease for tags containing a dash. Local guard runs: v0.2.1 matches 0.2.1; v0.3.0, v0.2.1-rc.1, v0.2.2 rejected; v0.3.0-rc.1 matches 0.3.0rc1 without a changelog section; stable v0.3.0 rejected without its section and accepted with it. actionlint clean, zizmor No findings. The tag path itself only runs on a real tag; an owner pushed v0.3.0-rc.1 after Phase 4 would exercise it without moving latest.
Status: DONE

Issue:  The main publish built and tagged multi-arch images in one step, so latest moved before anything scanned the pushed bytes; only the amd64 CI build was ever scanned; release.yml duplicated the logic.
Action: New reusable _publish.yml (modes main, release, dry-run): push by digest only, Trivy on the pushed digest for linux/amd64 and linux/arm64, cosign sign the digest, then docker buildx imagetools create the tags and fail unless every tag resolves to the scanned digest. latest=auto keeps latest off prereleases. No build cache in publish. ci.yml publish calls it with mode main; a new publish-dry-run job runs it on every pull request against a registry:3.1.1 service container without signing. Local: imagetools retag preserved index digest 294b683c including attestation manifests; tag step exit 0 when tags match, exit 1 on a digest mismatch; actionlint clean; zizmor No findings (2 self-repository ignored with reason: ./ already pins the callee to this commit and actionlint does not parse $/ yet).
Status: DONE

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

Issue:  D14 chart image references.
Action: values.yaml pins nginx and httpd to the same tag and digest as compose/docker-compose.yml, and CI fails if they differ. Dependabot keeps bumping compose; a compose bump goes red until the chart values follow in the same PR.
Status: REVISIT

Issue:  D15 counter image in the chart.
Action: Defaults to ghcr.io/www8351/docker-devops-tooling/counter at the chart appVersion (0.3.0, set ahead of the release because the 0.2.x images lack counter.sh --healthcheck). CI loads a local build into kind with pullPolicy Never. The release guard asserts appVersion matches the tag.
Status: REVISIT

Issue:  Alertmanager and Loki in the observability profile.
Action: Out of scope, as recorded in compose/docker-compose.yml and README before this ledger existed.
Status: REVISIT

Issue:  Portainer read-write access to docker.sock.
Action: Known design decision recorded in SECURITY.md: a Docker management UI needs the engine.
Status: REVISIT
