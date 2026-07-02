# syntax=docker/dockerfile:1
#
# counter — a minimal, hardened demo image.
#
# Multi-stage:
#   1) lint    — shellcheck the script at build time (a broken script fails the
#                build, not just CI). Nothing from this stage ships.
#   2) runtime — a tiny Alpine image carrying ONLY the validated script,
#                executed by an unprivileged user.
#
# Previously this ran on ubuntu:24.04 (~78 MB) and installed openssh-server,
# sshpass, tcpdump, net-tools and python3 — none of which the script uses.
# That was pure attack surface; it is all gone.

# ---- Stage 1: build-time lint gate -----------------------------------------
FROM alpine:3.24 AS lint

# hadolint ignore=DL3018
RUN apk add --no-cache shellcheck

WORKDIR /src
COPY counter.sh .
RUN shellcheck counter.sh

# ---- Stage 2: runtime -------------------------------------------------------
FROM alpine:3.24 AS runtime

LABEL maintainer="refael malka"

# Unprivileged user/group with fixed IDs (predictable for volume permissions).
RUN addgroup -S -g 10001 app \
    && adduser -S -u 10001 -G app app

# Copy only the script that passed the lint stage.
COPY --from=lint --chown=root:root /src/counter.sh /usr/local/bin/counter.sh
RUN chmod 0555 /usr/local/bin/counter.sh

USER app

# POSIX sh ships in Alpine's busybox — no bash package required.
CMD ["/usr/local/bin/counter.sh"]
