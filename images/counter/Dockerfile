# syntax=docker/dockerfile:1
#
# counter, a minimal, hardened demo image.
#
# Multi-stage:
#   0) base    : one pinned Alpine image shared by both stages below, so the
#                lint toolchain and the runtime always move together.
#   1) lint    : shellcheck the script at build time (a broken script fails the
#                build, not just CI). Nothing from this stage ships.
#   2) runtime : a tiny Alpine image carrying ONLY the validated script,
#                executed by an unprivileged user.
#
# Previously this ran on ubuntu:24.04 (~78 MB) and installed openssh-server,
# sshpass, tcpdump, net-tools and python3, none of which the script uses.
# That was pure attack surface; it is all gone.

# ---- Stage 0: shared base ---------------------------------------------------
FROM alpine:3.24@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6 AS base

# ---- Stage 1: build-time lint gate -----------------------------------------
FROM base AS lint

# hadolint ignore=DL3018
RUN apk add --no-cache shellcheck

WORKDIR /src
COPY counter.sh .
RUN shellcheck counter.sh

# ---- Stage 2: runtime -------------------------------------------------------
FROM base AS runtime

LABEL maintainer="refael malka"

# Unprivileged user/group with fixed IDs (predictable for volume permissions).
RUN addgroup -S -g 10001 app \
    && adduser -S -u 10001 -G app app

# Copy only the script that passed the lint stage.
COPY --from=lint --chown=root:root /src/counter.sh /usr/local/bin/counter.sh
RUN chmod 0555 /usr/local/bin/counter.sh

# Numeric, so runtimes (and Kubernetes runAsNonRoot) can verify it is not root.
USER 10001:10001

# The loop touches a heartbeat file in /tmp (override with COUNTER_HEARTBEAT);
# a stale or missing file means the loop has stopped. Compose runs the same
# probe command. With a read-only root filesystem, /tmp must be writable
# (e.g. --tmpfs /tmp), otherwise the loop exits on its first iteration.
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD ["/usr/local/bin/counter.sh", "--healthcheck"]

# POSIX sh ships in Alpine's busybox, so no bash package is required.
CMD ["/usr/local/bin/counter.sh"]
