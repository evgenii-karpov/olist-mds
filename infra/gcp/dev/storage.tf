resource "google_storage_bucket" "lakehouse" {
  name                        = local.bucket_names.lakehouse
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = var.force_destroy_buckets

  versioning {
    enabled = false
  }

  soft_delete_policy {
    retention_duration_seconds = 0
  }

  labels     = local.common_labels
  depends_on = [google_project_service.apis["storage.googleapis.com"]]
}

resource "google_storage_bucket" "checkpoint" {
  name                        = local.bucket_names.checkpoint
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = var.force_destroy_buckets

  versioning {
    enabled = false
  }

  soft_delete_policy {
    retention_duration_seconds = 0
  }

  labels     = local.common_labels
  depends_on = [google_project_service.apis["storage.googleapis.com"]]
}
