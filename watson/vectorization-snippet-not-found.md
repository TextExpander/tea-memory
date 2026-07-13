---
name: vectorization-snippet-not-found
description: "Snippet not found for snippetId" errors come from orphaned snippetsEmbeddings records in the vectorization SQS consumer.
metadata:
  type: project
---

TenetBot alert "Snippet not found for snippetId: <UUID>" originates in `repos/tenet/modules/server/tasks/vectorizeSnippetsInQueueTask.ts:364` (SQS consumer). Consumer log group: `/aws/lambda/TASK-staging-vectorizeSnippetsInQueue` (producer: `/aws/lambda/TASK-staging-queueSnippetsToVectorize`).

Root cause: orphaned records in the `snippetsEmbeddings` collection (note plural collection names: `snippets`, `snippetsEmbeddings`, `snippetGroups` in the `qa` db). `queueSnippetsToVectorizeTask` selects all embeddings with `embeddingStatus=NeedsProcessing` and enqueues them; the consumer does `SnippetModel.findById(snippetId)`. If the parent snippet (and often its group) was hard-deleted while the embedding survived, findById returns null → error. Consumer pushes `batchItemFailures` (retryable) so each orphan logs on every redelivery until DLQ after 5 attempts.

App deletes DO clean embeddings (snippetModel deleteSnippet:884, snippetGroupModel/teamModel deleteSnippetEmbeddingsForGroup), and deleteSnippet is a SOFT delete (deleted=true, doc stays). Orphans arise from hard-delete/teardown paths that bypass those Mongoose hooks (common in staging test churn). updateSnippet re-arms the embedding to NeedsProcessing (snippetModel:778).

The repo code already flags this as known (snippetEmbeddingRepo.ts searchSnippetEmbeddings comment: wire embedding deletes to doc delete + run cleanup script).
