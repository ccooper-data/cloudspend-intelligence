terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

variable "project_id" { type = string }
variable "billing_account_id" { type = string; sensitive = true }
variable "monthly_budget_usd" { type = number; default = 25 }
variable "daily_query_bytes" { type = number; default = 10737418240 }

provider "google" { project = var.project_id }

# This quota is a guardrail, not a guarantee against charges.
resource "google_service_usage_consumer_quota_override" "bigquery_daily_bytes" {
  project        = var.project_id
  service        = "bigquery.googleapis.com"
  metric         = urlencode("bigquery.googleapis.com/quota/query/usage")
  limit          = urlencode("/d/project")
  override_value = tostring(var.daily_query_bytes)
  force          = false
}

resource "google_billing_budget" "monthly" {
  billing_account = var.billing_account_id
  display_name    = "cloudspend-v1-safety"
  budget_filter { projects = ["projects/${var.project_id}"] }
  amount { specified_amount { currency_code = "USD" units = tostring(var.monthly_budget_usd) } }
  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.9 }
  threshold_rules { threshold_percent = 1.0 }

  all_updates_rule {
    disable_default_iam_recipients = false
  }
}

