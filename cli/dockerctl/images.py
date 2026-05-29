"""Image subcommands: pull and remove. Replaces pull_images.sh / remove_images.sh."""

from __future__ import annotations

import typer

from ._docker import DockerError, run

app = typer.Typer(help="Manage Docker images.")


@app.command("ls")
def list_images(
    json_: bool = typer.Option(False, "--json", help="Output one JSON object per line"),
) -> None:
    """List local images."""
    args = ["images"]
    if json_:
        args += ["--format", "{{json .}}"]
    try:
        typer.echo(run(*args, capture=True), nl=False)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command()
def build(
    path: str = typer.Argument(..., help="Build context path, e.g. images/counter"),
    tag: str = typer.Option(..., "--tag", "-t", help="Image tag, e.g. counter:latest"),
) -> None:
    """Build an image from a Dockerfile context."""
    try:
        run("build", "-t", tag, path)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Built {tag} from {path}")


@app.command()
def pull(name: str = typer.Argument(..., help="Image reference, e.g. nginx:latest")) -> None:
    """Pull an image from a registry."""
    try:
        run("pull", name)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"OK: pulled {name}")


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
    try:
        run(*args)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Removed image {image_id}")
