# syntax=docker/dockerfile:1
#
# dockerctl, the non-interactive Docker helper CLI, containerised.
#
# Multi-stage:
#   0) base    : one pinned Python + Alpine image shared by both stages below.
#                The venv embeds the interpreter version and libc, so the
#                builder and the runtime must never drift apart. Keeping a
#                single FROM line means a base bump moves both at once.
#   1) builder : install the project (and typer) into an isolated venv.
#                pip is removed from the venv once the install is done.
#   2) runtime : the same base carrying only the venv and the docker client,
#                with the system pip removed, run by an unprivileged user.
#
# Because dockerctl shells out to the `docker` CLI (see dockerctl/_docker.py),
# the runtime installs docker-cli so the tool is functional against a mounted
# /var/run/docker.sock:
#
#   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#       dockerctl images pull nginx:latest
#
# `version` / `--help` need no socket.

# ---- Stage 0: shared base ---------------------------------------------------
FROM python:3.13-alpine3.24@sha256:2d9aefe2fef018a7eb2c13064c89c71929800fd2e5dccdbf52ea5da5bb8d929a AS base

# ---- Stage 1: builder -------------------------------------------------------
FROM base AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Isolated venv we can copy wholesale into the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
# Only what the build needs: metadata first, then the package itself.
COPY pyproject.toml ./
COPY dockerctl/ dockerctl/
RUN pip install . \
    && pip uninstall --yes pip

# ---- Stage 2: runtime -------------------------------------------------------
FROM base AS runtime

LABEL maintainer="refael malka"

# docker client only (no daemon); talks to a mounted socket.
# The interpreter's own pip is not needed at runtime, so it goes too.
# hadolint ignore=DL3018
RUN apk add --no-cache docker-cli \
    && python -m pip uninstall --yes --disable-pip-version-check --root-user-action=ignore pip \
    && addgroup -S -g 10001 app \
    && adduser -S -u 10001 -G app app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER app

ENTRYPOINT ["dockerctl"]
CMD ["--help"]
