# GCP deployment and teardown runbook

Status: **prepared, not yet applied**. The live project is
`cloudspend-intelligence-v1`. All committed data is synthetic.

## Non-negotiable gates

1. Confirm the Free Trial remains active and has not been upgraded.
2. Create and visibly verify project-scoped budget `cloudspend-v1-safety` for
   `$25`, with default billing-email alerts at 50%, 90%, and 100%.
3. Keep `deploy_workloads=false` until the budget evidence is saved.
4. Review a Terraform plan. Any unexpected service, public principal, minimum
   Cloud Run instance, or unbounded query is a stop condition.
5. Never enable Gemini, Vertex AI, GKE, VMs, or unrelated APIs.

## Staged deployment

### Stage 0 — warning budget only

Create the budget through the Billing console or Google Cloud CLI. This is the
only live change permitted before the three thresholds and email recipients are
verified.

### Stage 1 — keyless identity bootstrap

With `create_deployment_identity=true` and `deploy_workloads=false`, create the
GitHub Workload Identity pool/provider and deployer service account. The OIDC
condition accepts only the numeric GitHub owner ID, this repository, and the
`main` branch. Create a GitHub environment named `gcp-production` with required
reviewers, then set the non-secret provider/service-account/state-bucket
variables. Store the billing account ID and alert email as GitHub secrets.

### Stage 2 — reviewed plan

Run **GCP Terraform Plan** manually with confirmation `PLAN`. The workflow is
keyless and intentionally has no apply step. Confirm:

- only the allow-listed APIs are enabled;
- BigQuery has a 10 GiB/day project quota and every query has the same maximum;
- Cloud Run has min 0, max 1, and no public IAM member;
- Scheduler runs once daily with one retry;
- all runtime identities have distinct, narrow roles;
- the container reference is pinned by digest;
- the failure alert targets the verified operator email.

### Stage 3 — deploy and validate

Only after plan approval, add a separately reviewed apply job protected by the
`gcp-production` environment. Load `data/synthetic_gcp_billing.csv`, run the
Workflow once, and compare the BigQuery results with the committed ground truth.
Obtain an identity token before calling the private Cloud Run API; verify an
unauthenticated request is rejected.

## Required evidence

Record timestamps and redacted command output in `evidence/deployment.md`:

- budget scope, amount, thresholds, and email recipients;
- trial status and `$0.00` out-of-pocket charges;
- Terraform plan summary and applied commit SHA;
- BigQuery row count (540), anomaly service-days (2), and attributed rows;
- Cloud Run min/max settings and unauthenticated rejection;
- successful manual Workflow execution and Scheduler configuration;
- IAM bindings showing no service-account keys or public principals;
- failure-test incident and recovery;
- final resource inventory and post-teardown billing check.

Never commit billing IDs, email addresses, tokens, project credentials, raw
Terraform state, or screenshots containing private account details.

## Failure handling

The query uses `CREATE OR REPLACE TABLE`, so a retry is idempotent. Scheduler is
limited to one retry. The Workflow fails if BigQuery does not finish within its
bounded call, and Cloud Monitoring alerts on any non-success execution. Before a
manual retry, inspect the execution and verify bytes processed; do not create a
retry loop.

## Teardown

1. Disable the Scheduler job first.
2. Save redacted validation evidence.
3. Destroy workload resources with the reviewed Terraform state.
4. Confirm Cloud Run, Workflows, Scheduler, BigQuery datasets, Artifact Registry,
   alert policies, and workload service accounts are absent.
5. Remove GitHub deployment variables/secrets and Workload Identity bindings.
6. Keep or remove the warning budget according to whether the project remains
   linked to billing.
7. Recheck Billing after usage reporting has settled and record the result.

Do not delete the GCP project until all portfolio evidence is saved and the user
explicitly approves that destructive action.
