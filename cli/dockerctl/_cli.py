"""Shared plumbing for the command groups."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import typer

from ._docker import DockerError


@contextmanager
def docker_errors() -> Iterator[None]:
    """Report a failed docker call on stderr and exit with status 1."""
    try:
        yield
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
