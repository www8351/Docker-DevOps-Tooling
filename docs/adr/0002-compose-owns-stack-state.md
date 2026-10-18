# 0002. Compose owns the stack's state

- Status: Accepted
- Date: 2026-05-27

## Context

The project started as interactive bash menus that ran `docker run` with
hand-built flags, hardcoded hosts and images that no longer existed. The
running state lived only in whatever the last menu choice had created, so it
could not be reviewed, diffed or tested.

## Decision

[`compose/docker-compose.yml`](../../compose/docker-compose.yml) is the single
declarative description of the long-running stack: images, ports, networks,
healthchecks, limits and hardening. The [Taskfile](../../Taskfile.yml) wraps
it for humans, and CI boots exactly that file with `docker compose up --wait`,
so every healthcheck is a test. Dynamic, one-off operations go to the CLI
(see [0003](0003-typed-non-interactive-cli.md)).

## Alternatives considered

- **Keep the scripts and harden them.** Imperative scripts still cannot be
  validated before they run, and every change would need a new prompt path.
- **Kubernetes manifests only.** Too heavy as the default for a single host;
  a chart now exists alongside compose instead (see
  [0014](0014-helm-chart-restricted-pss.md)).

## Consequences

`docker compose config` validates the stack offline, and the whole stack is
reviewable in one file. Behaviour that compose cannot express (one-off
deploys, image housekeeping) needs the CLI rather than a script.
