# 0010. Admin passwords come from generated file secrets, never defaults

- Status: Accepted
- Date: 2026-10-18

## Context

Grafana shipped with `admin:admin`, and Portainer's first-run page let
whoever reached it first create the admin account.

## Decision

[`scripts/gen-secrets.sh`](../../scripts/gen-secrets.sh) writes random
passwords to the gitignored `compose/secrets/`. Compose passes them as file
secrets: Grafana reads `GF_SECURITY_ADMIN_PASSWORD__FILE`, Portainer
`--admin-password-file`. There is no default anywhere, so a missing file
stops `up`. CI proves the stack refuses to start without the files, that the
generated Grafana password works and `admin:admin` gets 401, and that
Portainer issues a token for the generated password.

## Alternatives considered

- **Passwords in `.env`.** Easy to commit by accident and visible in
  `docker inspect`.
- **Document changing the default.** Defaults are rarely changed.

## Consequences

`task secrets` (or the script) must run before the first `up`. Both apps
read the secret only when their data volume is created, so rotating it on
an existing volume is a manual reset.
