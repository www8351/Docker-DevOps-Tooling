"""Tests for the `containers` command group (arg construction + error paths)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from dockerctl import containers
from dockerctl.__main__ import app
from tests.conftest import DockerFails, RecordCalls


def test_ls_default(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers, returns="NAMES\n")
    result = runner.invoke(app, ["containers", "ls"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps",)
    assert calls[0][1]["capture"] is True


def test_ls_all(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "ls", "--all"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps", "-a")


def test_rm_force(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "rm", "-f", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("rm", "--force", "--", "web")


HARDENED = (
    "--security-opt",
    "no-new-privileges:true",
    "--cap-drop",
    "ALL",
)


def test_deploy_is_hardened_by_default(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app,
        ["containers", "deploy", "nginx:latest", "--name", "web", "--port", "8080:80"],
    )
    assert result.exit_code == 0
    assert calls[0][0] == (
        "run",
        "-d",
        "--name",
        "web",
        *HARDENED,
        "--read-only",
        "--tmpfs",
        "/tmp",
        "--pids-limit",
        "256",
        "--memory",
        "256m",
        "-p",
        "127.0.0.1:8080:80",
        "--",
        "nginx:latest",
    )
    assert "Deployed web from nginx:latest on 127.0.0.1:8080:80" in result.stdout


@pytest.mark.parametrize(
    ("given", "published"),
    [
        ("8080:80", "127.0.0.1:8080:80"),
        ("80", "127.0.0.1::80"),
        ("8443:443/tcp", "127.0.0.1:8443:443/tcp"),
        ("0.0.0.0:8080:80", "0.0.0.0:8080:80"),
        ("[::1]:8080:80", "[::1]:8080:80"),
        (":8080:80", "127.0.0.1:8080:80"),
        ("::80", "127.0.0.1::80"),
    ],
)
def test_deploy_binds_to_loopback_unless_an_address_is_given(
    runner: CliRunner, record_calls: RecordCalls, given: str, published: str
) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "deploy", "img", "-n", "web", "-p", given])
    assert result.exit_code == 0
    args = calls[0][0]
    assert args[args.index("-p") + 1] == published


def test_deploy_escape_hatches(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app,
        [
            "containers",
            "deploy",
            "img",
            "-n",
            "web",
            "-p",
            "8080:80",
            "--cap-add",
            "NET_BIND_SERVICE",
            "--cap-add",
            "CHOWN",
            "--tmpfs",
            "/var/cache/nginx",
            "--writable",
            "--user",
            "101:101",
            "--memory",
            "64m",
            "--pids-limit",
            "32",
        ],
    )
    assert result.exit_code == 0
    assert calls[0][0] == (
        "run",
        "-d",
        "--name",
        "web",
        *HARDENED,
        "--cap-add",
        "NET_BIND_SERVICE",
        "--cap-add",
        "CHOWN",
        "--tmpfs",
        "/tmp",
        "--tmpfs",
        "/var/cache/nginx",
        "--pids-limit",
        "32",
        "--memory",
        "64m",
        "--user",
        "101:101",
        "-p",
        "127.0.0.1:8080:80",
        "--",
        "img",
    )


def test_deploy_user_tmpfs_for_tmp_replaces_the_default(
    runner: CliRunner, record_calls: RecordCalls
) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app,
        ["containers", "deploy", "img", "-n", "web", "-p", "80", "--tmpfs", "/tmp:size=64m"],
    )
    assert result.exit_code == 0
    args = calls[0][0]
    tmpfs = [args[i + 1] for i, a in enumerate(args) if a == "--tmpfs"]
    assert tmpfs == ["/tmp:size=64m"]


@pytest.mark.parametrize(
    "extra",
    [
        ["--cap-add", "CHOWN"],
        ["--tmpfs", "/run"],
        ["--writable"],
        ["--memory", "1g"],
        ["--pids-limit", "64"],
    ],
)
def test_deploy_no_harden_rejects_hardening_options(
    runner: CliRunner, record_calls: RecordCalls, extra: list[str]
) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app, ["containers", "deploy", "img", "-n", "web", "-p", "80", "--no-harden", *extra]
    )
    assert result.exit_code == 2
    assert "--no-harden" in result.stderr
    assert calls == []


def test_deploy_no_harden_keeps_user(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app,
        ["containers", "deploy", "img", "-n", "web", "-p", "80", "--no-harden", "--user", "1000"],
    )
    assert result.exit_code == 0
    assert calls[0][0] == ("run", "-d", "--name", "web", "--user", "1000", "-p", "80", "--", "img")


def test_deploy_no_harden_is_a_plain_run(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(
        app,
        ["containers", "deploy", "nginx:latest", "-n", "web", "-p", "8080:80", "--no-harden"],
    )
    assert result.exit_code == 0
    assert calls[0][0] == ("run", "-d", "--name", "web", "-p", "8080:80", "--", "nginx:latest")


def test_ls_json(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers, returns="{}\n")
    result = runner.invoke(app, ["containers", "ls", "--json"])
    assert result.exit_code == 0
    assert calls[0][0] == ("ps", "--format", "{{json .}}")


def test_logs_follow_tail(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "logs", "-f", "--tail", "5", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("logs", "--tail", "5", "--follow", "--", "web")


def test_logs_default_tail(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "logs", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("logs", "--tail", "all", "--", "web")


def test_stop_start(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    assert runner.invoke(app, ["containers", "stop", "web"]).exit_code == 0
    assert runner.invoke(app, ["containers", "start", "web"]).exit_code == 0
    assert calls[0][0] == ("stop", "--", "web")
    assert calls[1][0] == ("start", "--", "web")


def test_exec_passes_command(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "exec", "web", "--", "ls", "-la"])
    assert result.exit_code == 0
    assert calls[0][0] == ("exec", "--", "web", "ls", "-la")


def test_inspect_json(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers, returns="{}\n")
    result = runner.invoke(app, ["containers", "inspect", "--json", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("inspect", "--format", "{{json .}}", "--", "web")


def test_restart_default(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "restart", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("restart", "--", "web")
    assert "Restarted web" in result.stdout


def test_restart_with_time(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "restart", "-t", "5", "web"])
    assert result.exit_code == 0
    assert calls[0][0] == ("restart", "--time", "5", "--", "web")


def test_stats_default(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers, returns="CPU\n")
    result = runner.invoke(app, ["containers", "stats"])
    assert result.exit_code == 0
    assert calls[0][0] == ("stats", "--no-stream")
    assert calls[0][1]["capture"] is True


def test_stats_json_and_ids(runner: CliRunner, record_calls: RecordCalls) -> None:
    calls = record_calls(containers, returns="{}\n")
    result = runner.invoke(app, ["containers", "stats", "--json", "web", "db"])
    assert result.exit_code == 0
    assert calls[0][0] == ("stats", "--no-stream", "--format", "{{json .}}", "--", "web", "db")


def test_positional_starting_with_dash_is_not_a_flag(
    runner: CliRunner, record_calls: RecordCalls
) -> None:
    # A container literally named "-f" must reach docker as a name, not as --force.
    calls = record_calls(containers)
    result = runner.invoke(app, ["containers", "rm", "--", "-f"])
    assert result.exit_code == 0
    assert calls[0][0] == ("rm", "--", "-f")


def test_restart_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(containers)
    result = runner.invoke(app, ["containers", "restart", "ghost"])
    assert result.exit_code == 1


def test_stats_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(containers)
    result = runner.invoke(app, ["containers", "stats"])
    assert result.exit_code == 1


def test_rm_error_exits_1(runner: CliRunner, docker_fails: DockerFails) -> None:
    docker_fails(containers)
    result = runner.invoke(app, ["containers", "rm", "ghost"])
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "args",
    [
        ["containers", "ls"],
        ["containers", "deploy", "img", "-n", "web", "-p", "8080:80"],
        ["containers", "logs", "web"],
        ["containers", "stop", "web"],
        ["containers", "start", "web"],
        ["containers", "exec", "web", "--", "ls"],
        ["containers", "inspect", "web"],
    ],
)
def test_every_command_error_exits_1(
    runner: CliRunner, docker_fails: DockerFails, args: list[str]
) -> None:
    docker_fails(containers)
    result = runner.invoke(app, args)
    assert result.exit_code == 1
