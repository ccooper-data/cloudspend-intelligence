# CloudSpend Intelligence V1 — live validation evidence

Status: **not deployed**. Populate only with redacted, verified output. Never
commit billing account IDs, email addresses, access tokens, credentials,
Terraform state, or private account screenshots.

## Cost gate

- Free Trial active and not upgraded: pending
- Out-of-pocket charges before deployment: pending
- Budget name: `cloudspend-v1-safety`
- Scope: `cloudspend-intelligence-v1` only
- Amount: `$25` warning threshold; not spending authorization
- Actual-spend thresholds: 50%, 90%, 100%
- Default billing IAM email recipients enabled: pending
- Evidence captured at (UTC): pending

## Reviewed infrastructure

- Applied commit SHA: pending
- Terraform plan summary: pending
- Enabled API allow-list reviewed: pending
- BigQuery project quota: 10 GiB/day — pending live verification
- Cloud Run scaling: min 0 / max 1 — pending live verification
- Public Cloud Run principals absent: pending
- User-managed service-account keys absent: pending
- Scheduler: daily, UTC, one retry — pending
- Workflow query maximum: 10 GiB — pending
- Failure notification channel verified: pending

## Data and detector

- Synthetic rows loaded: expected 540; actual pending
- Detector result rows: expected 2; actual pending
- `2025-03-17 / Cloud Run / checkout-prod / vCPU-seconds`: pending
- `2025-03-22 / BigQuery / analytics-prod / Analysis`: pending
- BigQuery bytes processed: pending
- Idempotent second execution produced the same rows: pending

## API validation

- Container image digest: pending
- Health check with authenticated request: pending
- Unauthenticated request rejected: pending
- Deterministic explanation matched local output: pending

## Automation and failure handling

- Manual Workflow execution succeeded: pending
- Scheduler-to-Workflow invocation succeeded: pending
- Controlled failure produced Monitoring incident/email: pending
- Recovery run succeeded without duplicate results: pending

## Teardown and final cost

- Scheduler disabled before teardown: pending
- Workload resources removed: pending
- Workload service accounts and WIF bindings removed: pending
- Final resource inventory empty except explicitly retained controls: pending
- Final reported charges / trial credit change: pending
- Evidence captured at (UTC): pending
