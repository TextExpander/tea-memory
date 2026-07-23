---
name: rest-proj-error-handler-default-status-constant
description: DEFAULT_ERROR_HTTP_STATUS_CODE = 500 fallback in app.ts:313.
metadata:
  type: reference
  source: auto-reflection
  learnedBy: sherlock
  learnedAt: 2026-07-23
---

When an error has no explicit statusCode/status, rest-proj defaults to 500. Any handler throwing a bare Error for client-supplied bad input will escalate to 500 unless wrapped in TenetError with 4xx. This is a landmine for future regressions—bare Errors for bad input should always be TenetError(statusCode: 4xx).
