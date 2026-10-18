"""Container subcommands: list, remove, deploy.

Replaces remove_Container.sh and the deploy branches of the old menu scripts.
All non-interactive: arguments and flags only, so it is safe to call from CI.

Every docker call ends option parsing with `--` before the positional
arguments, so a name or reference that starts with a dash is never read as a
docker flag.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ._cli import docker_errors
from ._docker import run

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
    with docker_errors():
        typer.echo(run(*args, capture=True), nl=False)


@app.command("rm")
def remove(
    container_id: str = typer.Argument(..., help="Container ID or name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal of a running container"),
) -> None:
    """Remove a container by ID or name."""
    args = ["rm"]
    if force:
        args.append("--force")
    args += ["--", container_id]
    with docker_errors():
        run(*args)
    typer.echo(f"Removed container {container_id}")


def _loopback(port: str) -> str:
    """Bind a port mapping to 127.0.0.1 unless it already names a host address.

    "8080:80" -> "127.0.0.1:8080:80", "80" -> "127.0.0.1::80" (random host
    port); an empty address as in ":8080:80" or "::80" also gets 127.0.0.1.
    "0.0.0.0:8080:80" and "[::1]:8080:80" are left as given.
    """
    if port.startswith(":"):
        return f"127.0.0.1{port}"
    if port.startswith("[") or port.count(":") >= 2:
        return port
    if ":" in port:
        return f"127.0.0.1:{port}"
    return f"127.0.0.1::{port}"


@app.command()
def deploy(
    image: str = typer.Argument(..., help="Image to run, e.g. nginx:latest"),
    name: str = typer.Option(..., "--name", "-n", help="Container name"),
    port: str = typer.Option(
        ...,
        "--port",
        "-p",
        help="Port mapping host:container, e.g. 8080:80 (bound to 127.0.0.1 unless "
        "an address is given or --no-harden is set)",
    ),
    cap_add: Annotated[
        list[str] | None,
        typer.Option("--cap-add", help="Capability to add back after dropping all (repeatable)"),
    ] = None,
    tmpfs: Annotated[
        list[str] | None,
        typer.Option(
            "--tmpfs",
            help="Extra writable tmpfs path; /tmp is one unless given here with options "
            "(repeatable)",
        ),
    ] = None,
    writable: bool = typer.Option(
        False, "--writable", help="Keep the root filesystem writable instead of read-only"
    ),
    user: str | None = typer.Option(None, "--user", help="Run as UID[:GID]"),
    memory: str | None = typer.Option(None, "--memory", help="Memory limit (default 256m)"),
    pids_limit: int | None = typer.Option(
        None, "--pids-limit", help="Maximum number of processes (default 256)"
    ),
    no_harden: bool = typer.Option(
        False,
        "--no-harden",
        help="Plain `docker run -d` with only --name, --port and --user applied; "
        "the hardening options above are rejected",
    ),
) -> None:
    """Run a detached container, hardened by default.

    By default the container gets no-new-privileges, all capabilities dropped,
    a read-only root filesystem with /tmp on tmpfs, process and memory limits,
    and its port published on 127.0.0.1 only. Each default has an escape
    hatch; --no-harden turns them all off and refuses the hardening options,
    so a flag is never silently ignored.
    """
    if no_harden:
        given = {
            "--cap-add": bool(cap_add),
            "--tmpfs": bool(tmpfs),
            "--writable": writable,
            "--memory": memory is not None,
            "--pids-limit": pids_limit is not None,
        }
        clash = [flag for flag, set_ in given.items() if set_]
        if clash:
            raise typer.BadParameter(
                f"cannot be combined with {', '.join(clash)}", param_hint="'--no-harden'"
            )
    args = ["run", "-d", "--name", name]
    published = port
    if not no_harden:
        published = _loopback(port)
        args += ["--security-opt", "no-new-privileges:true", "--cap-drop", "ALL"]
        for cap in cap_add or []:
            args += ["--cap-add", cap]
        if not writable:
            args.append("--read-only")
        paths = tmpfs or []
        if all(path.split(":", 1)[0] != "/tmp" for path in paths):
            paths = ["/tmp", *paths]
        for path in paths:
            args += ["--tmpfs", path]
        args += [
            "--pids-limit",
            str(256 if pids_limit is None else pids_limit),
            "--memory",
            memory or "256m",
        ]
    if user:
        args += ["--user", user]
    args += ["-p", published, "--", image]
    with docker_errors():
        run(*args)
    typer.echo(f"Deployed {name} from {image} on {published}")


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
    args += ["--", container_id]
    with docker_errors():
        run(*args)


@app.command()
def stop(container_id: str = typer.Argument(..., help="Container ID or name")) -> None:
    """Stop a running container."""
    with docker_errors():
        run("stop", "--", container_id)
    typer.echo(f"Stopped {container_id}")


@app.command()
def start(container_id: str = typer.Argument(..., help="Container ID or name")) -> None:
    """Start a stopped container."""
    with docker_errors():
        run("start", "--", container_id)
    typer.echo(f"Started {container_id}")


@app.command("exec")
def exec_(
    container_id: Annotated[str, typer.Argument(help="Container ID or name")],
    command: Annotated[list[str], typer.Argument(help="Command to run inside the container")],
) -> None:
    """Run a command inside a running container (non-interactive)."""
    with docker_errors():
        run("exec", "--", container_id, *command)


@app.command()
def restart(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    time: int | None = typer.Option(
        None, "--time", "-t", help="Seconds to wait for stop before killing"
    ),
) -> None:
    """Restart a container."""
    args = ["restart"]
    if time is not None:
        args += ["--time", str(time)]
    args += ["--", container_id]
    with docker_errors():
        run(*args)
    typer.echo(f"Restarted {container_id}")


@app.command()
def stats(
    container_ids: Annotated[
        list[str] | None, typer.Argument(help="Container IDs or names (default: all running)")
    ] = None,
    json_: bool = typer.Option(False, "--json", help="Output one JSON object per line"),
) -> None:
    """Show a one-shot resource usage snapshot (always --no-stream: CI-safe)."""
    args = ["stats", "--no-stream"]
    if json_:
        args += ["--format", "{{json .}}"]
    if container_ids:
        args += ["--", *container_ids]
    with docker_errors():
        typer.echo(run(*args, capture=True), nl=False)


@app.command()
def inspect(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    json_: bool = typer.Option(False, "--json", help="Output the raw JSON object"),
) -> None:
    """Show low-level details for a container."""
    args = ["inspect"]
    if json_:
        args += ["--format", "{{json .}}"]
    args += ["--", container_id]
    with docker_errors():
        typer.echo(run(*args, capture=True), nl=False)
