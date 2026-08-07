resource "google_biglake_iceberg_catalog" "lakehouse" {
  project         = var.project_id
  name            = google_storage_bucket.lakehouse.name
  catalog_type    = "CATALOG_TYPE_GCS_BUCKET"
  credential_mode = "CREDENTIAL_MODE_VENDED_CREDENTIALS"

  depends_on = [
    google_project_service.apis["biglake.googleapis.com"],
    google_storage_bucket.lakehouse,
  ]
}

resource "google_biglake_iceberg_namespace" "namespaces" {
  for_each = local.iceberg_namespaces

  project      = var.project_id
  catalog      = google_biglake_iceberg_catalog.lakehouse.name
  namespace_id = each.value
  properties = {
    location = "gs://${google_storage_bucket.lakehouse.name}/${each.value}"
  }
}
