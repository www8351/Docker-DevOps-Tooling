"""Tests for the `compose` command group (arg construction + error paths)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dockerctl import compose
from dockerctl.__main__ import app
from tests.conftest import DockerFails, RecordCalls

BASE = ("compose", "-f", "compose/docker-compose.yml")


def test_up_waits_for_health_by_default(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(app, ["compose", "up"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "up", "-d", "--wait", "--wait-timeout", "180")
    assert "Stack is up" in result.stdout


def test_up_services_profiles_and_timeout(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(
        app,
        [
            "compose",
            "up",
            "--profile",
            "observability",
            "--profile",
            "tools",
            "--wait-timeout",
            "60",
            "nginx",
            "httpd",
        ],
    )
    assert result.exit_code == 0
    assert calls[0][0] == (
        *BASE,
        "--profile",
        "observability",
        "--profile",
        "tools",
        "up",
        "-d",
        "--wait",
        "--wait-timeout",
        "60",
        "--",
        "nginx",
        "httpd",
    )


def test_up_no_wait(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(app, ["compose", "up", "--no-wait"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "up", "-d")


def test_file_from_environment(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(
        app, ["compose", "ps"], env={"DOCKERCTL_COMPOSE_FILE": "/srv/stack/compose.yml"}
    )
    assert result.exit_code == 0
    assert calls[0][0][:3] == ("compose", "-f", "/srv/stack/compose.yml")


def test_file_option_beats_environment(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(
        app,
        ["compose", "down", "-f", "other.yml"],
        env={"DOCKERCTL_COMPOSE_FILE": "/srv/stack/compose.yml"},
    )
    assert result.exit_code == 0
    assert calls[0][0][:3] == ("compose", "-f", "other.yml")


def test_down(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(app, ["compose", "down"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "down")
    assert "Stack is down" in result.stdout


def test_down_volumes(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose)
    result = runner.invoke(app, ["compose", "down", "--volumes", "--profile", "observability"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "--profile", "observability", "down", "--volumes")


def test_ps_captures_output(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose, returns="NAME\n")
    result = runner.invoke(app, ["compose", "ps"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "ps")
    assert calls[0][1]["capture"] is True
    assert result.stdout == "NAME\n"


def test_ps_all_json(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(compose, returns="[]\n")
    result = runner.invoke(app, ["compose", "ps", "--all", "--json"])
    assert result.exit_code == 0
    assert calls[0][0] == (*BASE, "ps", "--all", "--format", "json")


@pytest.mark.parametrize(
    "args",
    [
        ["compose", "up"],
        ["compose", "down"],
        ["compose", "ps"],
    ],
)
def test_every_command_error_exits_1(
    runner: CliRunner, docker_fails: DockerFails, args: list[str]
) -> None:
    docker_fails(compose, "`docker compose` failed: exit code 1")
    result = runner.invoke(app, args)
    assert result.exit_code == 1
    assert "docker compose" in result.stderr


def test_group_is_registered(runner: CliRunner) -> None:
    result = runner.invoke(app, ["compose", "--help"])
    assert result.exit_code == 0
    for command in ("up", "down", "ps"):
        assert command in result.stdout
