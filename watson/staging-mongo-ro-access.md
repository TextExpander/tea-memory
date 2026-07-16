---
name: staging-mongo-ro-access
description: MONGO_RO_URI RO user was not authorized on the qa DB (observed 2026-07-16)
metadata:
  type: reference
---

On 2026-07-16 the `mongosh "$MONGO_RO_URI"` RO user could list `qa` as the only DB (`getDBNames()` → `['qa']`, default db `qa`) but every read (find/count/aggregate/listCollections) failed with `MongoServerError: not authorized on qa to execute command ...`. So data queries against the staging `qa` DB via MONGO_RO_URI were NOT possible — investigation had to rely on CloudWatch logs instead.

If a query is needed, verify the RO user's grants first with a trivial read; don't assume DB access works. May be a temporary grant issue — re-verify before relying on it. Relates to [[staging-api-logs]] and [[staging-db-terminology]].
