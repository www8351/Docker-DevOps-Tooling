"""Test the top-level version command and --version/-V flags."""

from __future__ import annotations

from typer.testing import CliRunner

from dockerctl import __version__
from dockerctl.__main__ import app

runner = CliRunner()


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_version_short_flag() -> None:
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_no_args_prints_help() -> None:
    result = runner.invoke(app, [])
    assert "Usage" in result.stdout
