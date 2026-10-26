resource "google_monitoring_notification_channel" "email" {
  count = var.deploy_workloads ? 1 : 0

  project      = var.project_id
  display_name = "CloudSpend operator email"
  type         = "email"
  force_delete = false
  labels = {
    email_address = var.alert_email
  }

  depends_on = [google_project_service.required]
}

resource "google_monitoring_alert_policy" "workflow_failure" {
  count = var.deploy_workloads ? 1 : 0

  project      = var.project_id
  display_name = "CloudSpend daily workflow failure"
  combiner     = "OR"
  enabled      = true

  documentation {
    mime_type = "text/markdown"
    content   = "The bounded daily workflow finished in a non-success state. Inspect the execution, do not repeatedly rerun it, and verify BigQuery bytes before retrying."
  }

  conditions {
    display_name = "Any failed CloudSpend execution"

    condition_threshold {
      filter = <<-EOT
        resource.type = "workflows.googleapis.com/Workflow"
        AND resource.labels.workflow_id = "cloudspend-daily"
        AND resource.labels.location = "${var.region}"
        AND metric.type = "workflows.googleapis.com/finished_execution_count"
        AND metric.labels.status = "FAILED"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }

      trigger { count = 1 }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].name]

  depends_on = [google_project_service.required]
}
