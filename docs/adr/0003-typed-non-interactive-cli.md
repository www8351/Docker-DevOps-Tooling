# 0003. A typed, non-interactive CLI wraps the docker CLI

- Status: Accepted
- Date: 2026-05-27

## Context

The old menus asked questions and parsed `docker` output with shell. They
could not run in CI, returned no useful exit codes and had no tests.

## Decision

`dockerctl` ([`cli/`](../../cli)) is a Python CLI built on Typer. Every input
is a flag or an argument, never a prompt. It calls the `docker` binary
through one wrapper (`cli/dockerctl/_docker.py`) that turns a non-zero exit
into a typed error, which every command reports on stderr with exit status
1. Every docker call ends option parsing with `--` before positional values,
so a name starting with a dash is never read as a flag. The code is
mypy-strict clean and the suite runs with a 90% coverage gate.

## Alternatives considered

- **The Docker SDK for Python.** It would add a large dependency and a second
  model of the engine; wrapping the CLI keeps behaviour identical to what an
  operator types and needs no daemon in unit tests.
- **More shell.** Untestable at the level of argument construction, which is
  where the bugs were.

## Consequences

Unit tests assert the exact docker argument list without an engine; one live
CI step drives the built image against a real engine. The CLI needs the
`docker` binary on `PATH`, and `dockerctl compose` needs the compose plugin,
which the image deliberately does not ship.
