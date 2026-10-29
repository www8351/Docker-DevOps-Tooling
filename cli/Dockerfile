# syntax=docker/dockerfile:1
#
# dockerctl, the non-interactive Docker helper CLI, containerised.
#
# Multi-stage:
#   0) base    : one pinned Python + Alpine image shared by both stages below.
#                The venv embeds the interpreter version and libc, so the
#                builder and the runtime must never drift apart. Keeping a
#                single FROM line means a base bump moves both at once.
#   1) builder : install the locked dependencies from uv.lock into an
#                isolated venv (one cached layer), then the project itself.
#                uv comes from its own pinned image and never ships.
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
FROM python:3.14-alpine3.24@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72 AS base

# uv, pinned as its own stage so Dependabot tracks it like any other image.
FROM ghcr.io/astral-sh/uv:0.13.6@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv

# ---- Stage 1: builder -------------------------------------------------------
FROM base AS builder

COPY --from=uv /uv /usr/local/bin/uv

# The venv goes straight to /opt/venv, built with the base interpreter (uv
# must never download its own). uv venvs carry no pip.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

WORKDIR /src
# Dependencies first, from the lockfile only: this layer is reused until
# uv.lock or pyproject.toml change, whatever happens to the source.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
# Then the package itself, installed as a regular (non-editable) wheel.
COPY dockerctl/ dockerctl/
RUN uv sync --frozen --no-editable

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

# Numeric, so runtimes (and Kubernetes runAsNonRoot) can verify it is not root.
USER 10001:10001

ENTRYPOINT ["dockerctl"]
CMD ["--help"]
