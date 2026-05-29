"""Tests for the `containers` command group (arg construction + error paths)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dockerctl import containers
from dockerctl.__main__ import app
from dockerctl._docker import DockerError

runner = CliRunner()


def _record_calls(monkeypatch: pytest.MonkeyPatch, returns: str = "") -> list[tuple]:
    calls: list[tuple] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return returns

    monkeypatch.setattr(containers, "run", fake_run)
    return calls


def test_ls_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch, returns="NAMES\n")
    result = runner.invoke(app, ["containers", "ls"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps",)
    assert calls[0][1]["capture"] is True


def test_ls_all(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch, returns="")
    result = runner.invoke(app, ["containers", "ls", "--all"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps", "-a")


def test_rm_force(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["containers", "rm", "-f", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("rm", "--force", "web")


def test_deploy_builds_run_args(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(
        app,
        ["containers", "deploy", "nginx:latest", "--name", "web", "--port", "8080:80"],
    )
    assert result.exit_code == 0
    assert calls[0][0] == ("run", "-d", "--name", "web", "-p", "8080:80", "nginx:latest")
    assert "Deployed web" in result.stdout


def test_ls_json(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch, returns="{}\n")
    result = runner.invoke(app, ["containers", "ls", "--json"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps", "--format", "{{json .}}")


def test_logs_follow_tail(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["containers", "logs", "-f", "--tail", "5", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("logs", "--tail", "5", "--follow", "web")


def test_logs_default_tail(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["containers", "logs", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("logs", "--tail", "all", "web")


def test_stop_start(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    assert runner.invoke(app, ["containers", "stop", "web"]).exit_code == 0
    assert runner.invoke(app, ["containers", "start", "web"]).exit_code == 0
    assert calls[0][0] == ("stop", "web")
    assert calls[1][0] == ("start", "web")


def test_exec_passes_command(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch)
    result = runner.invoke(app, ["containers", "exec", "web", "--", "ls", "-la"])
    assert result.exit_code == 0
    assert calls[0][0] == ("exec", "web", "ls", "-la")


def test_inspect_json(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_calls(monkeypatch, returns="{}\n")
    result = runner.invoke(app, ["containers", "inspect", "--json", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("inspect", "--format", "{{json .}}", "web")


def test_rm_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise DockerError("nope")

    monkeypatch.setattr(containers, "run", boom)
    result = runner.invoke(app, ["containers", "rm", "ghost"])
    assert result.exit_code == 1
