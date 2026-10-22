# 0014. A Helm chart for the web tier, admitted under the restricted Pod Security Standard

- Status: Accepted
- Date: 2026-10-18

## Context

The stack ran only under compose. Kubernetes users had nothing, and a chart
that only renders proves little: the hardening has to survive admission and
real networking.

## Decision

[`deploy/chart`](../../deploy/chart) deploys nginx, httpd and counter. Every
pod runs as its image's fixed non-root user with seccomp `RuntimeDefault`, a
read-only root filesystem, no privilege escalation, every capability dropped
and an in-memory `/tmp`; the service account mounts no token; NetworkPolicies
deny everything except HTTP on 8080 into the web servers. nginx and httpd
use the same tag and digest as compose, and httpd the same `httpd.conf`.
CI installs the chart on kind in a namespace that enforces the restricted
profile (after proving a bare pod is refused), runs `helm test`, and proves
the NetworkPolicy blocks pod to pod traffic it does not allow. The web
servers are not part of the observability or management tiers, which stay
compose only.

## Alternatives considered

- **Plain manifests or Kustomize.** No values schema and no `helm test`.
- **Port the whole stack.** Portainer and cAdvisor need host access that
  the restricted profile forbids, by design.

## Consequences

A Dependabot bump of nginx or httpd in compose fails CI until the chart's
values carry the same reference. The chart's default counter tag is its
`appVersion`, so a release must publish that tag.
