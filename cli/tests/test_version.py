"""Test the top-level version command."""

from __future__ import annotations

from typer.testing import CliRunner

from dockerctl import __version__
from dockerctl.__main__ import app

runner = CliRunner()


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
