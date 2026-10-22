# 0004. Images are multi-stage, Alpine based and run as a fixed non-root user

- Status: Accepted
- Date: 2026-06-26

## Context

The original counter image was Ubuntu with an SSH server, tcpdump and
Python installed, none of which the script used, and it ran as root.

## Decision

Both published images ([counter](../../images/counter/Dockerfile),
[dockerctl](../../cli/Dockerfile)) build in stages from one digest-pinned
Alpine based image: a build or lint stage (shellcheck, or a venv built from
`uv.lock`) and a runtime stage that copies only the result. The runtime runs
as the numeric user `10001:10001`, numeric so Kubernetes `runAsNonRoot` can
verify it. hadolint gates both Dockerfiles.

## Alternatives considered

- **Distroless.** No shell means no busybox `wget` or `sh` for healthchecks,
  and the counter is a shell script.
- **Single-stage builds.** The build toolchain (shellcheck, uv) would ship.

## Consequences

Small images with little to scan. Anything that runs them read-only must
give them a writable `/tmp`. Changing the UID is a breaking change for
anyone who mounts volumes.
