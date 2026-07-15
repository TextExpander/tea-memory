# Memory Index

One line per memory file: - [Title](file.md), a short hook. No memory content here.

- [Staging API logs](staging-api-logs.md) — addSnippet/REST errors live in `/tenet/staging/api`; Mongo collections are camelCase.
- [Vectorization snippet-not-found](vectorization-snippet-not-found.md) — "Snippet not found for snippetId" = orphaned snippetsEmbeddings records; consumer log group TASK-staging-vectorizeSnippetsInQueue.
- [mcp-server request-count anomaly alarm](mcp-server-request-count-anomaly.md) — flaky false-positive; band collapses to ~0 at low-traffic hours; triage via baseline + ALB access logs.
