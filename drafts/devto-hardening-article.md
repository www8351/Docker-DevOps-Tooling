---
title: "Make your CI boot the stack: read-only containers, SHA-pinned Actions, and the bug 'works on my machine' hid"
tags: docker, devops, security, cicd
published: false
---

<!-- Publish on dev.to. Promote via the short LinkedIn post in drafts/linkedin-and-cv.md
     linking here — do NOT cross-post full text to LinkedIn Articles (no canonical support). -->

Years ago I wrote a set of interactive bash menus to learn Docker (the public repo history
starts this year — the originals lived on my disk). They worked at a keyboard and nowhere
else. This year I rebuilt them into something I'd run in production: every container
read-only, every image signed, every merge gated by CI that actually **boots the stack**.

Here are the four changes that taught me the most, with real diffs from the repo
([Docker-DevOps-Tooling](https://github.com/www8351/Docker-DevOps-Tooling)).

## 1. Read-only containers with `cap_drop: ALL`

Most containers never need to write to their own filesystem — they just do because
nobody stopped them. Locking that down is one compose stanza per service:

```yaml
  nginx:
    image: nginx:1.27-alpine        # pinned; alpine's busybox wget powers the healthcheck
    read_only: true
    tmpfs:
      - /var/cache/nginx            # the only paths nginx actually writes
      - /var/run
      - /tmp
    cap_drop: [ALL]
    cap_add: [CHOWN, SETGID, SETUID, NET_BIND_SERVICE]
    security_opt:
      - no-new-privileges:true
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://127.0.0.1/"]
```

Two lessons from doing this across the whole stack:

- **The tmpfs list is the real work.** `read_only: true` is one line; knowing that httpd
  keeps its pid file under `logs/` and nginx needs `/var/run` is where you actually learn
  the images you run.
- **Image variants are load-bearing.** I moved to alpine tags specifically because busybox
  ships `wget` — which is what makes healthchecks possible without installing anything.

## 2. Rebuild the image, not just the config

The original version of one image ran a trivial counter loop on `ubuntu:24.04` with
`openssh-server`, `sshpass`, and `tcpdump` installed — none of it used, all of it exactly
what a scanner flags first. The hardened rebuild is a two-stage Dockerfile:

- **Stage 1** runs `shellcheck` against the script — broken shell fails `docker build`,
  so bad code never reaches an image.
- **Stage 2** starts from `alpine:3.20` and copies in *only* the validated script, owned
  by a fixed-ID non-root user, mounted read-and-execute only.

Result: **~7 MB instead of 78 MB**, and Trivy's HIGH/CRITICAL gate passes clean — there's
almost nothing left in the image to scan. The removed packages *were* the attack surface.

## 3. SHA-pin your GitHub Actions (tags are movable)

`uses: some-action@v3` feels pinned. It isn't — tags can be re-pointed, and if that
action gets compromised, "v3" quietly becomes malicious code with your repo's token. The
[tj-actions/changed-files incident](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
(CVE-2025-30066) made this concrete for thousands of repos.

The fix is pinning to full commit SHAs, with the version as a comment so humans (and
Dependabot, which updates SHA pins just fine) can still read it:

```yaml
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
```

While I was in there: a workflow-level `permissions: contents: read` block (jobs escalate
individually), and per-ref concurrency so superseded pushes cancel.

## 4. Make CI prove it, not just lint it

From day one, my CI validated the compose file — and stayed green. Validating is not
running. Now every push boots all eight long-running services of the hardened stack —
including an optional observability profile (Prometheus, Grafana, cAdvisor) whose scrape
targets CI also gates on — and `--wait` turns every healthcheck into an assertion:

```yaml
      - name: Boot the hardened stack (healthchecks gate)
        run: |
          cp compose/.env.example compose/.env
          docker compose -f compose/docker-compose.yml --profile observability up -d --wait --wait-timeout 180
      - name: Probe web endpoints
        run: |
          curl -fsS http://localhost:8080
          curl -fsS http://localhost:8081
      # trimmed — full job in .github/workflows/ci.yml
```

This caught a real bug on the job's first run — one that had been hiding for weeks. The
stack's CLI image runs as a non-root user (UID 10001) and drives the Docker engine
through a mounted socket. Worked perfectly on my machine. In CI:
`permission denied while trying to connect to the docker API`. On my machine, Docker
Desktop leaves the socket wide open; a real Linux host's is `root:docker` `0660`. The fix
keeps the hardening intact — grant the container the socket's group instead of root:

```bash
docker run --rm \
  --group-add "$(stat -c '%g' /var/run/docker.sock)" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  dockerctl:local containers ls
```

To be clear: anything holding the Docker socket is root-equivalent — that's inherent to a
tool whose job is driving the engine. The hardening isn't pretending otherwise; it's
making sure the container gets exactly that one privilege and nothing else: non-root
user, no added capabilities, read-only filesystem, and the socket's group rather than
blanket root.

"Works locally, fails in CI" is exactly the class of bug that only surfaces when the
pipeline runs the real thing.

## The rest of the supply chain

Once CI boots and probes the stack, the publishing side follows the same principle —
don't claim it, attest it:

- **Trivy** gates merges on fixable HIGH/CRITICAL vulnerabilities.
- **CycloneDX SBOMs** are generated for every image build and attached as artifacts, so
  "what exactly is in this image?" has a machine-readable answer for every build.
- Published images are **multi-arch** (amd64/arm64) with BuildKit **provenance
  attestations** (`mode=max`) — a signed record of what built the image, from which
  commit, on which runner.
- Every pushed digest is **cosign-signed** (keyless, GitHub OIDC). Anyone can verify:

```bash
cosign verify \
  --certificate-identity-regexp 'https://github.com/www8351/Docker-DevOps-Tooling/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/www8351/docker-devops-tooling/dockerctl:latest
```

Every piece of this is in the open repo, including the
[design doc](https://github.com/www8351/Docker-DevOps-Tooling/blob/main/docs/design/production-upgrade-design.md)
written before implementation and the
[CHANGELOG](https://github.com/www8351/Docker-DevOps-Tooling/blob/main/CHANGELOG.md)
tracking each release: **github.com/www8351/Docker-DevOps-Tooling**

If you're hardening your own stack, start with `read_only: true` on one service and let
the crash logs teach you its tmpfs list. It's the highest signal-per-line change in
container security.
