# Resource and Schema Inventory

## GCP resources

```text
Project: dedicated olist-mds project
Region: us-east1

GCS:
  Terraform state bucket (manual, versioned, survives main destroy)
  Lakehouse bucket (STANDARD, no soft delete/versioning/lifecycle)
  Checkpoint bucket (STANDARD, no soft delete/versioning/lifecycle)

Lakehouse runtime catalog:
  one multiple-bucket / credential-vending catalog
  namespaces: bronze, silver, reference, audit

BigQuery datasets:
  olist_lakehouse_bridge
  olist_gold_store
  olist_gold
  olist_serving_control
  olist_cloud_test

Service accounts:
  olist-terraform-deployer
  olist-spark-lakehouse-writer
  olist-dbt-bigquery-runner
```

## BigQuery control-table minimum

```text
serving_runs
boundary_offsets
entity_results
model_results
publication_state
schema_migrations
```

Suggested `serving_runs` fields include:

```text
sync_run_seq
sync_run_id
status
target
previous_boundary_id
current_boundary_id
expected_active_sync_run_seq
created_at
build_started_at
ready_at
published_at
failed_at
conflicted_at
error_code
error_message
```

## Per-model Gold objects

For every logical model:

```text
olist_gold_store.<model>__history
olist_gold_store.<model>__current
olist_gold.<model>
```

History includes `sync_run_seq`, `operation_type`, model grain, payload, source interval, and build metadata.
