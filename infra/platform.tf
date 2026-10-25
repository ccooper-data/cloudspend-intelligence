locals {
  identity_services = toset([
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
  ])

  required_services = toset([
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "monitoring.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "workflowexecutions.googleapis.com",
    "workflows.googleapis.com",
  ])
}

resource "google_project_service" "identity" {
  for_each = var.create_deployment_identity ? local.identity_services : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "required" {
  for_each = var.deploy_workloads ? local.required_services : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_bigquery_dataset" "cloudspend" {
  count = var.deploy_workloads ? 1 : 0

  project                    = var.project_id
  dataset_id                 = "cloudspend_v1"
  friendly_name              = "CloudSpend Intelligence V1"
  description                = "Synthetic GCP-style billing data and deterministic anomaly results."
  location                   = "US"
  delete_contents_on_destroy = true

  labels = {
    data_classification = "synthetic"
    environment         = "portfolio"
  }

  depends_on = [google_project_service.required]
}

resource "google_bigquery_table" "billing_records" {
  count = var.deploy_workloads ? 1 : 0

  project             = var.project_id
  dataset_id          = google_bigquery_dataset.cloudspend[0].dataset_id
  table_id            = "billing_records"
  description         = "Explicitly synthetic daily billing records."
  deletion_protection = false
  schema              = file("${path.module}/schemas/billing_records.json")

  labels = { data_classification = "synthetic" }
}

resource "google_bigquery_table" "anomalies" {
  count = var.deploy_workloads ? 1 : 0

  project             = var.project_id
  dataset_id          = google_bigquery_dataset.cloudspend[0].dataset_id
  table_id            = "anomalies"
  description         = "Deterministic anomaly results with project and SKU attribution."
  deletion_protection = false
  schema              = file("${path.module}/schemas/anomalies.json")
}

resource "google_artifact_registry_repository" "api" {
  count = var.deploy_workloads ? 1 : 0

  project       = var.project_id
  location      = var.region
  repository_id = "cloudspend-api"
  description   = "Container images for the deterministic explanation API."
  format        = "DOCKER"

  cleanup_policies {
    id     = "retain-three-versions"
    action = "KEEP"
    most_recent_versions { keep_count = 3 }
  }

  cleanup_policies {
    id     = "delete-older-versions"
    action = "DELETE"
    condition { tag_state = "ANY" }
  }

  depends_on = [google_project_service.required]
}

resource "google_cloud_run_v2_service" "api" {
  count = var.deploy_workloads ? 1 : 0

  project             = var.project_id
  name                = "cloudspend-api"
  location            = var.region
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    service_account                  = google_service_account.api_runtime[0].email
    timeout                          = "60s"
    max_instance_request_concurrency = 10

    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    containers {
      image = var.container_image

      ports { container_port = 8080 }

      resources {
        cpu_idle = true
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }

      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 2
        period_seconds        = 5
        failure_threshold     = 6
        http_get { path = "/healthz" }
      }
    }
  }

  depends_on = [google_project_service.required]
}

# Public IAM principals are deliberately absent.
resource "google_cloud_run_v2_service_iam_member" "workflow_invoker" {
  count = var.deploy_workloads ? 1 : 0

  project  = var.project_id
  location = google_cloud_run_v2_service.api[0].location
  name     = google_cloud_run_v2_service.api[0].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.workflow[0].email}"
}

resource "google_workflows_workflow" "daily" {
  count = var.deploy_workloads ? 1 : 0

  project             = var.project_id
  name                = "cloudspend-daily"
  region              = var.region
  description         = "Bounded, idempotent daily anomaly processing."
  service_account     = google_service_account.workflow[0].id
  deletion_protection = false
  call_log_level      = "LOG_ERRORS_ONLY"

  source_contents = templatefile("${path.module}/workflow.yaml.tftpl", {
    project_id          = var.project_id
    detector_query_json = jsonencode(templatefile("${path.module}/../sql/detect_anomalies_bigquery.sql", {
      project_id = var.project_id
    }))
  })

  depends_on = [google_project_service.required]
}

resource "google_cloud_scheduler_job" "daily" {
  count = var.deploy_workloads ? 1 : 0

  project          = var.project_id
  region           = var.region
  name             = "cloudspend-daily"
  description      = "One bounded CloudSpend run per day."
  schedule         = "0 6 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "60s"

  retry_config {
    retry_count          = 1
    max_retry_duration   = "120s"
    min_backoff_duration = "10s"
    max_backoff_duration = "30s"
    max_doublings        = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.daily[0].id}/executions"
    body        = base64encode(jsonencode({ argument = jsonencode({ trigger = "scheduler" }) }))

    headers = { "Content-Type" = "application/json" }

    oauth_token {
      service_account_email = google_service_account.scheduler[0].email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }

  depends_on = [google_project_service.required]
}
