# Future infrastructure — plan only

Nothing in this directory has been initialized, planned, applied, or deployed. It documents a possible GCP phase after explicit approval and funding.

Proposed controls:

- BigQuery project daily query quota, defaulting to 10 GiB/day.
- A small monthly budget threshold, with alerts at 50%, 80%, 100%, and forecasted 100%.
- Billing export dataset location and lifecycle settings reviewed before use.
- Cloud Run minimum instances set to zero, maximum instances capped, and unauthenticated access disabled.
- Required APIs enabled only in the approved project.
- Terraform state must not contain secrets and should move to a reviewed remote backend for team use.

Important: budgets send notifications; they do not automatically cap spend. Quotas reduce risk but are not a guarantee of $0 cost.

