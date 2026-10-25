from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureGuardrailTests(unittest.TestCase):
    def test_budget_matches_approved_safety_policy(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")

        self.assertIn('default     = 25', variables)
        self.assertIn('display_name    = "cloudspend-v1-safety"', terraform)
        self.assertIn('projects = ["projects/${var.project_id}"]', terraform)
        self.assertEqual(terraform.count("threshold_rules"), 3)
        for threshold in ("0.5", "0.9", "1.0"):
            self.assertIn(f"threshold_percent = {threshold}", terraform)
        self.assertIn("disable_default_iam_recipients = false", terraform)

    def test_query_quota_remains_conservative(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")

        self.assertIn('default     = 10737418240', variables)
        self.assertIn('limit          = urlencode("/d/project")', terraform)
        self.assertIn('force          = false', terraform)
        self.assertIn('count          = var.deploy_workloads ? 1 : 0', terraform)

    def test_workloads_are_off_by_default_and_image_is_immutable(self) -> None:
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")
        platform = (ROOT / "infra" / "platform.tf").read_text(encoding="utf-8")

        self.assertIn('variable "deploy_workloads"', variables)
        self.assertIn('default     = false', variables)
        self.assertIn('@sha256:[0-9a-f]{64}$', variables)
        self.assertIn('min_instance_count = 0', platform)
        self.assertIn('max_instance_count = 1', platform)
        self.assertNotIn('allUsers', platform)
        self.assertNotIn('allAuthenticatedUsers', platform)

    def test_github_federation_is_keyless_and_repo_scoped(self) -> None:
        iam = (ROOT / "infra" / "iam.tf").read_text(encoding="utf-8")

        self.assertIn('issuer_uri = "https://token.actions.githubusercontent.com"', iam)
        self.assertIn("assertion.repository == '${var.github_repository}'", iam)
        self.assertIn("assertion.repository_owner_id == '${var.github_repository_owner_id}'", iam)
        self.assertIn("assertion.ref == 'refs/heads/main'", iam)
        self.assertNotIn('google_service_account_key', iam)

    def test_daily_automation_is_bounded_and_idempotent(self) -> None:
        platform = (ROOT / "infra" / "platform.tf").read_text(encoding="utf-8")
        workflow = (ROOT / "infra" / "workflow.yaml.tftpl").read_text(encoding="utf-8")
        sql = (ROOT / "sql" / "detect_anomalies_bigquery.sql").read_text(encoding="utf-8")

        self.assertIn('schedule         = "0 6 * * *"', platform)
        self.assertIn('retry_count          = 1', platform)
        self.assertIn('attempt_deadline = "60s"', platform)
        self.assertIn('maximumBytesBilled: "10737418240"', workflow)
        self.assertIn('CREATE OR REPLACE TABLE', sql)
        self.assertIn('ARRAY_LENGTH(prior_days) = 14', sql)
        self.assertIn('daily_cost > median_cost * 1.50', sql)
        self.assertIn('daily_cost - median_cost > 25.00', sql)
        self.assertIn('ORDER BY contributor_cost DESC, project_id ASC, sku ASC', sql)

    def test_monitoring_detects_failed_workflow_executions(self) -> None:
        monitoring = (ROOT / "infra" / "monitoring.tf").read_text(encoding="utf-8")

        self.assertIn('finished_execution_count', monitoring)
        self.assertIn('metric.labels.status != "SUCCEEDED"', monitoring)
        self.assertIn('threshold_value = 0', monitoring)
        self.assertIn('notification_channels', monitoring)

    def test_github_cloud_workflow_can_only_plan(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "gcp-plan.yml").read_text(encoding="utf-8")

        self.assertIn('id-token: write', workflow)
        self.assertIn("inputs.confirm == 'PLAN'", workflow)
        self.assertIn('google-github-actions/auth@v2', workflow)
        self.assertIn('terraform -chdir=infra plan', workflow)
        self.assertNotIn('terraform -chdir=infra apply', workflow)
        self.assertNotIn('service_account_key', workflow)


if __name__ == "__main__":
    unittest.main()
