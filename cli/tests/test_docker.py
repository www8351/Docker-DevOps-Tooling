"""Unit tests for the docker subprocess wrapper (_docker.run)."""

from __future__ import annotations

import subprocess

import pytest

from dockerctl import _docker
from dockerctl._docker import DockerError, run


def test_missing_docker_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_docker.shutil, "which", lambda _: None)
    with pytest.raises(DockerError, match="docker CLI not found"):
        run("ps")


def test_success_streaming(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_docker.shutil, "which", lambda _: "/usr/bin/docker")

    def fake_run(cmd, **kwargs):
        assert cmd == ["/usr/bin/docker", "pull", "nginx"]
        assert kwargs["capture_output"] is False
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(_docker.subprocess, "run", fake_run)
    assert run("pull", "nginx") == ""


def test_success_capture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_docker.shutil, "which", lambda _: "/usr/bin/docker")

    def fake_run(cmd, **kwargs):
        assert kwargs["capture_output"] is True
        return subprocess.CompletedProcess(cmd, 0, stdout="CONTAINER ID\n", stderr="")

    monkeypatch.setattr(_docker.subprocess, "run", fake_run)
    assert run("ps", capture=True) == "CONTAINER ID\n"


def test_failure_surfaces_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_docker.shutil, "which", lambda _: "/usr/bin/docker")

    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(1, cmd, stderr="no such image")

    monkeypatch.setattr(_docker.subprocess, "run", fake_run)
    with pytest.raises(DockerError, match="no such image"):
        run("pull", "bogus")


def test_failure_without_stderr_uses_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_docker.shutil, "which", lambda _: "/usr/bin/docker")

    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(7, cmd, stderr="")

    monkeypatch.setattr(_docker.subprocess, "run", fake_run)
    with pytest.raises(DockerError, match="exit code 7"):
        run("rm", "x")
