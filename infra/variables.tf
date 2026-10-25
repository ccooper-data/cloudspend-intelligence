variable "project_id" {
  description = "Dedicated GCP project ID."
  type        = string
}

variable "billing_account_id" {
  description = "Billing account used only to create the project-scoped warning budget."
  type        = string
  sensitive   = true
}

variable "monthly_budget_usd" {
  description = "Warning budget; this is not permission to spend."
  type        = number
  default     = 25
}

variable "daily_query_bytes" {
  description = "Project-wide BigQuery on-demand query quota in bytes per day."
  type        = number
  default     = 10737418240
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
  default     = ""

  validation {
    condition     = !var.deploy_workloads || can(regex("^[0-9]+$", var.github_repository_owner_id))
    error_message = "Set the numeric GitHub repository owner ID before enabling workloads."
  }
}
