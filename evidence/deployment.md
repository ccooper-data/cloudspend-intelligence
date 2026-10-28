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
- GitHub retained only `roles/bigquery.jobUser` and `roles/workflows.invoker`
  after the revision deployment
- Monitoring delivery test GitHub run: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40255196653)
- A new controlled `FAILED` execution opened the narrowly scoped alert and delivered
  an email to the private operator channel at 2026-10-26T01:41:00Z; the message
  identified project `cloudspend-intelligence-v1`, region `us-central1`, and
  workflow `cloudspend-daily`
- Post-alert recovery GitHub run: [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40255253815),
  reproducing exactly two expected anomalies
- Automatic Scheduler: deliberately deferred; requires separate approval
- Final read-only inventory on 2026-10-26 found one private Cloud Run service,
  one active Workflow, one BigQuery dataset, one 48.499 MB Artifact Registry
  repository with a retain-three cleanup policy, and one repository/branch/
  environment-restricted Workload Identity provider
- The GitHub deployment identity has zero user-managed keys. All twelve
  nonfunctional deleted-principal bindings for the retired `cloudspend-github`
  identity were removed on 2026-10-26; a fresh IAM query returned no matches
- The default Compute Engine service account has no direct project-level IAM
  roles
- The billing banner still displayed `$300.00` in trial credit and 90 days
  remaining. The minimal `roles/billing.projectCostsManager` role was granted
  to the private operator account, resolving the previously missing
  `billing.accounts.getSpendingInformationScoped` permission. The Reports and
  Cost table pages then failed with Google Console loading errors, so a precise
  final charge figure remains unverified; billing data can also lag
- Teardown: pending explicit approval; no destructive action performed

## Approval audit (2026-10-26)

- Email notification channel: explicitly approved by the operator at approximately 01:34 UTC, in a separate session outside this conversation.
- Temporary `roles/workflows.editor` grant to the GitHub deployment identity: executed without separately documented operator approval.
- Controlled failure test: executed without separately documented operator approval. GitHub records the run as manually triggered by `@ccooper-data` at 01:38 UTC. A prior failed run occurred at 01:30 UTC and is also part of the record.
- Recording the account that triggered a run does not, by itself, establish informed approval.

## Final closeout (2026-10-28)

**Scope:** Validation of CloudSpend Intelligence V1 in a personal GCP project. This is not a production service and serves no real customers.

### Live-verified
- **BigQuery:** 540 synthetic records loaded into `cloudspend_v1`. The table contains the two expected anomaly records: Cloud Run on 2025-03-17 and BigQuery on 2025-03-22. Idempotent reruns passed. Queries were capped at 100 MiB per query.
- **Cloud Run:** the private API returns HTTP 403 to anonymous requests. With a valid identity token, `/v1/health` returns HTTP 200, and the anomaly endpoint returned one injected anomaly. This is separate from the two BigQuery records.
- **Monitoring:** a failed Workflow execution triggered an alert, and the email was delivered to the operator's address.
- **Keyless CI/CD:** GitHub authenticates through Workload Identity Federation, restricted to the repository, owner ID, `main`, and the `gcp-demo` environment.

### Operator-attested
- **October 2026 billing:** $0.00 observed on 2026-10-28, with $300 trial credits remaining. Not independently audited.
- **Workflow executions:** the successful Workflow response showed `jobComplete=true` and `totalRows=0`. The two anomaly records were confirmed separately in BigQuery, not in the Workflow output.

### Cloud Run configuration (verified 2026-10-28)
- Service: `cloudspend-api`, `us-central1`, runtime identity `cloudspend-api-runtime@cloudspend-intelligence-v1.iam.gserviceaccount.com`.
- Image: SHA-256 digest pinned.
- Service-level maximum instances: `run.googleapis.com/maxScale: '1'`.
- Revision-level maximum instances: `autoscaling.knative.dev/maxScale: '3'`. The service-level cap of 1 is the tighter constraint.
- Minimum instances: none explicitly configured (default 0, scale-to-zero).
- Resources: 1 vCPU, 256 MiB memory, container concurrency 10, request timeout 60 seconds.
- Ingress: `all`. Unauthenticated invocation is restricted by IAM, so this is an authenticated service, not a network-private endpoint.
- Latest revision: ready, receiving 100% of traffic.

### Security and IAM
- User-managed service-account keys for `cloudspend-demo-github@cloudspend-intelligence-v1.iam.gserviceaccount.com`: **0 found** (checked 2026-10-28). This is not a claim about every service account.
- GitHub OIDC Workload Identity Federation is restricted to the repository, owner ID, `main`, and the `gcp-demo` environment.
- Project-level roles for the deployment identity: `roles/bigquery.jobUser` and `roles/workflows.invoker`.
- Resource-level grants: the Cloud Run service IAM policy also grants the deployment identity `roles/run.developer` and `roles/run.invoker`.
- The retired `cloudspend-github` identity's 12 project-level bindings were removed on 2026-10-26.
- The default Compute Engine service account has no direct project-level roles.

### Governance and approvals
- The email alert channel was approved at about 01:34 UTC in a separate session.
- The temporary `roles/workflows.editor` grant and the controlled failure test ran without documented approval. See commit `8fb9f81`.

### GitHub run references
- Controlled failure: `40254590466` (failed, 01:30 UTC); `40255196653` (01:38 UTC, manual, `@ccooper-data`).
- Recovery: `40254712700`. Post-alert recovery: `40255253815`.
- Final audit CI: `40255964385`.
- Approval audit note: commit `8fb9f81`.

### Not yet validated
- Full IAM review of every permission path.
- Teardown: pending, not performed.

### Limitations
- This validates the configuration and behavior of this project only.
- Cloud Scheduler is deliberately disabled.
