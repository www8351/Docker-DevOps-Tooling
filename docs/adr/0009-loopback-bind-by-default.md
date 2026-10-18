# 0009. Published ports bind to loopback by default

- Status: Accepted
- Date: 2026-10-18

## Context

Every published port used to listen on all interfaces, which put Portainer,
Grafana and Prometheus on the local network of any machine that ran the
stack.

## Decision

Every published port in compose binds to `${WEB_BIND_ADDR:-127.0.0.1}`
(nginx, httpd) or `${ADMIN_BIND_ADDR:-127.0.0.1}` (Portainer, Prometheus,
Grafana), so the web tier and the admin tier are opened separately. The CI
`lint` job renders the compose file with every profile and fails if any
published port is off loopback. `dockerctl containers deploy` follows the
same rule for its `--port` mapping unless an address is given.

## Alternatives considered

- **One bind variable for everything.** Opening the web tier would also
  expose the admin UIs.
- **Leave all interfaces and document a firewall.** Unsafe by default.

## Consequences

Reaching the stack from another machine is an explicit edit of
`compose/.env`. Anyone who relied on LAN access sees a breaking change.
