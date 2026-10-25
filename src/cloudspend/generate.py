"""Generate explicitly synthetic, deterministic GCP-style billing records."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

START_DATE = date(2025, 1, 1)
DAYS = 90
DEFAULT_DATA = Path("data/synthetic_gcp_billing.csv")
DEFAULT_LABELS = Path("data/injected_anomalies.csv")


@dataclass(frozen=True)
class Workload:
    project_id: str
    service: str
    sku: str
    base_cost: float


WORKLOADS = (
    Workload("checkout-prod", "Cloud Run", "vCPU-seconds", 42.00),
    Workload("checkout-prod", "Cloud Run", "GiB-seconds", 18.00),
    Workload("analytics-prod", "BigQuery", "Analysis", 65.00),
    Workload("analytics-dev", "BigQuery", "Storage", 16.00),
    Workload("shared-platform", "Cloud Storage", "Standard storage", 12.00),
    Workload("shared-platform", "Cloud Logging", "Log ingestion", 24.00),
)

# Labels are ground truth for evaluation, never inputs to the detector.
INJECTIONS = {
    (date(2025, 3, 17), "checkout-prod", "Cloud Run", "vCPU-seconds"): 92.00,
    (date(2025, 3, 17), "checkout-prod", "Cloud Run", "GiB-seconds"): 38.00,
    (date(2025, 3, 22), "analytics-prod", "BigQuery", "Analysis"): 120.00,
}


def _normal_cost(base: float, day_index: int, workload_index: int) -> float:
    """A deterministic weekly pattern; no random state or external data."""
    weekly = (-0.04, -0.01, 0.02, 0.04, 0.01, -0.03, -0.05)
    small_cycle = ((day_index + workload_index * 2) % 5 - 2) * 0.003
    return round(base * (1 + weekly[day_index % 7] + small_cycle), 2)


def build_records() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    labels: list[dict[str, str]] = []
    for day_index in range(DAYS):
        usage_date = START_DATE + timedelta(days=day_index)
        for workload_index, workload in enumerate(WORKLOADS):
            key = (usage_date, workload.project_id, workload.service, workload.sku)
            normal = _normal_cost(workload.base_cost, day_index, workload_index)
            injected = INJECTIONS.get(key, 0.0)
            cost = round(normal + injected, 2)
            row = {
                "usage_date": usage_date.isoformat(),
                "billing_account_id": "SYNTHETIC-000000-000000",
                "project_id": workload.project_id,
                "service": workload.service,
                "sku": workload.sku,
                "cost": f"{cost:.2f}",
                "currency": "USD",
                "is_synthetic": "true",
                "injected_anomaly": str(injected > 0).lower(),
            }
            records.append(row)
            if injected:
                labels.append({**row, "injected_amount": f"{injected:.2f}"})
    return records, labels


def write_dataset(data_path: Path = DEFAULT_DATA, labels_path: Path = DEFAULT_LABELS) -> None:
    records, labels = build_records()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    for path, rows in ((data_path, records), (labels_path, labels)):
        fieldnames = list(rows[0])
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {len(records)} explicitly synthetic records to {data_path}")
    print(f"Wrote {len(labels)} ground-truth injection labels to {labels_path}")


if __name__ == "__main__":
    write_dataset()

