# 0008. cAdvisor reads /sys only and holds no engine socket

- Status: Accepted
- Date: 2026-10-18

## Context

cAdvisor used to mount `/var/run` and so held the Docker socket. A GET-only
Docker API proxy looked like the fix, but cAdvisor v0.55.1 registers its
Docker integration only when it has both docker.sock and a containerd
client (`container/docker/factory.go` creates the containerd client
unconditionally). The containerd API is root-equivalent and no proxy can
narrow it.

## Decision

cAdvisor mounts only `/sys` read-only, runs with `cgroup: host`, drops every
capability and holds no engine socket
([compose](../../compose/docker-compose.yml)). Prometheus derives a short
`container_id` label from each series' cgroup path, and the Grafana
dashboard labels containers by that id. CI asserts that `/sys` is
cAdvisor's only mount and that the nginx container still has memory series.

## Alternatives considered

- **GET-only Docker proxy plus the raw containerd socket.** The containerd
  socket is still root-equivalent, so nothing is gained.
- **Keep the `/var/run` mount and document it.** Leaves a root-equivalent
  holder in the observability profile.

## Consequences

Containers appear by short id, not by name, and per-container network
counters are not collected (the dashboard shows nginx requests per second
instead). Moving off cgroup-path parsing would need a new record.
