"""Tests for the `images` command group (arg construction + error paths)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dockerctl import images
from dockerctl.__main__ import app
from dockerctl._docker import DockerError

runner = CliRunner()


def _record_calls(monkeypatch: pytest.MonkeyPatch) -> list[tuple]:
    calls: list[tuple] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return ""

    monkeypatch.setattr(images, "run", fake_run)
    return calls


def test_pull_builds_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "pull", "nginx:latest"])
    assert result.exit_code == 0
    assert calls[0][0] == ("pull", "nginx:latest")
    assert "pulled nginx:latest" in result.stdout


def test_rm_force(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "rm", "--force", "abc123"])
    assert result.exit_code == 0
    assert calls[0][0] == ("rmi", "--force", "abc123")


def test_ls_json(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "ls", "--json"])
    assert result.exit_code == 0
    assert calls[0][0] == ("images", "--format", "{{json .}}")


def test_build_builds_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "build", "images/counter", "-t", "counter:latest"])
    assert result.exit_code == 0
    assert calls[0][0] == ("build", "-t", "counter:latest", "images/counter")
    assert "Built counter:latest" in result.stdout


def test_pull_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise DockerError("`docker pull` failed: nope")

    monkeypatch.setattr(images, "run", boom)
    result = runner.invoke(app, ["images", "pull", "bogus"])
    assert result.exit_code == 1
