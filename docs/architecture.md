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

## Future GCP shape (not deployed)

```text
Cloud Billing export -> BigQuery raw table -> scheduled SQL/query job
                                              |
                                              v
                                        anomaly table
                                              |
                                              v
                                  Cloud Run deterministic API
```

Terraform sketches this future architecture with guardrails. Before any deployment, a human must explicitly approve billing, choose a project and region, review current pricing, set a real notification channel, and run `terraform plan`. This repository contains no credentials and performs no cloud calls.

