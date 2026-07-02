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

## Existing posture

- Multi-stage images on minimal Alpine bases, running as a fixed non-root
  user (UID/GID 10001); build toolchains never reach runtime stages.
- Trivy scans gate CI on fixable HIGH/CRITICAL findings; a CycloneDX SBOM is
  generated for every image build.
- Compose services run read-only with all capabilities dropped, bounded
  logging, resource limits, and `no-new-privileges`; docker.sock consumers
  are isolated on their own network tier.
- All GitHub Actions are pinned to full commit SHAs and run under
  least-privilege workflow permissions.

## Known design decision, not a vulnerability

Portainer (and `dockerctl` when you mount the socket) has read-write access
to `/var/run/docker.sock`. Socket access is root-equivalent on the host by
design — that is what a Docker management UI is for. Do not expose Portainer
publicly without authentication, and only mount the socket into `dockerctl`
when you intend it to drive the engine.
