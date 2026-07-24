---
name: rest-proj-error-log-level-fix
description: 4xx errors (e.g. malformed URI params) must not log at ERROR level; gate on statusCode ≥ 500.
metadata:
  type: reference
  source: curation
  curatedAt: 2026-07-24
---

**Problem**
Express's router calls `decodeURIComponent()` on route params (e.g. `/:id` in `/share/:id`). Malformed UTF-8 percent-sequences like `%c0` throw `URIError`, which Express catches and tags as 400. The error handler in `rest-proj/app/app.ts:300–301` logs *all* non-TenetError Errors at `log.error()` regardless of statusCode, and `Sentry.expressErrorHandler()` (line 285) captures them before status filtering. This causes benign 400 client errors to surface as ERROR-level alerts.

**Team-agreed principle** (Hernán + Scott Jeide, 2026-07-23): any user/client-provided bad data to an API call should NOT be logged at error level and should return a 4xx (not 5xx). This applies generally across rest-proj.

**Fix**
- Key log level off resolved statusCode: log 4xx at info/warn, reserve `log.error` for `statusCode >= 500`. This ensures 4xx TenetErrors and 4xx plain Errors are treated identically.
- Apply same gate to Sentry: `shouldHandleError: (err) => ((err.status ?? err.statusCode ?? 500) >= 500)`.

**Related landmine** (`app.ts:313`): `DEFAULT_ERROR_HTTP_STATUS_CODE = 500` — bare Errors with no explicit statusCode default to 500. Any handler throwing a bare Error for client-supplied bad input will escalate to 500 unless wrapped in `TenetError` with a 4xx. Future handlers must always use `TenetError(statusCode: 4xx)` for client errors.
