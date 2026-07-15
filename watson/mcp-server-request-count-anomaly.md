---
name: mcp-server-request-count-anomaly
description: The mcp-server-request-count-anomaly CloudWatch alarm (us-west-2, acct 882001132752) is a flaky false-positive signal.
metadata:
  type: reference
---

Alarm `mcp-server-request-count-anomaly` on ALB `app/mcp-server-alb/6224355d8fe6cd62` (tenet-secondary, us-west-2) uses `ANOMALY_DETECTION_BAND(m1, 3)` on RequestCount Sum. Configured 2026-07-04. Its band frequently collapses to a ~0.0 upper threshold for low-traffic hours (e.g. midnight UTC), so normal low-volume traffic (10–20 req/5min) trips it as a "surge" even though absolute volume is at the *daily low* (baseline 200–800 req/hr, peaks ~2400).

To triage: compare the alarm datapoints against the hourly baseline (get-metric-statistics, period 3600) and pull ALB access logs from `s3://mcp-server-alb-logs-882001132752/AWSLogs/.../elasticloadbalancing/us-west-2/YYYY/MM/DD/`. Normal traffic = MCP OAuth flow via Amazon CloudFront: `/mcp` (401 when unauthenticated), `/token`, `/.well-known/oauth-*`. Background internet scanning (zgrab, visionheight.com/scan, Exchange ProxyShell `/ecp/...` probes) is routine noise, all 400/401/404. Routes to SNS `mcp-server-security-alerts`. On 2026-07-15 00:37 UTC it fired on 15 & 21 req/5min = false positive.
