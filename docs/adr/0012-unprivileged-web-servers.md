# 0012. Web servers run unprivileged on port 8080

- Status: Accepted
- Date: 2026-10-18

## Context

nginx and httpd ran their master process as root and re-added CHOWN, SETGID,
SETUID and NET_BIND_SERVICE so they could bind port 80 and switch to a
worker user. That is four capabilities and a root process for a static site.

## Decision

nginx runs `nginxinc/nginx-unprivileged` (UID 101). httpd runs the official
`httpd` Alpine image as `www-data` (UID 82) with a minimal
[`httpd.conf`](../../compose/httpd/httpd.conf): it listens on 8080 and keeps
its pid and mutexes in `/tmp`. Both listen on 8080, run read-only with every
capability dropped and nothing added back. The host ports (8080, 8081) did
not change. The Helm chart runs the same images and the same `httpd.conf`.

## Alternatives considered

- **Keep port 80 inside the container.** Needs NET_BIND_SERVICE, or a
  per-container sysctl that compose and the chart would both have to carry.
- **Build custom images.** More to maintain and scan; both upstream images
  already support this.

## Consequences

Nothing in the web tier runs as root. The httpd configuration is now ours to
maintain; CI fails if the compose and chart copies differ.
