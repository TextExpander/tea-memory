---
name: growthbook-timeout-alert
description: Root cause of the "GrowthBook surpassed timeout when loading features" alert spike (Jul 2026)
metadata:
  type: reference
---

The "GrowthBook surpassed timeout when loading features after N attempts" alert comes from `repos/tenet/modules/server/growthbook/growthbook.ts` (500ms timeout × 2 attempts against `growthproxy-prod`; all envs — dev/staging/prod — point `GB_API_HOST` at growthproxy-*prod*).

The mid-July-2026 spike is a *code change, not load*: commit `55144ba19` (MSSN-1067, Jul 17 2026) switched the success signal from `growthBook.ready` to `init().success`. In `@growthbook/growthbook@1.1.0` a timed-out `init()` still leaves `ready=true`, so the old check almost never logged; the new one logs on every timeout miss — an observability artifact of pre-existing cold-start races, not a new failure.

Capacity is fine: growthbook-prod ECS (growthproxy ×6, growthapi ×4) CPU flat ~10-16% avg / ~45% max over 14 days, no trend — a capacity bump is not warranted.

Errors reach Slack via winston `SlackLogger` (`repos/tenet/.../logging/log.ts`); the phrase was not found in prod ECS/lambda logs, so it likely surfaces from staging and/or Sentry aggregation.

**How to apply:** If this alert re-spikes, first confirm it is the MSSN-1067 logging behavior (not real load) before recommending capacity changes. GrowthBook is self-hosted on ECS (growthproxy/growthapi task defs in repos/devops).
