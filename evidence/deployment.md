# Redacted deployment evidence

All data used by this project is explicitly synthetic. This record contains no
billing account identifier, email address, token, credential, or Terraform
state.

## Validated controls

- Project-scoped warning budget: `$25`, with 50%, 90%, and 100% alerts.
- BigQuery project query quota: 10 GiB/day.
- GitHub authentication: keyless Workload Identity Federation, restricted to
  this repository, `main`, and the `gcp-demo` environment.
- Cloud Run: private, zero minimum instances, one maximum instance.
- Cloud Workflow: manual trigger only, 10 GiB per-query maximum, 60-second
  bounded BigQuery call, error-only call logging.
- Cloud Scheduler API, identity, job, and IAM binding: absent.

## Reproducible validation

| Evidence | Result |
| --- | --- |
| Commit | `8c3db8f` |
| CI | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40253902237) |
| Manual Workflow deployment | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40253955579) |
| Manual Workflow execution | [passed](https://github.com/ccooper-data/cloudspend-intelligence/actions/runs/40254028752) |
| Execution state | `SUCCEEDED` |
| Detected service-days | 2 |

The execution reproduced the committed ground truth:

1. `2025-03-17` — Cloud Run; largest contributor `checkout-prod` / `vCPU-seconds`.
2. `2025-03-22` — BigQuery; largest contributor `analytics-prod` / `Analysis`.

After deployment, the GitHub identity's temporary `roles/workflows.editor`
grant was removed. It retains `roles/workflows.invoker` for deliberate manual
execution. The Workflow runtime identity has `roles/bigquery.jobUser` at the
project and writer access only on the `cloudspend_v1` dataset.
