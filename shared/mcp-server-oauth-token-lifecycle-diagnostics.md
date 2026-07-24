---
name: mcp-server-oauth-token-lifecycle-diagnostics
description: OAuthCoordinator logs redisDegraded, mode, uptimeSec for token validation context
metadata:
  type: reference
  source: auto-reflection
  learnedBy: sherlock
  learnedAt: 2026-07-24
---

When OAuthCoordinator.ts rejects refresh tokens (lines 1182-1201), it logs diagnostic context: `redisDegraded` (boolean), `mode` (valkey/redis), and `uptimeSec` (uptime since last restart). Healthy Valkey + high uptime (~6+ days) indicates tokens are genuinely expired/evicted, not a service fail-closed. Use uptimeSec to rule out post-deploy reconnect storms; use redisDegraded flag to distinguish infrastructure issues from client token staleness.
