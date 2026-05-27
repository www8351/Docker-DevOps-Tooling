<div align="center">

# 🐳 Docker Labs → Production Tooling

**From 5-year-old interactive bash scripts to a CI/CD-ready Docker toolkit.**

Declarative infrastructure · a typed Python CLI · a single task-runner entrypoint.

[![CI](https://github.com/www8351/Bash/actions/workflows/ci.yml/badge.svg)](https://github.com/www8351/Bash/actions/workflows/ci.yml)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/CLI-Typer-009688)
![Task](https://img.shields.io/badge/Runner-Task-29BEB0?logo=task&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

## 📖 Table of contents

- [Why this exists](#-why-this-exists)
- [Architecture](#-architecture)
- [Project layout](#-project-layout)
- [Requirements](#-requirements)
- [Quick start](#-quick-start)
- [The stack (docker-compose)](#-the-stack-docker-compose)
- [The CLI (dockerctl)](#-the-cli-dockerctl)
- [Task runner](#-task-runner)
- [Continuous integration](#-continuous-integration)
- [Design principles](#-design-principles)
- [Troubleshooting](#-troubleshooting)

---

## 💡 Why this exists

This repo began as a set of **interactive bash menus** written years ago to learn Docker.
They worked at a keyboard, but they were fragile and impossible to automate:

| Old way ❌ | New way ✅ |
|-----------|-----------|
| `while [ "True" ]` menus that prompt for input | declarative config + flag-driven CLI |
| Hardcoded AWS IPs (`3.22.171.145`) | host IP auto-detected / `localhost` |
| Dead images (`abh1nav/dockerui`) | `portainer/portainer-ce` |
| Fragile `docker search \| awk` checks | real `docker` exit codes |
| Nothing runs in CI | linted + validated on every push |

The result is **non-interactive, reproducible, and pipeline-safe**.

---

## 🏗 Architecture

```mermaid
flowchart TD
    Dev([👩‍💻 Engineer / CI]) --> Task[Taskfile.yml<br/>single entrypoint]

    Task --> Compose[docker compose<br/>infrastructure + state]
    Task --> CLI[dockerctl<br/>dynamic ops + logic]

    Compose --> Nginx[nginx<br/>:8080]
    Compose --> Httpd[httpd<br/>:8081]
    Compose --> Portainer[portainer<br/>:9000]
    Compose --> Counter[counter<br/>custom image]

    Nginx -. mounts .-> Web[web/index.html]
    Counter -. builds .-> Img[images/counter/]

    CLI --> Docker[(Docker Engine)]
```

**Separation of concerns** — each tool owns exactly one job:

| Layer | Owns | Tool |
|-------|------|------|
| 🧱 Infrastructure | container lifecycle, networks, volumes, state | `docker-compose` |
| 🐍 Logic | dynamic image/container ops, error handling | Python + Typer |
| ▶️ Orchestration | day-to-day commands | Taskfile |
| 🤖 Quality gate | validation, no humans | GitHub Actions |

---

## 📂 Project layout

```
.
├── compose/
│   ├── docker-compose.yml   # declarative stack (nginx, httpd, portainer, counter)
│   └── .env.example         # ports + image tags  →  copy to .env
├── images/
│   └── counter/             # custom image, built by compose
│       ├── Dockerfile
│       └── counter.sh
├── web/
│   └── index.html           # served by nginx from a read-only mount
├── cli/                     # dockerctl — non-interactive Python CLI
│   ├── pyproject.toml
│   └── dockerctl/
│       ├── __main__.py      # entrypoint + subcommand wiring
│       ├── _docker.py       # typed wrapper around the docker CLI
│       ├── images.py        # pull / rm
│       └── containers.py    # ls / rm / deploy
├── Taskfile.yml             # engineering entrypoint
└── .github/workflows/ci.yml # lint + validate on every push
```

---

## ✅ Requirements

| Tool | Why | Install |
|------|-----|---------|
| Docker Engine + Compose v2 | run the stack | <https://docs.docker.com/get-docker/> |
| Python ≥ 3.10 | run `dockerctl` | <https://www.python.org/> |
| Task (optional) | task runner | <https://taskfile.dev/installation/> |

> Without Task installed, every command has a raw `docker compose` equivalent shown below.

---

## 🚀 Quick start

```bash
# 1. configure ports / image tags
cp compose/.env.example compose/.env

# 2. start everything in the background
task up                 # or: docker compose -f compose/docker-compose.yml up -d

# 3. open the services
#    nginx     → http://localhost:8080
#    httpd     → http://localhost:8081
#    portainer → http://localhost:9000

# 4. tear down
task down               # or: docker compose -f compose/docker-compose.yml down
```

---

## 🧱 The stack (docker-compose)

Defined in [`compose/docker-compose.yml`](compose/docker-compose.yml). Ports and tags come
from `compose/.env` (never hardcoded).

| Service | Image | Default port | Notes |
|---------|-------|--------------|-------|
| `nginx` | `nginx` | `8080:80` | serves `web/` read-only |
| `httpd` | `httpd` | `8081:80` | replaces the old non-existent `apache2` |
| `portainer` | `portainer/portainer-ce` | `9000:9000` | Docker UI, replaces dead `dockerui` |
| `counter` | built from `images/counter/` | — | prints an incrementing counter |

```bash
task build    # docker compose build
task pull     # docker compose pull
task logs     # docker compose logs -f
task clean    # down + remove volumes
```

---

## 🐍 The CLI (dockerctl)

A small **non-interactive** CLI for the dynamic operations compose shouldn't own
(ad-hoc pulls, removals, one-off deploys). Flags only — no prompts — so it is safe in CI.
Every command returns a meaningful **exit code** and writes errors to stderr.

```bash
pip install -e cli            # installs the `dockerctl` command
```

| Command | Replaces | Example |
|---------|----------|---------|
| `images pull <ref>` | `pull_images.sh` | `dockerctl images pull nginx:latest` |
| `images rm <id> [-f]` | `remove_images.sh` | `dockerctl images rm nginx:latest` |
| `containers ls [-a]` | menu listing | `dockerctl containers ls --all` |
| `containers rm <id> [-f]` | `remove_Container.sh` | `dockerctl containers rm web --force` |
| `containers deploy <img>` | deploy menus | `dockerctl containers deploy nginx:latest -n web -p 8080:80` |

```bash
dockerctl --help              # full command tree
dockerctl images --help       # per-group help
```

---

## ▶️ Task runner

[`Taskfile.yml`](Taskfile.yml) is the one entrypoint everyone (and CI) uses.

```bash
task            # list all tasks
task up         # start the stack
task down       # stop + remove
task build      # build images
task pull       # pull images
task logs       # tail logs
task clean      # down + volumes
task lint       # run every linter locally
task cli -- images pull nginx:latest   # proxy to dockerctl
```

---

## 🤖 Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request —
**fully unattended, nothing prompts**:

1. ✅ **Compose** — `docker compose config` validates the stack
2. 🐳 **Dockerfile** — `hadolint` lints `images/counter/Dockerfile`
3. 🐚 **Shell** — `shellcheck` on shell scripts
4. 🐍 **Python** — `ruff` lints the CLI
5. 📦 **CLI** — installs `dockerctl` and runs it to confirm it imports

---

## 🎯 Design principles

- **Declarative over imperative** — compose describes the desired state; we don't script `docker run`.
- **No interactivity** — flags and env vars only, so everything works in a pipeline.
- **Meaningful exit codes** — failures fail loudly and stop CI.
- **One entrypoint** — Taskfile, so nobody memorizes long commands.
- **Right tool per job** — compose for infra, Python for logic, Task to glue, CI to enforce.

---

## 🧰 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `task: command not found` | Install Task, or use the `docker compose …` equivalents above. |
| Port already in use | Change the port in `compose/.env` and re-run `task up`. |
| Page looks unstyled | Hard-refresh; `web/index.html` is mounted live (no rebuild needed). |
| `dockerctl: command not found` | Run `pip install -e cli` first. |
| Permission denied on docker socket | Add your user to the `docker` group, or run with `sudo`. |

---

<div align="center">
<sub>Built as a learning project, refactored into production-grade tooling.</sub>
</div>
