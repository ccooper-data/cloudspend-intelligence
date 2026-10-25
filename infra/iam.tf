data "google_project" "current" {
  project_id = var.project_id
}

resource "google_service_account" "api_runtime" {
  count = var.deploy_workloads ? 1 : 0

  project      = var.project_id
  account_id   = "cloudspend-api-runtime"
  display_name = "CloudSpend API runtime"
}

resource "google_service_account" "workflow" {
  count = var.deploy_workloads ? 1 : 0

  project      = var.project_id
  account_id   = "cloudspend-workflow"
  display_name = "CloudSpend daily workflow"
}

resource "google_service_account" "scheduler" {
  count = var.deploy_workloads ? 1 : 0

  project      = var.project_id
  account_id   = "cloudspend-scheduler"
  display_name = "CloudSpend daily scheduler"
}

resource "google_service_account" "github_deployer" {
  count = var.create_deployment_identity ? 1 : 0

  project      = var.project_id
  account_id   = "cloudspend-github"
  display_name = "Keyless GitHub Actions deployer"
}

resource "google_iam_workload_identity_pool" "github" {
  count = var.create_deployment_identity ? 1 : 0

  project                   = var.project_id
  workload_identity_pool_id = "github-actions"
  display_name              = "GitHub Actions"
  description               = "Keyless federation for the CloudSpend repository only."

  depends_on = [google_project_service.identity]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  count = var.create_deployment_identity ? 1 : 0

  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github[0].workload_identity_pool_id
  workload_identity_pool_provider_id = "cloudspend-main"
  display_name                       = "CloudSpend main branch"

  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.repository"          = "assertion.repository"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
    "attribute.ref"                 = "assertion.ref"
  }

  attribute_condition = "assertion.repository == '${var.github_repository}' && assertion.repository_owner_id == '${var.github_repository_owner_id}' && assertion.ref == 'refs/heads/main'"

  oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
}

resource "google_service_account_iam_member" "github_federation" {
  count = var.create_deployment_identity ? 1 : 0

  service_account_id = google_service_account.github_deployer[0].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${data.google_project.current.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.github[0].workload_identity_pool_id}/attribute.repository/${var.github_repository}"
}

locals {
  github_deployer_roles = toset([
    "roles/artifactregistry.admin",
    "roles/bigquery.dataOwner",
    "roles/bigquery.jobUser",
    "roles/cloudscheduler.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/monitoring.alertPolicyEditor",
    "roles/monitoring.notificationChannelEditor",
    "roles/resourcemanager.projectIamAdmin",
    "roles/run.admin",
    "roles/serviceusage.serviceUsageAdmin",
    "roles/workflows.admin",
  ])
}

# These bootstrap permissions are bounded to one project and an environment-
# protected, main-branch-only GitHub identity. No user-managed key is created.
resource "google_project_iam_member" "github_deployer" {
  for_each = var.create_deployment_identity ? local.github_deployer_roles : toset([])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_deployer[0].email}"
}

# Runtime access is data-plane only. No owner/editor roles are granted.
resource "google_project_iam_member" "api_bigquery_job_user" {
  count = var.deploy_workloads ? 1 : 0

  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.api_runtime[0].email}"
}

resource "google_bigquery_dataset_iam_member" "api_data_viewer" {
  count = var.deploy_workloads ? 1 : 0

  project    = var.project_id
  dataset_id = google_bigquery_dataset.cloudspend[0].dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.api_runtime[0].email}"
}

resource "google_project_iam_member" "workflow_bigquery_job_user" {
  count = var.deploy_workloads ? 1 : 0

  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.workflow[0].email}"
}

resource "google_bigquery_dataset_iam_member" "workflow_data_editor" {
  count = var.deploy_workloads ? 1 : 0

  project    = var.project_id
  dataset_id = google_bigquery_dataset.cloudspend[0].dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.workflow[0].email}"
}

resource "google_project_iam_member" "scheduler_workflow_invoker" {
  count = var.deploy_workloads ? 1 : 0

  project = var.project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.scheduler[0].email}"
}
