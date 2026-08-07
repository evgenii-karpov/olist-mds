resource "google_service_account" "accounts" {
  for_each = local.service_account_ids

  project      = var.project_id
  account_id   = each.value
  display_name = "Olist MDS ${each.key}"
  description  = "Role-specific identity for the Olist MDS GCP contour."
}

resource "google_project_iam_member" "terraform_deployer" {
  for_each = toset([
    "roles/biglake.admin",
    "roles/bigquery.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/monitoring.admin",
    "roles/serviceusage.serviceUsageAdmin",
    "roles/storage.admin",
  ])

  project = var.project_id
  role    = each.value
  member  = google_service_account.accounts["terraform_deployer"].member
}

resource "google_project_iam_member" "spark_catalog_viewer" {
  project = var.project_id
  role    = "roles/biglake.viewer"
  member  = google_service_account.accounts["spark_writer"].member
}

resource "google_project_iam_member" "dbt_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = google_service_account.accounts["dbt_runner"].member
}

resource "google_storage_bucket_iam_member" "spark_checkpoint_writer" {
  bucket = google_storage_bucket.checkpoint.name
  role   = "roles/storage.objectAdmin"
  member = google_service_account.accounts["spark_writer"].member
}

resource "google_storage_bucket_iam_member" "catalog_vending_storage_admin" {
  bucket = google_storage_bucket.lakehouse.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_biglake_iceberg_catalog.lakehouse.biglake_service_account}"
}

resource "google_bigquery_dataset_iam_member" "dbt_dataset_roles" {
  for_each = {
    bridge          = "roles/bigquery.dataViewer"
    gold            = "roles/bigquery.dataViewer"
    gold_store      = "roles/bigquery.dataEditor"
    serving_control = "roles/bigquery.dataEditor"
    cloud_test      = "roles/bigquery.dataEditor"
  }

  project    = var.project_id
  dataset_id = google_bigquery_dataset.datasets[each.key].dataset_id
  role       = each.value
  member     = google_service_account.accounts["dbt_runner"].member
}
