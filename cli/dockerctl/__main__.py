"""dockerctl entrypoint: wires the image, container and compose command groups together."""

from __future__ import annotations

import typer

from . import __version__, compose, containers, images

app = typer.Typer(
    help="Non-interactive Docker helper for CI/CD pipelines.",
    no_args_is_help=True,
)
app.add_typer(images.app, name="images")
app.add_typer(containers.app, name="containers")
app.add_typer(compose.app, name="compose")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Print the dockerctl version and exit.",
    ),
) -> None:
    """Non-interactive Docker helper for CI/CD pipelines."""


@app.command()
def version() -> None:
    """Print the dockerctl version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
