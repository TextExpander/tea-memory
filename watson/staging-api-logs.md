---
name: staging-api-logs
description: Where staging addSnippet/REST errors surface and Mongo collection name casing
metadata:
  type: reference
---

Staging Meteor/REST app errors (e.g. `API: addSnippet - databaseError`) surface in CloudWatch log group `/tenet/staging/api` (profile tenet-primary, us-east-1), NOT in the `TENET-staging-addSnippet` lambda group. Stream names look like `staging/api/tenet_api_staging/<id>`.

REST error log format (`repos/tenet/modules/server/util/restErrorHandler.ts:34-40`):
`API: {method} - {error.message} - [{description}] - {userId} - {client}` then the request payload as extraData. So the trailing hex is the **userId** and the browser string is the client (Chrome Headless = CI/e2e).

Mongo collection names in the `qa` staging DB are camelCase: `snippetGroups`, `snippetGroupMembers`, `snippetHistory` (NOT lowercase `snippetgroups`). Querying wrong casing silently returns 0. See [[staging-db-terminology]].
