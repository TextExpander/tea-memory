---
name: long-output-multiple-messages
description: When output is long, split across Slack messages instead of letting it become an auto-attached file
metadata:
  type: feedback
---

When a finding is long, do NOT let the reply grow so large it becomes an auto-attached file. Split it across multiple Slack messages instead.

**Why:** Hernán (2026-07-22) said an attached-file output was hard to read; multiple concise messages are preferred.
**How to apply:** Keep each reply concise (~3000 chars). Lead with the answer; push long logs/queries/diffs to the end. Split long findings into logical chunks. Note: only one threaded reply is produced per turn, so "multiple messages" means spreading the content across turns.
