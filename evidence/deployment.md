# CloudSpend Intelligence V1 — live validation evidence

Status: **identity and empty BigQuery dataset live; data and workloads not deployed**. Populate only with redacted, verified output. Never
commit billing account IDs, email addresses, access tokens, credentials,
Terraform state, or private account screenshots.

## Cost gate

- Free Trial active and not upgraded: verified in Billing console
- Out-of-pocket charges before deployment: `$0.00` verified in Billing console
- Budget name: `cloudspend-v1-safety`
- Scope: `cloudspend-intelligence-v1` only
- Amount: `$25` warning threshold; not spending authorization
- Actual-spend thresholds: 50%, 90%, 100%
- Default billing IAM email recipients enabled: verified (notification rule leaves defaults enabled)
- Evidence captured at (UTC): 2026-10-25T20:45:58Z

## Reviewed infrastructure

- Identity commit SHA: `8c65667118d25356339e2e8caa06f5d31730b7ce`
- CI: passed — https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40233601200
- Terraform plan summary: pending
- Enabled before workloads: Service Usage, Billing Budgets, BigQuery, IAM Credentials, and Security Token Service APIs only
- BigQuery project quota: 10 GiB/day — verified effective limit 10,240 MiB
- Cloud Run scaling: min 0 / max 1 — pending live verification
- Public Cloud Run principals absent: pending
- GitHub federation: active; restricted to `ccooper-data/cloudspend-intelligence`, numeric owner ID, and `refs/heads/main`
- Previous `cloudspend-github` service account and `github-actions` pool/provider: soft-deleted; recoverable for 30 days from 2026-10-25
- Active GitHub identity: `cloudspend-demo-github` with `github-demo/cloudspend-demo`
- Federation principal: restricted to repository, numeric owner ID, `main`, and GitHub environment `gcp-demo`
- Keyless token impersonation: passed on attempt 2 after IAM propagation — https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40233614291
- Obsolete GitHub environment `gcp-production`: deleted after confirming its variables referenced only the soft-deleted identity
- Active GitHub environments: `gcp-demo` only
- Active identity project roles: `roles/bigquery.jobUser` only
- Dataset-scoped identity role: `roles/bigquery.dataEditor` on `cloudspend_v1` only
- User-managed service-account keys: 0
- Identity evidence captured at (UTC): 2026-10-25T21:04:04Z
- Scheduler: daily, UTC, one retry — pending
- Workflow query maximum: 10 GiB — pending
- Failure notification channel verified: pending

## Data and detector

- Dataset: `cloudspend_v1`, location `US`, labels `data_classification=synthetic` and `environment=portfolio`
- Dataset tables before load: 0
- BigQuery access evidence captured at (UTC): 2026-10-25T21:10:34Z
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
