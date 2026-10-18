# 0001. Record architecture decisions

- Status: Accepted
- Date: 2026-10-18

## Context

The project's hardening choices (which images run as which user, who holds
the engine socket, why a port binds where it does) were spread across
compose comments, the changelog and pull request descriptions. A reader who
wants to know why something is the way it is, or whether a change would
undo a deliberate trade-off, has to dig through history.

## Decision

Keep one short record per significant decision in `docs/adr/`, numbered in
order and written from [`template.md`](template.md), in the shape popularised
by Michael Nygard and MADR: context, decision, alternatives, consequences.
Records describe decisions already in force when they were backfilled;
later changes add a new record that supersedes the old one instead of
editing it.

## Alternatives considered

- **Comments in the code only.** They explain the local setting but not the
  options that were rejected, and they scatter one decision over several
  files (compose, the chart, CI).
- **A wiki.** It drifts away from the code it describes and is not reviewed
  with the change.

## Consequences

A pull request that reverses a recorded decision should add a record saying
so. The index in [`README.md`](README.md) lists every record.
