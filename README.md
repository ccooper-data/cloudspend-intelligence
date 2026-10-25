# CloudSpend Intelligence V1

[![CI](https://github.com/ccooper-data/cloudspend-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/ccooper-data/cloudspend-intelligence/actions/workflows/ci.yml)

A strictly local, $0-cost portfolio project that detects material daily cloud-spend spikes and explains them from query evidence. It uses 90 days of **deterministic, explicitly synthetic** GCP-style billing records. It does not require or contact GCP, does not create resources, and does not use a billing account or paid API.

> **Illustrative data only.** Every record is generated, every billing account identifier is fake, and no row represents anyone's real cloud spend.

## What it demonstrates

- Python data engineering with deterministic fixtures
- SQL windowing and an even-count trailing median
- Materiality-aware anomaly detection
- Evidence-grounded project and SKU attribution
- Boundary, edge-case, and idempotency testing
- CI and infrastructure-as-code planning with explicit cost controls

## Detection rule

Flag a service when its daily cost exceeds its trailing 14-day median by **both** more than 50% and more than $25. The current day is excluded from the baseline; 14 prior days are required. Comparisons are strict, so exactly 50% or exactly $25 does not flag. Zero baselines, decreases, and services without sufficient history do not flag.

## Run locally

Prerequisite: Python 3.10 or newer. No third-party packages, credentials, or network access are needed.

```bash
make demo
make test
```

`make demo` regenerates the 540-row data set (90 days × 6 workload/SKU combinations), executes the SQL detector in an in-memory SQLite database, prints deterministic explanations, and writes `reports/anomalies.json`. Generated reports are ignored by Git.

To run the pieces separately:

```bash
PYTHONPATH=src python -m cloudspend.generate
PYTHONPATH=src python -m cloudspend.cli --input data/synthetic_gcp_billing.csv
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Repository map

```text
data/                  committed synthetic demo data and injection labels
docs/                  architecture and decision record
infra/                 unexecuted future Terraform cost-control sketch
sql/                   detector business rule
src/cloudspend/        generator, loader, detector, explainer, CLI
tests/                 edge cases and reproducibility tests
.github/workflows/     local-equivalent CI; no cloud authentication
```

## Ground truth versus detector inputs

`data/injected_anomalies.csv` and the `injected_anomaly` column make the synthetic scenario auditable. The detector intentionally ignores both. Its decision uses only date, service, and cost; attribution uses project and SKU after an anomaly is found. This prevents label leakage.

## Expected demo behavior

The committed scenario injects three anomalous line items on two service-days. The detector should identify material Cloud Run and BigQuery service spikes and name the largest same-day project/SKU contributor. The explanation is factual and deterministic; it does not overstate the contributor as a proven root cause.

Example output:

```text
On 2025-03-17, Cloud Run spend was $187.95, up 216.09% ($128.49) from its
trailing 14-day median of $59.46. The largest same-day contributor was project
checkout-prod / SKU vCPU-seconds at $132.49.
```

## Tests

The suite covers:

- zero median baseline
- insufficient 14-day history and a new service
- decreases
- deterministic contributor ties
- exact 50% and exact $25 boundaries
- an even-count median
- expected labeled data shape
- byte-for-byte generator idempotency

## Future GCP deployment — not performed

The future design is Billing Export → BigQuery → scheduled query → anomaly table → authenticated Cloud Run API. [`infra/`](infra/) sketches a BigQuery daily byte quota and budget thresholds. It is documentation, not a deployment: CI never invokes Terraform, no backend or credentials are configured, and this project has made no cloud calls.

Budget alerts do not stop spend, and quotas cannot guarantee a zero bill. Any deployment must be a separately approved phase after pricing review, a funded billing account, a real notification channel, and review of `terraform plan`. An optional Gemini summary may be explored later, but the deterministic explanation remains the default and fallback.

See the [architecture](docs/architecture.md) and [ADR 0001](docs/adr/0001-local-deterministic-v1.md).

## Portfolio status

This public repository is designed for code review and learning. It contains no credentials, proprietary code, or real billing data. The synthetic scenario is a demonstration of engineering judgment and evaluation discipline—not a benchmark of production detection accuracy.
