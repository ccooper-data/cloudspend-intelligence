# Architecture

## V1: local and $0

```text
deterministic generator
        |
        v
synthetic billing CSV + separate ground-truth labels
        |
        v
in-memory SQLite --> SQL trailing-median detector
        |                         |
        +-------------------------+
                    |
                    v
deterministic project/SKU attribution --> JSON report + console explanation
```

The detector never reads `injected_anomaly` or the labels file. Those fields are evaluation truth only. Detection groups line items into daily service totals, uses the preceding 14 calendar days for the median, and applies both materiality thresholds. The explanation reports observed evidence and deliberately says “largest contributor,” not “root cause.”

## Data contract

The generated billing file resembles a small subset of GCP detailed billing export fields:

| Field | Meaning |
|---|---|
| `usage_date` | UTC-style daily usage date |
| `billing_account_id` | Obvious synthetic placeholder |
| `project_id`, `service`, `sku` | Attribution dimensions |
| `cost`, `currency` | Synthetic USD daily cost |
| `is_synthetic` | Always `true` |
| `injected_anomaly` | Ground-truth evaluation label; ignored by detector |

## GCP validation shape (deployment gated)

```text
synthetic CSV -> BigQuery billing_records -> Workflows detector query
                                                ^              |
                                                |              v
                                      Cloud Scheduler      anomalies table
                                                               |
                                                               v
                                                private Cloud Run API
```

The project uses the GCP Free Trial without upgrading to paid billing. Terraform
has two explicit gates: a separately bootstrapped, keyless GitHub identity and
the workloads themselves. Workloads default off. A project-scoped `$25` warning
budget and all email thresholds must be verified before either gate is opened.

BigQuery queries are limited both by a 10 GiB/day project quota and a 10 GiB
per-query maximum. The detector recreates its result table, making retries
idempotent. Scheduler runs daily with one retry; Workflows surfaces failures to
Cloud Monitoring. Cloud Run accepts only authenticated callers, keeps zero
minimum and one maximum instance, and runs a digest-pinned container. No public
IAM principal, user-managed service-account key, Gemini service, VM, cluster, or
always-on compute is part of the design.

GitHub Actions obtains short-lived credentials through Workload Identity
Federation, constrained to the numeric repository owner, repository name, and
`main` branch. The cloud workflow is manual, environment-protected, and
plan-only until a separate review adds an apply step.

