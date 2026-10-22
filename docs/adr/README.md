# Architecture decision records

Why the project is built the way it is. Each record states the context, the
decision, the options that lost, and the consequences. New decisions start
from [`template.md`](template.md) and take the next number; a decision that
replaces an older one adds a new record and marks the old one superseded.

| # | Decision | Status |
|---|----------|--------|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-compose-owns-stack-state.md) | Compose owns the stack's state | Accepted |
| [0003](0003-typed-non-interactive-cli.md) | A typed, non-interactive CLI wraps the docker CLI | Accepted |
| [0004](0004-multi-stage-alpine-non-root-images.md) | Images are multi-stage, Alpine based and run as a fixed non-root user | Accepted |
| [0005](0005-pin-actions-to-commit-shas.md) | Pin every GitHub Action to a full commit SHA | Accepted |
| [0006](0006-trivy-gates-fixable-high-critical.md) | Trivy gates CI on fixable HIGH and CRITICAL findings | Accepted |
| [0007](0007-explicit-engine-socket-holders.md) | No image bakes in engine access; socket holders are explicit | Accepted |
| [0008](0008-cadvisor-without-engine-sockets.md) | cAdvisor reads /sys only and holds no engine socket | Accepted |
| [0009](0009-loopback-bind-by-default.md) | Published ports bind to loopback by default | Accepted |
| [0010](0010-admin-passwords-from-file-secrets.md) | Admin passwords come from generated file secrets, never defaults | Accepted |
| [0011](0011-lock-python-dependencies-with-uv.md) | Lock Python dependencies with uv | Accepted |
| [0012](0012-unprivileged-web-servers.md) | Web servers run unprivileged on port 8080 | Accepted |
| [0013](0013-publish-by-digest.md) | Publish by digest: scan, sign, then tag | Accepted |
| [0014](0014-helm-chart-restricted-pss.md) | A Helm chart for the web tier, admitted under the restricted Pod Security Standard | Accepted |
