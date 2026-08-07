-- BigQuery serving-control foundation for the GCP target.
--
-- The migration runner replaces {{ project_id }} with the validated GCP
-- project ID before submission.  The dataset itself is provisioned by
-- Terraform; application tables and their seed rows are SQL-owned.

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.control_state` (
  state_key STRING NOT NULL,
  target STRING NOT NULL,
  next_sync_run_seq INT64 NOT NULL,
  active_sync_run_seq INT64 NOT NULL,
  lease_owner_id STRING,
  lease_operation STRING,
  lease_acquired_at TIMESTAMP,
  lease_heartbeat_at TIMESTAMP,
  lease_expires_at TIMESTAMP,
  row_version INT64 NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'GCP-native serving-control sequence, lease and active predecessor state'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.serving_runs` (
  target STRING NOT NULL,
  sync_run_seq INT64 NOT NULL,
  sync_run_id STRING NOT NULL,
  operation_type STRING NOT NULL,
  status STRING NOT NULL,
  status_reason STRING NOT NULL,
  current_airflow_dag_run_id STRING,
  attempt_count INT64 NOT NULL,
  is_noop BOOL NOT NULL,
  expected_active_sync_run_seq INT64 NOT NULL,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  previous_transaction_id STRING,
  previous_transaction_end_offset INT64,
  target_transaction_id STRING,
  target_transaction_end_offset INT64,
  source_snapshot_completed BOOL NOT NULL,
  target_offsets JSON,
  iceberg_snapshot_ids JSON,
  expected_event_count INT64 NOT NULL,
  materialized_event_count INT64 NOT NULL,
  expected_entity_counts JSON,
  materialized_entity_counts JSON,
  report_json JSON,
  error_code STRING,
  error_message STRING,
  created_at TIMESTAMP NOT NULL,
  build_started_at TIMESTAMP,
  ready_at TIMESTAMP,
  published_at TIMESTAMP,
  failed_at TIMESTAMP,
  conflicted_at TIMESTAMP,
  completed_at TIMESTAMP,
  updated_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'GCP serving runs; sync_run_seq is scoped to the GCP control dataset'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.boundary_offsets` (
  target STRING NOT NULL,
  sync_run_seq INT64 NOT NULL,
  topic STRING NOT NULL,
  partition_id INT64 NOT NULL,
  previous_offset INT64,
  target_offset INT64 NOT NULL,
  transaction_id STRING,
  frozen_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'Frozen Kafka topic-partition offsets for a serving boundary'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.entity_results` (
  target STRING NOT NULL,
  sync_run_seq INT64 NOT NULL,
  entity STRING NOT NULL,
  status STRING NOT NULL,
  expected_event_count INT64 NOT NULL,
  materialized_event_count INT64 NOT NULL,
  affected_key_count INT64 NOT NULL,
  candidate_current_count INT64 NOT NULL,
  event_checksum STRING,
  error_code STRING,
  error_message STRING,
  updated_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'Per-entity validation and materialization results for a GCP run'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.model_results` (
  target STRING NOT NULL,
  sync_run_seq INT64 NOT NULL,
  model_name STRING NOT NULL,
  status STRING NOT NULL,
  candidate_row_count INT64 NOT NULL,
  affected_grain_count INT64 NOT NULL,
  row_checksum STRING,
  error_code STRING,
  error_message STRING,
  updated_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'Per-model dbt build and publication readiness results'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.publication_state` (
  state_key STRING NOT NULL,
  target STRING NOT NULL,
  active_sync_run_seq INT64 NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'Stable GCP publication pointer mirrored from control_state'
);

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_serving_control.schema_migrations` (
  migration_id STRING NOT NULL,
  checksum STRING NOT NULL,
  description STRING NOT NULL,
  applied_at TIMESTAMP NOT NULL
)
OPTIONS (
  description = 'Checksummed, ordered BigQuery migration ledger'
);

MERGE `{{ project_id }}.olist_serving_control.control_state` AS state
USING (
  SELECT
    'gcp' AS state_key,
    'gcp' AS target,
    1 AS next_sync_run_seq,
    0 AS active_sync_run_seq,
    1 AS row_version,
    CURRENT_TIMESTAMP() AS updated_at
) AS seed
ON state.state_key = seed.state_key AND state.target = seed.target
WHEN NOT MATCHED THEN
  INSERT (
    state_key,
    target,
    next_sync_run_seq,
    active_sync_run_seq,
    row_version,
    updated_at
  )
  VALUES (
    seed.state_key,
    seed.target,
    seed.next_sync_run_seq,
    seed.active_sync_run_seq,
    seed.row_version,
    seed.updated_at
  );

MERGE `{{ project_id }}.olist_serving_control.publication_state` AS state
USING (
  SELECT
    'gcp' AS state_key,
    'gcp' AS target,
    0 AS active_sync_run_seq,
    CURRENT_TIMESTAMP() AS updated_at
) AS seed
ON state.state_key = seed.state_key AND state.target = seed.target
WHEN NOT MATCHED THEN
  INSERT (state_key, target, active_sync_run_seq, updated_at)
  VALUES (
    seed.state_key,
    seed.target,
    seed.active_sync_run_seq,
    seed.updated_at
  );
