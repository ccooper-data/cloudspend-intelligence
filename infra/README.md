# Future infrastructure — plan only

Nothing in this directory has been initialized, planned, applied, or deployed. It documents a possible GCP phase after explicit approval and funding.

Proposed controls:

- BigQuery project daily query quota, defaulting to 10 GiB/day.
- A project-scoped `$25` monthly warning budget named `cloudspend-v1-safety`, with email alerts to default billing IAM recipients at 50%, 90%, and 100%.
- Billing export dataset location and lifecycle settings reviewed before use.
- Cloud Run minimum instances set to zero, maximum instances capped, and unauthenticated access disabled.
- Required APIs enabled only in the approved project.
- Terraform state must not contain secrets and should move to a reviewed remote backend for team use.

Important: budgets send notifications; they do not automatically cap spend. Quotas reduce risk but are not a guarantee of $0 cost.

The budget is an early-warning threshold, not authorization to spend `$25`. The operating target remains `$0` out of pocket, and the account must not be upgraded from the Free Trial without explicit approval.

