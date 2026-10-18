# 0005. Pin every GitHub Action to a full commit SHA

- Status: Accepted
- Date: 2026-07-02

## Context

A tag on a third-party action can be moved to different code at any time,
and a compromised action runs with the workflow's token.

## Decision

Every `uses:` line names a full 40-character commit SHA with the version as
a comment. Workflows default to `contents: read` and escalate per job;
checkouts do not keep their token; every job has a timeout. actionlint and
zizmor lint the workflows in CI, zizmor including its online checks for
impostor or known-vulnerable commits. Dependabot proposes SHA bumps, waiting
seven days after a release.

## Alternatives considered

- **Major version tags (`@v4`).** Convenient, but they move.

## Consequences

Updates arrive as Dependabot pull requests rather than silently. Reading
which version runs needs the trailing comment, which reviewers must keep
accurate.
