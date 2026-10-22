# 0006. Trivy gates CI on fixable HIGH and CRITICAL findings

- Status: Accepted
- Date: 2026-05-27

## Context

Base images and dependencies collect CVEs over time. A gate that fails on
every finding, including ones with no fix yet, gets switched off.

## Decision

Every image build in CI is scanned with Trivy and fails on HIGH or CRITICAL
findings that have a fix (`ignore-unfixed`). Findings go to code scanning as
SARIF. The publish workflow scans the exact pushed digest on every platform
before any tag moves (see [0013](0013-publish-by-digest.md)).

## Alternatives considered

- **Fail on everything.** Blocks work on findings nobody can act on.
- **Report only.** Nothing forces the base image to move.

## Consequences

A newly published fix for an old CVE can turn CI red without a code change;
the remedy is a base image or dependency bump, usually already proposed by
Dependabot.
