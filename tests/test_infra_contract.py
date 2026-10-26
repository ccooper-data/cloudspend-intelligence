from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureGuardrailTests(unittest.TestCase):
    def test_budget_matches_approved_safety_policy(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")

        self.assertIn('default     = 25', variables)
        self.assertIn('variable "manage_budget"', variables)
        self.assertIn('count = var.manage_budget ? 1 : 0', terraform)
        self.assertIn('display_name    = "cloudspend-v1-safety"', terraform)
        self.assertIn('projects = ["projects/${data.google_project.current.number}"]', terraform)
        self.assertEqual(terraform.count("threshold_rules"), 3)
        for threshold in ("0.5", "0.9", "1.0"):
            self.assertIn(f"threshold_percent = {threshold}", terraform)
        self.assertRegex(terraform, r"disable_default_iam_recipients\s*=\s*false")

    def test_query_quota_remains_conservative(self) -> None:
        terraform = (ROOT / "infra" / "main.tf").read_text(encoding="utf-8")
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")

        self.assertIn('variable "daily_query_mib"', variables)
        self.assertIn('default     = 10240', variables)
        self.assertIn('limit          = urlencode("/d/project")', terraform)
        self.assertIn('force          = false', terraform)
        self.assertIn('count          = var.deploy_workloads ? 1 : 0', terraform)

    def test_workloads_are_off_by_default_and_image_is_immutable(self) -> None:
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")
        platform = (ROOT / "infra" / "platform.tf").read_text(encoding="utf-8")
        iam = (ROOT / "infra" / "iam.tf").read_text(encoding="utf-8")

        self.assertIn('variable "deploy_workloads"', variables)
        self.assertIn('default     = false', variables)
        self.assertIn('check "identity_precedes_workloads"', variables)
        self.assertIn('@sha256:[0-9a-f]{64}$', variables)
        self.assertIn('min_instance_count = 0', platform)
        self.assertIn('max_instance_count = 1', platform)
        self.assertNotIn('allUsers', platform)
        self.assertNotIn('allAuthenticatedUsers', platform)
        self.assertNotIn('api_bigquery_job_user', iam)
        self.assertNotIn('api_data_viewer', iam)
        self.assertIn('google_cloud_run_v2_service_iam_member" "github_invoker', platform)

    def test_github_federation_is_keyless_and_repo_scoped(self) -> None:
        iam = (ROOT / "infra" / "iam.tf").read_text(encoding="utf-8")

        self.assertIn('issuer_uri = "https://token.actions.githubusercontent.com"', iam)
        self.assertIn("assertion.repository == '${var.github_repository}'", iam)
        self.assertIn("assertion.repository_owner_id == '${var.github_repository_owner_id}'", iam)
        self.assertIn("assertion.ref == 'refs/heads/main'", iam)
        self.assertIn('"attribute.environment"', iam)
        self.assertIn("assertion.environment == '${var.github_environment}'", iam)
        self.assertIn('principalSet://iam.googleapis.com/', iam)
        self.assertIn('/attribute.environment/${var.github_environment}', iam)
        self.assertNotIn('google_project_iam_member" "github_deployer', iam)
        self.assertNotIn('google_service_account_key', iam)

        check = (ROOT / ".github" / "workflows" / "gcp-identity-check.yml").read_text(encoding="utf-8")
        self.assertIn('id-token: write', check)
        self.assertIn('environment: gcp-demo', check)
        self.assertIn('google-github-actions/auth@v3', check)
        self.assertIn('gcloud auth print-access-token >/dev/null', check)
        self.assertNotIn('service_account_key', check)

    def test_daily_automation_is_bounded_and_idempotent(self) -> None:
        platform = (ROOT / "infra" / "platform.tf").read_text(encoding="utf-8")
        variables = (ROOT / "infra" / "variables.tf").read_text(encoding="utf-8")
        iam = (ROOT / "infra" / "iam.tf").read_text(encoding="utf-8")
        workflow = (ROOT / "infra" / "workflow.yaml.tftpl").read_text(encoding="utf-8")
        sql = (ROOT / "sql" / "detect_anomalies_bigquery.sql").read_text(encoding="utf-8")

        self.assertIn('variable "enable_scheduler"', variables)
        self.assertIn('check "scheduler_requires_workloads"', variables)
        self.assertIn('var.deploy_workloads && var.enable_scheduler', platform)
        self.assertIn('var.deploy_workloads && var.enable_scheduler', iam)
        self.assertNotIn('"cloudscheduler.googleapis.com",\n    "workflowexecutions.googleapis.com"', platform)
        self.assertIn('schedule         = "0 6 * * *"', platform)
        self.assertIn('retry_count          = 1', platform)
        self.assertIn('attempt_deadline = "60s"', platform)
        self.assertIn('maximumBytesBilled: "10737418240"', workflow)
        self.assertIn('force_failure', workflow)
        self.assertIn('CONTROLLED_TEST_FAILURE: no BigQuery job was submitted', workflow)
        self.assertIn('- fail_incomplete:', workflow)
        self.assertNotIn('next: return_result\n        raise:', workflow)
        self.assertIn('CREATE OR REPLACE TABLE', sql)
        self.assertIn('LEFT JOIN service_daily AS prior', sql)
        self.assertIn('WHERE history_days = 14', sql)
        self.assertIn('daily_cost > median_cost * 1.50', sql)
        self.assertIn('daily_cost - median_cost > 25.00', sql)
        self.assertIn('ORDER BY contributor_cost DESC, project_id ASC, sku ASC', sql)
        self.assertNotIn(' AS current', sql)

    def test_manual_workflow_deploy_and_run_are_explicit(self) -> None:
        deploy = (ROOT / ".github" / "workflows" / "gcp-workflow-deploy.yml").read_text(encoding="utf-8")
        run = (ROOT / ".github" / "workflows" / "gcp-workflow-run.yml").read_text(encoding="utf-8")
        renderer = (ROOT / "scripts" / "render_workflow.py").read_text(encoding="utf-8")

        for workflow in (deploy, run):
            self.assertIn('environment: gcp-demo', workflow)
            self.assertIn('id-token: write', workflow)
            self.assertIn('google-github-actions/auth@v3', workflow)
            self.assertNotIn('service_account_key', workflow)
            self.assertNotIn('cloud scheduler', workflow.lower())
        self.assertIn("inputs.confirm == 'DEPLOY_MANUAL_WORKFLOW'", deploy)
        self.assertIn('gcloud workflows deploy cloudspend-daily', deploy)
        self.assertIn('--call-log-level=log-errors-only', deploy)
        self.assertIn("inputs.confirm == 'RUN_MANUAL_WORKFLOW'", run)
        self.assertIn('gcloud workflows run cloudspend-daily', run)
        self.assertIn('--maximum_bytes_billed=104857600', run)
        self.assertIn('.replace("$${", "${")', renderer)

        failure = (ROOT / ".github" / "workflows" / "gcp-workflow-failure-test.yml").read_text(encoding="utf-8")
        self.assertIn("inputs.confirm == 'TEST_CONTROLLED_FAILURE'", failure)
        self.assertIn('environment: gcp-demo', failure)
        self.assertIn('id-token: write', failure)
        self.assertIn('"force_failure":true', failure)
        self.assertIn('\"state\": \"FAILED\"', failure)
        self.assertNotIn('test "$status" -ne 0', failure)
        self.assertNotIn('cloud scheduler', failure.lower())

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
        self.assertIn('google-github-actions/auth@v3', workflow)
        self.assertIn('terraform -chdir=infra plan', workflow)
        self.assertNotIn('terraform -chdir=infra apply', workflow)
        self.assertNotIn('service_account_key', workflow)

    def test_ci_builds_a_non_root_container_and_checks_health(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn('docker build --tag cloudspend-api:ci .', workflow)
        self.assertIn('--entrypoint id cloudspend-api:ci -u', workflow)
        self.assertIn('http://127.0.0.1:8080/v1/health', workflow)

    def test_cloud_run_demo_deployment_is_private_and_bounded(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "gcp-cloud-run-deploy.yml").read_text(encoding="utf-8")

        self.assertIn("inputs.confirm == 'DEPLOY_PRIVATE_DEMO'", workflow)
        self.assertIn('environment: gcp-demo', workflow)
        self.assertIn('id-token: write', workflow)
        self.assertIn('us-central1-docker.pkg.dev/cloudspend-intelligence-v1/cloudspend-api/', workflow)
        self.assertIn('@$digest', workflow)
        self.assertIn('--revision-suffix=r${{ github.run_id }}', workflow)
        self.assertIn('--service-account=cloudspend-api-runtime@', workflow)
        self.assertIn('--min=0', workflow)
        self.assertIn('--max=1', workflow)
        self.assertIn('--cpu-throttling', workflow)
        self.assertNotIn('--allow-unauthenticated', workflow)

    def test_cloud_run_live_validation_requires_authentication(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "gcp-cloud-run-validate.yml").read_text(encoding="utf-8")

        self.assertIn("inputs.confirm == 'VALIDATE_PRIVATE_API'", workflow)
        self.assertIn('environment: gcp-demo', workflow)
        self.assertIn('id-token: write', workflow)
        self.assertIn('token_format: id_token', workflow)
        self.assertIn("'.status.url'", workflow)
        self.assertIn('id_token_audience: ${{ steps.service.outputs.status_url }}', workflow)
        self.assertIn('id_token_audience: ${{ steps.service.outputs.project_url }}', workflow)
        self.assertIn('status.url matched-audience response', workflow)
        self.assertIn('project-number matched-audience response', workflow)
        self.assertIn("printf 'STATUS_URL_Q=%q", workflow)
        self.assertIn("STATUS_URL_HEX=", workflow)
        self.assertIn('curl --verbose', workflow)
        self.assertIn('Authorization: Bearer $STATUS_TOKEN', workflow)
        self.assertIn('$STATUS_URL/v1/health', workflow)
        self.assertNotIn('X-Serverless-Authorization', workflow)
        self.assertIn('401|403|404', workflow)
        self.assertIn('result["anomaly_count"] == 2', workflow)
        self.assertIn('2025-03-17', workflow)
        self.assertIn('2025-03-22', workflow)

    def test_live_loader_is_project_locked_and_bounded(self) -> None:
        loader = (ROOT / "scripts" / "load_and_validate_gcp.sh").read_text(encoding="utf-8")
        validation = (ROOT / "sql" / "validate_live.sql").read_text(encoding="utf-8")

        self.assertIn('cloudspend-intelligence-v1', loader)
        self.assertIn('LOAD_SYNTHETIC_DATA', loader)
        self.assertIn('--maximum_bytes_billed=104857600', loader)
        self.assertIn('COUNT(*) = 540', validation)
        self.assertIn('COUNT(*) = 2', validation)
        self.assertIn("DATE '2025-03-17' AND service = 'Cloud Run'", validation)
        self.assertIn("DATE '2025-03-22' AND service = 'BigQuery'", validation)

        live_workflow = (ROOT / ".github" / "workflows" / "gcp-bigquery-validate.yml").read_text(encoding="utf-8")
        self.assertIn("inputs.confirm == 'LOAD_SYNTHETIC_DATA'", live_workflow)
        self.assertIn('environment: gcp-demo', live_workflow)
        self.assertIn('id-token: write', live_workflow)
        self.assertIn('./scripts/load_and_validate_gcp.sh LOAD_SYNTHETIC_DATA', live_workflow)


if __name__ == "__main__":
    unittest.main()
