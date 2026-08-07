output "project_id" {
  description = "Managed GCP project ID."
  value       = var.project_id
}

output "region" {
  description = "Managed regional location."
  value       = var.region
}

output "lakehouse_bucket" {
  description = "GCS bucket used by the Lakehouse runtime catalog."
  value       = google_storage_bucket.lakehouse.name
}

output "checkpoint_bucket" {
  description = "GCS bucket used only for Spark checkpoints."
  value       = google_storage_bucket.checkpoint.name
}

output "lakehouse_catalog_id" {
  description = "BigLake Iceberg catalog ID."
  value       = google_biglake_iceberg_catalog.lakehouse.name
}

output "lakehouse_catalog_uri" {
  description = "BigLake Iceberg REST catalog endpoint."
  value       = "https://biglake.googleapis.com/iceberg/v1/restcatalog"
}

output "lakehouse_warehouse" {
  description = "Warehouse URI for the BigLake runtime catalog."
  value       = "bl://projects/${var.project_id}/catalogs/${google_biglake_iceberg_catalog.lakehouse.name}"
}

output "service_accounts" {
  description = "Role-specific service account emails; no keys are generated."
  value = {
    for name, account in google_service_account.accounts : name => account.email
  }
}

output "bigquery_datasets" {
  description = "Managed BigQuery application datasets."
  value = {
    for name, dataset in google_bigquery_dataset.datasets : name => dataset.dataset_id
  }
}
