# 0013. Publish by digest: scan, sign, then tag

- Status: Accepted
- Date: 2026-10-18

## Context

The old pipeline built, scanned a local image, then pushed tags. What was
scanned and what was tagged were not provably the same bytes, and a failed
step could leave `latest` half updated.

## Decision

One reusable workflow, [`_publish.yml`](../../.github/workflows/_publish.yml),
serves both `main` and releases. It pushes the multi-arch image by digest
only, scans that digest on every platform with Trivy, signs it with cosign
(keyless, GitHub OIDC), then points the tags at it with
`docker buildx imagetools create` and fails unless every tag resolves to the
signed digest. Releases first run the full CI suite on the tagged commit;
tags with a prerelease part never move `latest`. On pull requests a dry run
does the same against a throwaway local registry.

## Alternatives considered

- **Tag on push.** Simple, but tags move before the scan.
- **Separate workflows for main and releases.** They drift.

## Consequences

A tag on GHCR always names a scanned, signed digest. Publishing takes longer,
and the dry run adds a few minutes to every pull request.
