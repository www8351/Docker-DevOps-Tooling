"""Image subcommands: pull and remove. Replaces pull_images.sh / remove_images.sh."""

from __future__ import annotations

import typer

from ._cli import docker_errors
from ._docker import run

app = typer.Typer(help="Manage Docker images.")


@app.command("ls")
def list_images(
    json_: bool = typer.Option(False, "--json", help="Output one JSON object per line"),
) -> None:
    """List local images."""
    args = ["images"]
    if json_:
        args += ["--format", "{{json .}}"]
    with docker_errors():
        typer.echo(run(*args, capture=True), nl=False)


@app.command()
def build(
    path: str = typer.Argument(..., help="Build context path, e.g. images/counter"),
    tag: str = typer.Option(..., "--tag", "-t", help="Image tag, e.g. counter:latest"),
) -> None:
    """Build an image from a Dockerfile context."""
    with docker_errors():
        run("build", "-t", tag, path)
    typer.echo(f"Built {tag} from {path}")


@app.command()
def pull(name: str = typer.Argument(..., help="Image reference, e.g. nginx:latest")) -> None:
    """Pull an image from a registry."""
    with docker_errors():
        run("pull", name)
    typer.echo(f"OK: pulled {name}")


@app.command()
def tag(
    source: str = typer.Argument(..., help="Source image reference, e.g. counter:ci"),
    target: str = typer.Argument(..., help="Target reference, e.g. ghcr.io/acme/counter:1.0"),
) -> None:
    """Tag an image with a new reference."""
    with docker_errors():
        run("tag", source, target)
    typer.echo(f"Tagged {source} as {target}")


@app.command()
def push(
    name: str = typer.Argument(..., help="Image reference, e.g. ghcr.io/acme/counter:1.0"),
) -> None:
    """Push an image to a registry."""
    with docker_errors():
        run("push", name)
    typer.echo(f"OK: pushed {name}")


@app.command("rm")
def remove(
    image_id: str = typer.Argument(..., help="Image ID or reference to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal"),
) -> None:
    """Remove an image by ID or reference."""
    args = ["rmi"]
    if force:
        args.append("--force")
    args.append(image_id)
    with docker_errors():
        run(*args)
    typer.echo(f"Removed image {image_id}")
