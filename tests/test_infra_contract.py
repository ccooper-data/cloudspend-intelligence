from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureGuardrailTests(unittest.TestCase):
    def test_budget_matches_approved_safety_policy(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")

        self.assertIn('default = 25', terraform)
        self.assertIn('display_name    = "cloudspend-v1-safety"', terraform)
        self.assertIn('projects = ["projects/${var.project_id}"]', terraform)
        self.assertEqual(terraform.count("threshold_rules"), 3)
        for threshold in ("0.5", "0.9", "1.0"):
            self.assertIn(f"threshold_percent = {threshold}", terraform)
        self.assertIn("disable_default_iam_recipients = false", terraform)

    def test_query_quota_remains_conservative(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")

        self.assertIn('default = 10737418240', terraform)
        self.assertIn('limit          = urlencode("/d/project")', terraform)
        self.assertIn('force          = false', terraform)


if __name__ == "__main__":
    unittest.main()
