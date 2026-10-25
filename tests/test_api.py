import csv
from pathlib import Path
import unittest

from cloudspend.api import analyze_payload


ROOT = Path(__file__).resolve().parents[1]


class ApiTests(unittest.TestCase):
    def test_synthetic_fixture_returns_expected_anomalies(self) -> None:
        with (ROOT / "data" / "synthetic_gcp_billing.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            records = list(csv.DictReader(handle))

        response = analyze_payload({"records": records})

        self.assertIs(response["synthetic_demo"], True)
        self.assertEqual(response["anomaly_count"], 2)
        self.assertEqual(
            [(item["usage_date"], item["service"]) for item in response["anomalies"]],
            [("2025-03-17", "Cloud Run"), ("2025-03-22", "BigQuery")],
        )

    def test_requires_records_array(self) -> None:
        for payload in ({}, {"records": "not-a-list"}, []):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ValueError, "records array"):
                    analyze_payload(payload)


if __name__ == "__main__":
    unittest.main()
