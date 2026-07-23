---
name: express-decodeuricomponent-malformed-utf-8-handling-in-tenet
description: Invalid percent-sequences like %c0 in route params cause URIError → 400 logged as ERROR-level noise.
metadata:
  type: reference
  source: auto-reflection
  learnedBy: sherlock
  learnedAt: 2026-07-23
---

Express's router calls decodeURIComponent() on route params (e.g. /:id in /share/:id). Malformed UTF-8 percent-sequences like %c0 throw URIError, which Express catches and tags as 400. However, the error handler in rest-proj/app/app.ts:300–301 logs *all* non-TenetError Errors at log.error() regardless of statusCode, and Sentry.expressErrorHandler() (line 285) captures them before status filtering. This causes benign 400 client errors to surface as ERROR-level alerts. Fix: gate log level on statusCode >= 500, and use Sentry's shouldHandleError option to exclude 4xx.
