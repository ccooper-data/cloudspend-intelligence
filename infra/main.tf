terraform {
  required_version = ">= 1.6.0"
  backend "gcs" {}

  required_providers {
    google = { source = "hashicorp/google", version = "~> 7.0" }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 7.0"
    }
  }
}

provider "google" { project = var.project_id }
provider "google-beta" { project = var.project_id }

# This quota is a guardrail, not a guarantee against charges.
resource "google_service_usage_consumer_quota_override" "bigquery_daily_bytes" {
  provider       = google-beta
  count          = var.deploy_workloads ? 1 : 0
  project        = var.project_id
  service        = "bigquery.googleapis.com"
  metric         = urlencode("bigquery.googleapis.com/quota/query/usage")
  limit          = urlencode("/d/project")
  override_value = tostring(var.daily_query_mib)
  force          = false
}

resource "google_billing_budget" "monthly" {
  count = var.manage_budget ? 1 : 0

  billing_account = var.billing_account_id
  display_name    = "cloudspend-v1-safety"
  budget_filter { projects = ["projects/${data.google_project.current.number}"] }
  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.monthly_budget_usd)
    }
  }
  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.9 }
  threshold_rules { threshold_percent = 1.0 }

  all_updates_rule {
    monitoring_notification_channels = []
    disable_default_iam_recipients   = false
  }
}

