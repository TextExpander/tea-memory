# Memory Index

One line per memory file: - [Title](file.md), a short hook. No memory content here.

- [Staging DB terminology](staging-db-terminology.md) — "staging db" = the `qa` database on the `Tenet-CI` cluster.
- [Tenet serverless stage names](tenet-serverless-stage-names.md) — rest-proj stages are prod/staging/dev; log groups TENET-<stage>-*; SSM params are SecureString.
- [GrowthBook timeout alert](growthbook-timeout-alert.md) — "surpassed timeout loading features" spike (Jul 2026) is the MSSN-1067 logging change, not capacity.
- [Long output → multiple messages](long-output-multiple-messages.md) — split long findings across Slack messages, don't let it become an auto-attached file.
- [Express decodeURIComponent malformed UTF-8 handling in tenet/rest-proj](express-decodeuricomponent-malformed-utf-8-handling-in-tenet.md) — Invalid percent-sequences like %c0 in route params cause URIError → 400 logged as ERROR-level noise.
- [Log level should key off HTTP status, not error type](log-level-should-key-off-http-status-not-error-type.md) — Gate error-level logs by status code (≥500), not by instanceof TenetError.
- [rest-proj error handler default status constant](rest-proj-error-handler-default-status-constant.md) — DEFAULT_ERROR_HTTP_STATUS_CODE = 500 fallback in app.ts:313.
