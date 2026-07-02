## What

<!-- One or two sentences: what does this PR change and why. -->

## Checklist

- [ ] `task lint` passes (compose config, hadolint, shellcheck, ruff, mypy)
- [ ] `task test` passes (pytest, coverage ≥ 90%)
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (skip for docs-only changes)
- [ ] Docs touched if behavior changed (README / CONTRIBUTING / SECURITY)
- [ ] New images/services follow the hardening baseline (read-only, `cap_drop: ALL`, non-root, pinned tags)
