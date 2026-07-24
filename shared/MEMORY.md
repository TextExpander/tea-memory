# Memory Index

One line per memory file: - [Title](file.md), a short hook. No memory content here.

- [Staging DB terminology](staging-db-terminology.md) — "staging db" = the `qa` database on the `Tenet-CI` cluster.
- [Tenet serverless stage names](tenet-serverless-stage-names.md) — rest-proj stages are prod/staging/dev; log groups TENET-<stage>-*; SSM params are SecureString.
- [GrowthBook timeout alert](growthbook-timeout-alert.md) — "surpassed timeout loading features" spike (Jul 2026) is the MSSN-1067 logging change, not capacity.
- [Long output → multiple messages](long-output-multiple-messages.md) — split long findings across Slack messages, don't let it become an auto-attached file.
- [rest-proj error handler default status constant](rest-proj-error-handler-default-status-constant.md) — DEFAULT_ERROR_HTTP_STATUS_CODE = 500 fallback in app.ts:313.
- [rest-proj error handler: log level must key off HTTP status, not error type](rest-proj-error-log-level-fix.md) — 4xx errors (e.g. malformed URI params) must not log at ERROR level; gate on statusCode ≥ 500.
- [mcp-server auth-failure metric definition](mcp-server-auth-failure-metric-definition.md) — CloudWatch log-metric-filter on /ecs/mcp-server audit log; alarm threshold is 10 in 5 min
- [mcp-server OAuth token lifecycle diagnostics](mcp-server-oauth-token-lifecycle-diagnostics.md) — OAuthCoordinator logs redisDegraded, mode, uptimeSec for token validation context
