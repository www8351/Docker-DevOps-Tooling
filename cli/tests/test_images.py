"""Tests for the `images` command group (arg construction + error paths)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dockerctl import images
from dockerctl.__main__ import app
from tests.conftest import DockerFails, RecordCalls


def test_pull_builds_args(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "pull", "nginx:latest"])
    assert result.exit_code == 0
    assert calls[0][0] == ("pull", "--", "nginx:latest")
    assert "pulled nginx:latest" in result.stdout


def test_rm_force(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "rm", "--force", "abc123"])
    assert result.exit_code == 0
    assert calls[0][0] == ("rmi", "--force", "--", "abc123")


def test_ls_json(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "ls", "--json"])
    assert result.exit_code == 0
    assert calls[0][0] == ("images", "--format", "{{json .}}")


def test_build_builds_args(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "build", "images/counter", "-t", "counter:latest"])
    assert result.exit_code == 0
    assert calls[0][0] == ("build", "-t", "counter:latest", "--", "images/counter")
    assert "Built counter:latest" in result.stdout


def test_tag_builds_args(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "tag", "counter:ci", "ghcr.io/acme/counter:1.0"])
    assert result.exit_code == 0
    assert calls[0][0] == ("tag", "--", "counter:ci", "ghcr.io/acme/counter:1.0")
    assert "Tagged counter:ci" in result.stdout


def test_push_builds_args(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(images)
    result = runner.invoke(app, ["images", "push", "ghcr.io/acme/counter:1.0"])
    assert result.exit_code == 0
    assert calls[0][0] == ("push", "--", "ghcr.io/acme/counter:1.0")
    assert "pushed ghcr.io/acme/counter:1.0" in result.stdout


def test_tag_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(images)
    result = runner.invoke(app, ["images", "tag", "a", "b"])
    assert result.exit_code == 1


def test_push_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(images)
    result = runner.invoke(app, ["images", "push", "bogus"])
    assert result.exit_code == 1


def test_pull_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(images, "`docker pull` failed: nope")
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
def test_every_command_error_exits_1(
    runner: CliRunner, docker_fails: DockerFails, args: list[str]
) -> None:
    docker_fails(images)
    result = runner.invoke(app, args)
    assert result.exit_code == 1
