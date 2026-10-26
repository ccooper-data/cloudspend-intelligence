variable "project_id" {
  description = "Dedicated GCP project ID."
  type        = string
}

variable "billing_account_id" {
  description = "Billing account used only when Terraform is explicitly managing the warning budget."
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = !var.manage_budget || length(trimspace(var.billing_account_id)) > 0
    error_message = "Set billing_account_id only when manage_budget is true."
  }
}

variable "manage_budget" {
  description = "Manage the warning budget in Terraform. Leave false when adopting a budget created during the manual cost gate."
  type        = bool
  default     = false
}

variable "monthly_budget_usd" {
  description = "Warning budget; this is not permission to spend."
  type        = number
  default     = 25
}

variable "daily_query_mib" {
  description = "Project-wide BigQuery on-demand query quota in MiB per day."
  type        = number
  default     = 10240
}

variable "region" {
  description = "Single region used by the portfolio deployment."
  type        = string
  default     = "us-central1"
}

variable "deploy_workloads" {
  description = "Explicit safety gate. Keep false until the budget and quotas are verified."
  type        = bool
  default     = false
}

variable "enable_scheduler" {
  description = "Separate opt-in gate for automatic daily execution. Keep false during manual validation."
  type        = bool
  default     = false
}

check "scheduler_requires_workloads" {
  assert {
    condition     = !var.enable_scheduler || var.deploy_workloads
    error_message = "Cloud Scheduler cannot be enabled unless workloads are explicitly enabled."
  }
}

variable "create_deployment_identity" {
  description = "Separate bootstrap gate for the keyless GitHub deployment identity."
  type        = bool
  default     = false
}

check "identity_precedes_workloads" {
  assert {
    condition     = !var.deploy_workloads || var.create_deployment_identity
    error_message = "Workloads require the keyless deployment identity gate to be enabled."
  }
}

variable "container_image" {
  description = "Immutable Artifact Registry image digest for the Cloud Run API."
  type        = string
  default     = ""

  validation {
    condition     = !var.deploy_workloads || can(regex("@sha256:[0-9a-f]{64}$", var.container_image))
    error_message = "When deploy_workloads is true, container_image must be pinned by sha256 digest."
  }
}

variable "github_repository" {
  description = "Only this GitHub repository may exchange OIDC tokens."
  type        = string
  default     = "ccooper-data/cloudspend-intelligence"
}

variable "github_repository_owner_id" {
  description = "Numeric GitHub owner ID used to prevent organization-name reuse attacks."
  type        = string
  default     = "314428882"

  validation {
    condition     = !(var.deploy_workloads || var.create_deployment_identity) || can(regex("^[0-9]+$", var.github_repository_owner_id))
    error_message = "Set the numeric GitHub repository owner ID before enabling workloads."
  }
}

variable "github_environment" {
  description = "GitHub environment included in the OIDC subject for the demo identity."
  type        = string
  default     = "gcp-demo"
}

variable "alert_email" {
  description = "Operational alert recipient. Supply via an uncommitted tfvars file."
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = !var.deploy_workloads || can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.alert_email))
    error_message = "Set a valid operational alert email before enabling workloads."
  }
}
