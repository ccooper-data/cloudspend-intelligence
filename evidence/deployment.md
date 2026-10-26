# CloudSpend Intelligence V1 — live validation evidence

Status: **BigQuery, private Cloud Run, and manual Workflow validated; automatic
scheduling disabled**. All data is explicitly synthetic. Never commit billing
account IDs, email addresses, tokens, credentials, Terraform state, or private
account screenshots.

## Cost gate

- Free Trial active and not upgraded: verified in Billing console
- Out-of-pocket charges before deployment: `$0.00` verified in Billing console
- Budget name: `cloudspend-v1-safety`
- Scope: `cloudspend-intelligence-v1` only
- Amount: `$25` warning threshold; not spending authorization
- Actual-spend thresholds: 50%, 90%, 100%
- Default billing IAM email recipients enabled: verified
- Evidence captured at (UTC): 2026-10-25T20:45:58Z

## Reviewed infrastructure and identity

- Identity commit SHA: `8c65667118d25356339e2e8caa06f5d31730b7ce`
- Identity CI: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40233601200)
- BigQuery project quota: 10 GiB/day — verified effective limit 10,240 MiB
- GitHub federation: restricted to `ccooper-data/cloudspend-intelligence`,
  numeric owner ID, `refs/heads/main`, and environment `gcp-demo`
- Keyless token impersonation: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40233614291)
- Obsolete GitHub environment `gcp-production`: deleted after confirming its
  variables referenced only the soft-deleted identity
- User-managed service-account keys: 0
- GitHub identity project roles after Workflow deployment:
  `roles/bigquery.jobUser` and `roles/workflows.invoker`
- Temporary `roles/workflows.editor`: removed after deployment
- Workflow service-account attachment: GitHub has
  `roles/iam.serviceAccountUser` only on `cloudspend-workflow`
- Identity evidence captured at (UTC): 2026-10-25T21:04:04Z

## Data and detector

- Dataset: `cloudspend_v1`, location `US`, labeled synthetic/portfolio
- Synthetic rows loaded: expected 540; actual 540
- Detector result rows: expected 2; actual 2
- `2025-03-17 / Cloud Run / checkout-prod / vCPU-seconds`: $187.95 daily,
  $59.46 median, 216.09% / $128.49 increase; top contributor $132.49
- `2025-03-22 / BigQuery / analytics-prod / Analysis`: $204.58 daily,
  $80.05 median, 155.57% / $124.53 increase; top contributor $187.99
- Initial validation: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40234644298)
- Idempotent second execution: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40234708958)
- BigQuery bytes processed per validation: 89,298 bytes; each validation query
  capped at 100 MiB
- Compatibility failures were bounded and preserved: reserved alias in run
  `40234417512`; correlated subquery in run `40234526890`
- Live validation evidence captured at (UTC): 2026-10-25T21:17:41Z

## Private API validation

- Cloud Run is private, with zero minimum and one maximum instance
- Unauthenticated `/v1/health` request: rejected with 403
- Authenticated `/v1/health` request: 200 on both service URL forms
- Authenticated anomaly request: exactly two expected synthetic anomalies
- Deployment: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40252435793)
- Validation: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40252520755)

## Manual Workflow validation

| Evidence | Result |
| --- | --- |
| Corrected commit | `8c3db8f` |
| CI | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40253902237) |
| Manual deployment | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40253955579) |
| Manual execution | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40254028752) |
| Execution state | `SUCCEEDED` |
| Detected service-days | 2 |

- Workflow: `cloudspend-daily`, region `us-central1`, state `ACTIVE`
- Runtime identity: `cloudspend-workflow`
- Runtime access: `roles/bigquery.jobUser` at project level and writer access
  only on `cloudspend_v1`
- Query maximum: 10 GiB; BigQuery call timeout: 60 seconds
- Logging: errors only
- Trigger label: `manual`
- Cloud Scheduler API, service account, job, and IAM binding: absent
- Cloud Monitoring email channel: enabled; destination retained only in GCP
- Alert policy: `CloudSpend manual workflow failure`, enabled and filtered to
  `cloudspend-daily`, `us-central1`, and execution status `FAILED`

## Remaining validation and teardown

- Controlled execution `0b3673b8-389d-4f1a-853f-aa74eda6f47a` entered
  `FAILED` with `CONTROLLED_TEST_FAILURE`; its branch submitted no BigQuery job
- Controlled-failure GitHub run: [cloud failure verified; wrapper assertion exposed and corrected](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40254590466)
- Recovery execution `616bb5d2-2a56-4c77-b05d-b025ed75a4a9` entered
  `SUCCEEDED` and reproduced exactly two expected anomalies
- Recovery GitHub run: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40254712700)
- GitHub remained `roles/workflows.invoker` only after the revision deployment
- Workflow failure policy and email channel: configured; delivery test pending
- Automatic Scheduler: deliberately deferred; requires separate approval
- Final reported charges / trial-credit change: pending
- Teardown: pending explicit approval; no destructive action performed
