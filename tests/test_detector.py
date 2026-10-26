from __future__ import annotations

import hashlib
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from cloudspend.detector import connect, detect, detector_sql, load_records
from cloudspend.generate import build_records, write_dataset


def series(costs, service="Test Service", project="project-a", sku="sku-a"):
    start = date(2025, 1, 1)
    return [
        {"usage_date": (start + timedelta(days=i)).isoformat(), "project_id": project,
         "service": service, "sku": sku, "cost": cost}
        for i, cost in enumerate(costs)
    ]


def run(rows):
    db = connect()
    load_records(db, rows)
    return detect(db)


class DetectorTests(unittest.TestCase):
    def test_packaged_detector_sql_matches_reviewable_source(self):
        source = Path(__file__).resolve().parents[1] / "sql" / "detect_anomalies.sql"
        self.assertEqual(source.read_text(encoding="utf-8"), detector_sql())

    def test_flags_only_when_both_thresholds_are_strictly_exceeded(self):
        found = run(series([100] * 14 + [151]))
        self.assertEqual(1, len(found))
        self.assertEqual(51, found[0].absolute_increase)

    def test_exact_percentage_boundary_does_not_flag(self):
        self.assertEqual([], run(series([100] * 14 + [150])))

    def test_exact_dollar_boundary_does_not_flag(self):
        self.assertEqual([], run(series([50] * 14 + [75])))

    def test_zero_baseline_does_not_flag_or_divide_by_zero(self):
        self.assertEqual([], run(series([0] * 14 + [100])))

    def test_insufficient_history_and_new_service_do_not_flag(self):
        rows = series([100] * 13 + [1000])
        rows += series([500], service="Brand New", project="new", sku="new")
        self.assertEqual([], run(rows))

    def test_decrease_does_not_flag(self):
        self.assertEqual([], run(series([100] * 14 + [10])))

    def test_even_median_averages_middle_values(self):
        found = run(series(list(range(10, 150, 10)) + [200]))
        self.assertEqual(75, found[0].median_cost)

    def test_contributor_tie_has_stable_lexicographic_winner(self):
        rows = series([100] * 14)
        event_date = date(2025, 1, 15).isoformat()
        rows += [
            {"usage_date": event_date, "project_id": "z-project", "service": "Test Service", "sku": "a-sku", "cost": 100},
            {"usage_date": event_date, "project_id": "a-project", "service": "Test Service", "sku": "z-sku", "cost": 100},
        ]
        found = run(rows)
        self.assertEqual("a-project", found[0].project_id)
        self.assertEqual("z-sku", found[0].sku)

    def test_generated_dataset_contains_expected_labeled_injections(self):
        records, labels = build_records()
        self.assertEqual(540, len(records))
        self.assertEqual(3, len(labels))
        self.assertTrue(all(row["is_synthetic"] == "true" for row in records))

    def test_generation_is_idempotent_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as folder:
            data, labels = Path(folder) / "data.csv", Path(folder) / "labels.csv"
            write_dataset(data, labels)
            first = (hashlib.sha256(data.read_bytes()).hexdigest(), hashlib.sha256(labels.read_bytes()).hexdigest())
            write_dataset(data, labels)
            second = (hashlib.sha256(data.read_bytes()).hexdigest(), hashlib.sha256(labels.read_bytes()).hexdigest())
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

