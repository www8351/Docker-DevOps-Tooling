# syntax=docker/dockerfile:1
#
# dockerctl — the non-interactive Docker helper CLI, containerised.
#
# Multi-stage:
#   1) builder — install the project (and typer) into an isolated venv using a
#                full Python toolchain. None of that toolchain ships.
#   2) runtime — a slim Alpine + Python image carrying only the venv and the
#                docker client, run by an unprivileged user.
#
# Because dockerctl shells out to the `docker` CLI (see dockerctl/_docker.py),
# the runtime installs docker-cli so the tool is functional against a mounted
# /var/run/docker.sock:
#
#   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#       dockerctl images pull nginx:latest
#
# `version` / `--help` need no socket.

# ---- Stage 1: builder -------------------------------------------------------
FROM python:3.14-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Isolated venv we can copy wholesale into the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
COPY . .
RUN pip install .

# ---- Stage 2: runtime -------------------------------------------------------
FROM python:3.14-alpine AS runtime

LABEL maintainer="refael malka"

# docker client only (no daemon); talks to a mounted socket.
# hadolint ignore=DL3018
RUN apk add --no-cache docker-cli \
    && addgroup -S -g 10001 app \
    && adduser -S -u 10001 -G app app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER app

ENTRYPOINT ["dockerctl"]
CMD ["--help"]
