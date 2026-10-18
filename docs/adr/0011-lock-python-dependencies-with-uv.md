# 0011. Lock Python dependencies with uv

- Status: Accepted
- Date: 2026-10-18

## Context

Dependencies were floating floors in `pyproject.toml`, so CI, the image and
a developer's machine could each resolve different versions, and nothing
recorded which ones a green build had used.

## Decision

`cli/uv.lock` pins every dependency with hashes. CI installs with
`uv sync --locked`, the image builds its venv with `uv sync --frozen` in a
builder stage that shares its digest-pinned Python Alpine base with the
runtime (so the venv is built for the libc it runs on), and the pre-commit
ruff and mypy hooks run from the same lock.
Dependabot's `uv` ecosystem proposes updates. Lint runs on Python 3.11, the
oldest supported, and the test matrix covers 3.12 to 3.14.

## Alternatives considered

- **pip-tools.** Works, but needs a separate compile step per platform and
  is slower; uv also manages the Python versions used by the matrix.
- **No lock.** The problem above.

## Consequences

Dependency changes are `task lock` plus a committed `uv.lock`. Contributors
need uv for the locked environment.
