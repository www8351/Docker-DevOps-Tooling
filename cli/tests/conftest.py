"""Shared fixtures: a CLI runner and fakes for the docker subprocess wrapper.

Command modules import `run` from `dockerctl._docker`, so tests patch the name
inside the module under test (e.g. `dockerctl.containers.run`).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from types import ModuleType

import pytest
from typer.testing import CliRunner

from dockerctl._docker import DockerError

Call = tuple[tuple[str, ...], dict[str, object]]
RecordCalls = Callable[..., list[Call]]
DockerFails = Callable[..., None]

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(text: str) -> str:
    """Drop ANSI styling. Typer forces colour when GITHUB_ACTIONS is set."""
    return _ANSI.sub("", text)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def record_calls(monkeypatch: pytest.MonkeyPatch) -> RecordCalls:
    """Replace `module.run` with a fake that records its arguments."""

    def _record(module: ModuleType, returns: str = "") -> list[Call]:
        calls: list[Call] = []

        def fake_run(*args: str, **kwargs: object) -> str:
            calls.append((args, kwargs))
            return returns

        monkeypatch.setattr(module, "run", fake_run)
        return calls

    return _record


@pytest.fixture
def docker_fails(monkeypatch: pytest.MonkeyPatch) -> DockerFails:
    """Replace `module.run` with a fake that raises DockerError."""

    def _fail(module: ModuleType, message: str = "nope") -> None:
        def boom(*args: str, **kwargs: object) -> str:
            raise DockerError(message)

        monkeypatch.setattr(module, "run", boom)

    return _fail
