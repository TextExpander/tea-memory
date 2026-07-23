---
name: log-level-should-key-off-http-status-not-error-type
description: Gate error-level logs by status code (≥500), not by instanceof TenetError.
metadata:
  type: feedback
  source: auto-reflection
  learnedBy: sherlock
  learnedAt: 2026-07-23
---

In rest-proj error middleware (app.ts:298-304), currently logs non-TenetError as ERROR regardless of status. Better approach: key off resolved status—log 4xx at info/warn, reserve log.error for statusCode >= 500. This ensures 4xx TenetErrors and 4xx plain Errors are treated identically, while genuine 500s still alert. Also apply to Sentry guard: shouldHandleError: (err) => ((err.status ?? err.statusCode ?? 500) >= 500).
