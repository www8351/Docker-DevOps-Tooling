# 0007. No image bakes in engine access; socket holders are explicit

- Status: Accepted
- Date: 2026-07-02

## Context

Access to `/var/run/docker.sock` is root on the host. It tends to spread:
monitoring, tooling and UIs all ask for it.

## Decision

No image grants itself engine access. The stack has exactly one socket
holder by default, Portainer, alone on the `mgmt` network, because a Docker
management UI needs the engine. `dockerctl` gets the socket only when an
operator mounts it, and then runs non-root with the socket's group added.
[SECURITY.md](../../SECURITY.md) lists every holder.

## Alternatives considered

- **A socket proxy for every consumer.** Worth it only where a consumer can
  live with a narrow API; Portainer cannot, and cAdvisor turned out to need
  more than the socket (see [0008](0008-cadvisor-without-engine-sockets.md)).

## Consequences

Adding a new socket holder is a visible change to compose and to
SECURITY.md, never a side effect of an image.
