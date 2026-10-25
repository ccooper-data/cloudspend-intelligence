"""SQLite-backed anomaly detector and evidence-grounded explanations."""

from __future__ import annotations

import csv
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, asdict
from pathlib import Path

SQL_PATH = Path(__file__).resolve().parents[2] / "sql" / "detect_anomalies.sql"


@dataclass(frozen=True)
class Anomaly:
    usage_date: str
    service: str
    daily_cost: float
    median_cost: float
    absolute_increase: float
    percent_increase: float
    project_id: str
    sku: str
    contributor_cost: float
    explanation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE billing_records (
            usage_date TEXT NOT NULL,
            billing_account_id TEXT NOT NULL DEFAULT 'SYNTHETIC',
            project_id TEXT NOT NULL,
            service TEXT NOT NULL,
            sku TEXT NOT NULL,
            cost REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            is_synthetic TEXT NOT NULL DEFAULT 'true',
            injected_anomaly TEXT NOT NULL DEFAULT 'false'
        )
    """)
    return db


def load_csv(db: sqlite3.Connection, input_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    db.executemany(
        """INSERT INTO billing_records VALUES
        (:usage_date, :billing_account_id, :project_id, :service, :sku,
         :cost, :currency, :is_synthetic, :injected_anomaly)""",
        rows,
    )


def load_records(db: sqlite3.Connection, rows: Iterable[dict[str, object]]) -> None:
    normalized = []
    for row in rows:
        normalized.append({
            "usage_date": row["usage_date"], "project_id": row["project_id"],
            "service": row["service"], "sku": row["sku"], "cost": row["cost"],
        })
    db.executemany(
        """INSERT INTO billing_records
        (usage_date, project_id, service, sku, cost) VALUES
        (:usage_date, :project_id, :service, :sku, :cost)""",
        normalized,
    )


def detect(db: sqlite3.Connection) -> list[Anomaly]:
    flagged = db.execute(SQL_PATH.read_text(encoding="utf-8")).fetchall()
    results: list[Anomaly] = []
    for item in flagged:
        # Stable secondary ordering makes contributor ties deterministic.
        contributor = db.execute(
            """SELECT project_id, sku, ROUND(SUM(cost), 2) contributor_cost
               FROM billing_records
               WHERE usage_date = ? AND service = ?
               GROUP BY project_id, sku
               ORDER BY contributor_cost DESC, project_id ASC, sku ASC
               LIMIT 1""",
            (item["usage_date"], item["service"]),
        ).fetchone()
        explanation = (
            f"On {item['usage_date']}, {item['service']} spend was "
            f"${item['daily_cost']:.2f}, up {item['percent_increase']:.2f}% "
            f"(${item['absolute_increase']:.2f}) from its trailing 14-day median "
            f"of ${item['median_cost']:.2f}. The largest same-day contributor was "
            f"project {contributor['project_id']} / SKU {contributor['sku']} "
            f"at ${contributor['contributor_cost']:.2f}."
        )
        results.append(Anomaly(
            usage_date=item["usage_date"], service=item["service"],
            daily_cost=item["daily_cost"], median_cost=round(item["median_cost"], 2),
            absolute_increase=item["absolute_increase"], percent_increase=item["percent_increase"],
            project_id=contributor["project_id"], sku=contributor["sku"],
            contributor_cost=contributor["contributor_cost"], explanation=explanation,
        ))
    return results

