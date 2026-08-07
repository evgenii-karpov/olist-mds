locals {
  common_labels = merge(
    {
      application = "olist-mds"
      environment = var.environment
      managed_by  = "terraform"
    },
    var.labels,
  )

  bucket_names = {
    lakehouse  = coalesce(var.lakehouse_bucket_name, "${var.project_id}-${var.name_prefix}-lakehouse")
    checkpoint = coalesce(var.checkpoint_bucket_name, "${var.project_id}-${var.name_prefix}-checkpoints")
  }

  required_services = toset([
    "biglake.googleapis.com",
    "bigquery.googleapis.com",
    "bigquerystorage.googleapis.com",
    "billingbudgets.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "monitoring.googleapis.com",
    "serviceusage.googleapis.com",
    "storage.googleapis.com",
    "sts.googleapis.com",
  ])

  iceberg_namespaces = toset([
    "bronze",
    "silver",
    "reference",
    "audit",
  ])

  bigquery_datasets = {
    bridge = {
      id          = "olist_lakehouse_bridge"
      description = "Stable read-only bridge views over Lakehouse Iceberg tables."
    }
    gold_store = {
      id          = "olist_gold_store"
      description = "Per-run Gold history/deltas and materialized current state."
    }
    gold = {
      id          = "olist_gold"
      description = "Stable consumer-facing Gold views."
    }
    serving_control = {
      id          = "olist_serving_control"
      description = "GCP-native serving runs, boundaries, results and publication state."
    }
    cloud_test = {
      id          = "olist_cloud_test"
      description = "Disposable vertical-slice and cloud acceptance objects."
    }
  }

  service_account_ids = {
    terraform_deployer = "olist-terraform-deployer"
    spark_writer       = "olist-spark-lakehouse-writer"
    dbt_runner         = "olist-dbt-bigquery-runner"
  }
}
