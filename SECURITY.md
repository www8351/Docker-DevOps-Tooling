# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| latest 0.x release | ✅ |
| anything older | ❌ |

## Reporting a vulnerability

Please use
[GitHub private vulnerability reporting](https://github.com/www8351/Docker-DevOps-Tooling/security/advisories/new)
on this repository. Do not open a public issue for security reports.

## Scope

- The two published container images
  (`ghcr.io/www8351/docker-devops-tooling/{counter,dockerctl}`)
- The `dockerctl` Python CLI
- The compose stack definition and GitHub Actions workflows

## Verifying image signatures

Published images are signed with [cosign](https://github.com/sigstore/cosign)
keyless signing (GitHub Actions OIDC) and ship BuildKit provenance + SBOM
attestations:

```bash
cosign verify \
  --certificate-identity-regexp 'https://github.com/www8351/Docker-DevOps-Tooling/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/www8351/docker-devops-tooling/dockerctl:latest
```

## Existing posture

- Multi-stage images on minimal Alpine bases, running as a fixed non-root
  user (UID/GID 10001); build toolchains never reach runtime stages.
- Trivy scans gate CI on fixable HIGH/CRITICAL findings; a CycloneDX SBOM is
  generated for every image build, and pushed images carry BuildKit
  provenance (`mode=max`) and SBOM attestations, signed with cosign.
- Images are published multi-arch (linux/amd64, linux/arm64).
- CI boots the full hardened stack on every push — healthchecks and live
  endpoint probes gate the merge.
- Compose services run read-only with all capabilities dropped (httpd
  re-adds the four it needs to bind port 80 and switch to its worker user),
  bounded logging, resource limits, and `no-new-privileges`.
- Published ports bind to `127.0.0.1` unless `WEB_BIND_ADDR` /
  `ADMIN_BIND_ADDR` say otherwise.
- Portainer and Grafana admin passwords come from generated secret files
  (`scripts/gen-secrets.sh`, gitignored `compose/secrets/`). There is no
  default password; a missing file stops the service from starting. Both
  apps read the secret only when their data volume is first created, so
  an existing volume keeps its old password until you reset it.
- Networks are split by role: `web` (nginx, httpd), internal
  `nginx-status`, `metrics` (prometheus, grafana, cadvisor, exporter) and
  `mgmt` (portainer). counter and dockerctl run without a network.
- Services that still run as root inside their container: httpd's master
  process, Portainer, and cAdvisor (with no capabilities and only `/sys`
  mounted read-only). Everything else runs as a fixed non-root user.
- All GitHub Actions are pinned to full commit SHAs and run under
  least-privilege workflow permissions.

## Known design decision, not a vulnerability

Engine socket holders, by design:

| Holder | Access | Why |
|--------|--------|-----|
| Portainer | `/var/run/docker.sock`, read-write | a Docker management UI drives the engine |
| `dockerctl` (only when you mount it) | `/var/run/docker.sock`, read-write | the CLI drives the engine |

Socket access is root-equivalent on the host. Do not expose Portainer
publicly (keep `ADMIN_BIND_ADDR` on loopback or behind your own auth), and
only mount the socket into `dockerctl` when you intend it to drive the
engine.

cAdvisor deliberately holds **no** engine socket. Its Docker integration
needs both docker.sock and the containerd socket, and neither can be
narrowed to read-only. It reads the host cgroup tree from `/sys` instead,
which means containers appear by id rather than by name and per-container
network counters are not collected.
