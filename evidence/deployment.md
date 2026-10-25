# CloudSpend Intelligence V1 — live validation evidence

Status: **BigQuery synthetic-data validation live; application and automation workloads not deployed**. Populate only with redacted, verified output. Never
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
- Synthetic rows loaded: expected 540; actual 540
- Detector result rows: expected 2; actual 2
- `2025-03-17 / Cloud Run / checkout-prod / vCPU-seconds`: $187.95 daily, $59.46 median, 216.09% / $128.49 increase; top contributor $132.49
- `2025-03-22 / BigQuery / analytics-prod / Analysis`: $204.58 daily, $80.05 median, 155.57% / $124.53 increase; top contributor $187.99
- Successful validation: https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40234644298
- Idempotent second execution produced the same rows: https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40234708958
- BigQuery bytes processed per successful run: 89,298 bytes; reported billed bytes 40 MiB due to BigQuery minimums; each query capped at 100 MiB
- Compatibility failures were bounded and preserved: reserved alias in run 40234417512; correlated subquery in run 40234526890
- Live validation evidence captured at (UTC): 2026-10-25T21:17:41Z

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
