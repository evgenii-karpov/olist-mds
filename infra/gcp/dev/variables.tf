variable "project_id" {
  description = "Dedicated GCP project ID for the Olist cloud contour."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a 6-30 character lower-case GCP project ID."
  }
}

variable "region" {
  description = "Single supported regional location for the first cloud contour."
  type        = string
  default     = "us-east1"

  validation {
    condition     = var.region == "us-east1"
    error_message = "The first cloud contour is fixed to us-east1."
  }
}

variable "environment" {
  description = "Cloud environment name. Only dev is supported initially."
  type        = string
  default     = "dev"

  validation {
    condition     = var.environment == "dev"
    error_message = "Only the dev environment is supported by this root module."
  }
}

variable "name_prefix" {
  description = "Lower-case resource name prefix used for service accounts and defaults."
  type        = string
  default     = "olist-mds"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{0,18}[a-z0-9]$", var.name_prefix))
    error_message = "name_prefix must be 2-20 lower-case letters, numbers or hyphens."
  }
}

variable "lakehouse_bucket_name" {
  description = "Optional globally unique bucket name for Iceberg data."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = var.lakehouse_bucket_name == null || can(regex(
      "^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$",
      var.lakehouse_bucket_name,
    ))
    error_message = "lakehouse_bucket_name must be a valid 3-63 character GCS bucket name."
  }
}

variable "checkpoint_bucket_name" {
  description = "Optional globally unique bucket name for Spark checkpoints."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = var.checkpoint_bucket_name == null || can(regex(
      "^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$",
      var.checkpoint_bucket_name,
    ))
    error_message = "checkpoint_bucket_name must be a valid 3-63 character GCS bucket name."
  }
}

variable "force_destroy_buckets" {
  description = "Allow dev Terraform destroy to remove bucket contents."
  type        = bool
  default     = true
}

variable "force_destroy_datasets" {
  description = "Allow dev Terraform destroy to remove BigQuery dataset contents."
  type        = bool
  default     = true
}

variable "user_project_override" {
  description = "Bill API requests to the configured project when using user ADC."
  type        = bool
  default     = true
}

variable "billing_account_id" {
  description = "Optional billing account ID used to create the development budget."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = var.billing_account_id == null || can(regex(
      "^[0-9A-Fa-f]{6}-[0-9A-Fa-f]{6}-[0-9A-Fa-f]{6}$",
      var.billing_account_id,
    ))
    error_message = "billing_account_id must use the 6-6-6 billing account format."
  }
}

variable "budget_limit_usd" {
  description = "Monthly notification budget; this is not a hard spend stop."
  type        = number
  default     = 5

  validation {
    condition     = var.budget_limit_usd > 0
    error_message = "budget_limit_usd must be positive."
  }
}

variable "budget_notification_email" {
  description = "Optional email channel for budget updates."
  type        = string
  default     = null
  nullable    = true
}

variable "labels" {
  description = "Additional labels applied to managed resources."
  type        = map(string)
  default     = {}
}
