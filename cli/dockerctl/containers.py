"""Container subcommands: list, remove, deploy.

Replaces remove_Container.sh and the deploy branches of the old menu scripts.
All non-interactive: arguments and flags only, so it is safe to call from CI.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ._docker import DockerError, run

app = typer.Typer(help="Manage Docker containers.")


@app.command("ls")
def list_containers(
    all_: bool = typer.Option(False, "--all", "-a", help="Include stopped containers"),
    json_: bool = typer.Option(False, "--json", help="Output one JSON object per line"),
) -> None:
    """List containers (running, or all with --all)."""
    args = ["ps"]
    if all_:
        args.append("-a")
    if json_:
        args += ["--format", "{{json .}}"]
    try:
        typer.echo(run(*args, capture=True), nl=False)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command("rm")
def remove(
    container_id: str = typer.Argument(..., help="Container ID or name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal of a running container"),
) -> None:
    """Remove a container by ID or name."""
    args = ["rm"]
    if force:
        args.append("--force")
    args.append(container_id)
    try:
        run(*args)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Removed container {container_id}")


@app.command()
def deploy(
    image: str = typer.Argument(..., help="Image to run, e.g. nginx:latest"),
    name: str = typer.Option(..., "--name", "-n", help="Container name"),
    port: str = typer.Option(..., "--port", "-p", help="Port mapping host:container, e.g. 8080:80"),
) -> None:
    """Run a detached container with a name and port mapping."""
    try:
        run("run", "-d", "--name", name, "-p", port, image)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Deployed {name} from {image} on {port}")


@app.command()
def logs(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Stream new log output"),
    tail: str = typer.Option("all", "--tail", help="Number of trailing lines (or 'all')"),
) -> None:
    """Show logs for a container."""
    args = ["logs", "--tail", tail]
    if follow:
        args.append("--follow")
    args.append(container_id)
    try:
        run(*args)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command()
def stop(container_id: str = typer.Argument(..., help="Container ID or name")) -> None:
    """Stop a running container."""
    try:
        run("stop", container_id)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Stopped {container_id}")


@app.command()
def start(container_id: str = typer.Argument(..., help="Container ID or name")) -> None:
    """Start a stopped container."""
    try:
        run("start", container_id)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"Started {container_id}")


@app.command("exec")
def exec_(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    command: Annotated[list[str], typer.Argument(help="Command to run inside the container")] = ...,
) -> None:
    """Run a command inside a running container (non-interactive)."""
    try:
        run("exec", container_id, *command)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command()
def inspect(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    json_: bool = typer.Option(False, "--json", help="Output the raw JSON object"),
) -> None:
    """Show low-level details for a container."""
    args = ["inspect"]
    if json_:
        args += ["--format", "{{json .}}"]
    args.append(container_id)
    try:
        typer.echo(run(*args, capture=True), nl=False)
    except DockerError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
