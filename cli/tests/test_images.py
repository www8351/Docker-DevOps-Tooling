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


def test_tag_builds_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "tag", "counter:ci", "ghcr.io/acme/counter:1.0"])
    assert result.exit_code == 0
    assert calls[0][0] == ("tag", "counter:ci", "ghcr.io/acme/counter:1.0")
    assert "Tagged counter:ci" in result.stdout


def test_push_builds_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["images", "push", "ghcr.io/acme/counter:1.0"])
    assert result.exit_code == 0
    assert calls[0][0] == ("push", "ghcr.io/acme/counter:1.0")
    assert "pushed ghcr.io/acme/counter:1.0" in result.stdout


def test_tag_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise DockerError("nope")

    monkeypatch.setattr(images, "run", boom)
    result = runner.invoke(app, ["images", "tag", "a", "b"])
    assert result.exit_code == 1


def test_push_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise DockerError("nope")

    monkeypatch.setattr(images, "run", boom)
    result = runner.invoke(app, ["images", "push", "bogus"])
    assert result.exit_code == 1


def test_pull_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise DockerError("`docker pull` failed: nope")

    monkeypatch.setattr(images, "run", boom)
    result = runner.invoke(app, ["images", "pull", "bogus"])
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "args",
    [
        ["images", "ls"],
        ["images", "build", "ctx", "-t", "x:1"],
        ["images", "rm", "abc123"],
    ],
)
def test_every_command_error_exits_1(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
    def boom(*a, **kw):
        raise DockerError("nope")

    monkeypatch.setattr(images, "run", boom)
    result = runner.invoke(app, args)
    assert result.exit_code == 1
