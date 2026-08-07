resource "google_bigquery_dataset" "datasets" {
  for_each = local.bigquery_datasets

  project                    = var.project_id
  dataset_id                 = each.value.id
  friendly_name              = each.value.id
  description                = each.value.description
  location                   = var.region
  delete_contents_on_destroy = var.force_destroy_datasets
  labels                     = local.common_labels
  max_time_travel_hours      = 48
  depends_on                 = [google_project_service.apis["bigquery.googleapis.com"]]
}
