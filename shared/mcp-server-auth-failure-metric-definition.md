---
name: mcp-server-auth-failure-metric-definition
description: CloudWatch log-metric-filter on /ecs/mcp-server audit log; alarm threshold is 10 in 5 min
metadata:
  type: reference
  source: auto-reflection
  learnedBy: sherlock
  learnedAt: 2026-07-24
---

The mcp-server-auth-failure-spike alarm is a CloudWatch log-metric-filter on /ecs/mcp-server matching `audit_action=authentication && audit_result=failure` (terraform/alarms.tf:138-165). Alarm triggers on a single datapoint > 10 in 5 minutes — fairly sensitive. When investigating spikes, check OAuthCoordinator.ts for missing_userid_after_grace (orphaned tokens, steady ~11-12/hr baseline) vs invalid_refresh_token (stale client tokens, variable). Include Valkey health (`redisDegraded`, `mode`, `uptimeSec`) in diagnostics.
