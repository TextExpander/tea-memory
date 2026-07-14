---
name: tenet-serverless-stage-names
description: TENET rest-proj serverless stage names are prod/staging/dev, not "production"
metadata:
  type: reference
---

The `tenet/rest-proj` serverless service (`service: tenet-rest`) uses stage names `prod`, `staging`, `dev` — NOT `production`.

- Lambda functions: `TENET-<stage>-<fn>`, e.g. `TENET-prod-sendGridHook` (log group `/aws/lambda/TENET-prod-sendGridHook`).
- SSM params prefixed with stage, e.g. `prod-rest-send_grid_hook_sqs_url`. These are SecureString — pass `--with-decryption` or you get an encrypted blob back.
