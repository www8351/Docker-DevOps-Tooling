"""Stack lifecycle subcommands: up, down, ps, wrapping `docker compose`.

The compose file defaults to compose/docker-compose.yml relative to the
working directory (the repository root); point elsewhere with --file or the
DOCKERCTL_COMPOSE_FILE environment variable. Needs the docker compose plugin,
which the dockerctl image does not ship: inside the image these commands fail
with docker's own usage error (docker-cli 29 reports "unknown shorthand flag:
'f' in -f") and exit 1.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ._cli import docker_errors
from ._docker import run

app = typer.Typer(help="Manage the compose stack (wraps `docker compose`).")

DEFAULT_FILE = "compose/docker-compose.yml"

FileOption = Annotated[
    str,
    typer.Option(
        "--file",
        "-f",
        envvar="DOCKERCTL_COMPOSE_FILE",
        help="Compose file",
    ),
]
ProfileOption = Annotated[
    list[str] | None,
    typer.Option("--profile", help="Enable a compose profile (repeatable)"),
]


def _compose(file: str, profiles: list[str] | None) -> list[str]:
    args = ["compose", "-f", file]
    for profile in profiles or []:
        args += ["--profile", profile]
    return args


@app.command()
def up(
    services: Annotated[
        list[str] | None, typer.Argument(help="Services to start (default: all enabled)")
    ] = None,
    file: FileOption = DEFAULT_FILE,
    profile: ProfileOption = None,
    wait: bool = typer.Option(
        True, "--wait/--no-wait", help="Block until every healthcheck passes"
    ),
    wait_timeout: int = typer.Option(180, "--wait-timeout", help="Seconds to wait for health"),
) -> None:
    """Start the stack in the background, waiting for it to be healthy."""
    args = [*_compose(file, profile), "up", "-d"]
    if wait:
        args += ["--wait", "--wait-timeout", str(wait_timeout)]
    if services:
        args += ["--", *services]
    with docker_errors():
        run(*args)
    typer.echo("Stack is up")


@app.command()
def down(
    file: FileOption = DEFAULT_FILE,
    profile: ProfileOption = None,
    volumes: bool = typer.Option(False, "--volumes", "-v", help="Also remove named volumes"),
) -> None:
    """Stop the stack and remove its containers (and volumes with --volumes)."""
    args = [*_compose(file, profile), "down"]
    if volumes:
        args.append("--volumes")
    with docker_errors():
        run(*args)
    typer.echo("Stack is down")


@app.command()
def ps(
    file: FileOption = DEFAULT_FILE,
    profile: ProfileOption = None,
    all_: bool = typer.Option(False, "--all", "-a", help="Include stopped containers"),
    json_: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    """List the stack's containers."""
    args = [*_compose(file, profile), "ps"]
    if all_:
        args.append("--all")
    if json_:
        args += ["--format", "json"]
    with docker_errors():
        typer.echo(run(*args, capture=True), nl=False)
