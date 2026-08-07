-- PostgreSQL control database migration: serving control schema & ledger tables
CREATE SCHEMA IF NOT EXISTS serving;

CREATE SEQUENCE IF NOT EXISTS serving.sync_run_seq AS bigint START WITH 1 INCREMENT BY 1;

CREATE TABLE IF NOT EXISTS serving.sync_runs (
    sync_run_seq bigint PRIMARY KEY DEFAULT nextval('serving.sync_run_seq'),
    sync_run_id text UNIQUE NOT NULL,
    target text NOT NULL DEFAULT 'local' CHECK (target = 'local'),
    operation_type text NOT NULL CHECK (operation_type IN ('SYNC', 'REBUILD')),
    status text NOT NULL CHECK (status IN ('PLANNING', 'WAITING', 'BLOCKED', 'MATERIALIZING', 'VALIDATING', 'READY_TO_PUBLISH', 'PUBLISHED_PENDING_FINALIZATION', 'SUCCEEDED', 'NOOP', 'FAILED_RETRYABLE', 'FAILED_TERMINAL')),
    status_reason text NOT NULL CHECK (status_reason IN ('NONE', 'NO_NEW_TRANSACTION', 'SOURCE_NOT_CAUGHT_UP', 'OPEN_TRANSACTION', 'OPEN_TRANSACTION_STALE', 'REJECTED_TRANSACTION', 'SNAPSHOT_REJECTED', 'ACTIVE_LEASE', 'MATERIALIZATION_MISMATCH', 'PUBLICATION_DRIFT', 'INVARIANT_FAILURE', 'EXECUTION_FAILURE')),
    current_airflow_dag_run_id text,
    attempt_count integer NOT NULL DEFAULT 0,
    expected_active_sync_run_seq bigint NOT NULL DEFAULT 0,
    is_noop boolean NOT NULL DEFAULT false,
    previous_transaction_id text,
    previous_transaction_end_offset bigint,
    target_transaction_id text,
    target_transaction_end_offset bigint,
    source_snapshot_completed boolean NOT NULL DEFAULT false,
    target_offsets_json jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(target_offsets_json) = 'object'),
    iceberg_snapshot_ids_json jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(iceberg_snapshot_ids_json) = 'object'),
    expected_event_count bigint NOT NULL DEFAULT 0,
    materialized_event_count bigint NOT NULL DEFAULT 0,
    expected_entity_counts_json jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(expected_entity_counts_json) = 'object'),
    materialized_entity_counts_json jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(materialized_entity_counts_json) = 'object'),
    report_json jsonb CHECK (report_json IS NULL OR jsonb_typeof(report_json) = 'object'),
    error_details_json jsonb CHECK (error_details_json IS NULL OR jsonb_typeof(error_details_json) = 'object'),
    started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    published_at timestamptz,
    completed_at timestamptz
);

CREATE TABLE IF NOT EXISTS serving.sync_entity_results (
    sync_run_seq bigint NOT NULL REFERENCES serving.sync_runs(sync_run_seq) ON DELETE CASCADE,
    entity text NOT NULL,
    PRIMARY KEY (sync_run_seq, entity),
    status text NOT NULL CHECK (status IN ('PLANNED', 'MATERIALIZED', 'VALIDATED', 'FAILED')),
    expected_event_count bigint NOT NULL DEFAULT 0,
    materialized_event_count bigint NOT NULL DEFAULT 0,
    affected_key_count bigint NOT NULL DEFAULT 0,
    candidate_current_count bigint NOT NULL DEFAULT 0,
    event_checksum text,
    error_code text,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS serving.runtime_state (
    singleton_key integer PRIMARY KEY CHECK (singleton_key = 1),
    target text NOT NULL DEFAULT 'local' CHECK (target = 'local'),
    last_published_sync_run_seq bigint NOT NULL DEFAULT 0,
    last_published_transaction_id text,
    last_published_transaction_end_offset bigint,
    last_published_target_offsets_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    source_snapshot_completed boolean NOT NULL DEFAULT false,
    lease_owner_id text,
    lease_owner_sync_run_seq bigint,
    lease_operation text CHECK (lease_operation IS NULL OR lease_operation IN ('SYNC', 'REBUILD', 'MAINTENANCE')),
    lease_acquired_at timestamptz,
    lease_heartbeat_at timestamptz,
    lease_expires_at timestamptz,
    schedules_activated_at timestamptz,
    row_version bigint NOT NULL DEFAULT 1,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- Seed singleton runtime_state row
INSERT INTO serving.runtime_state (singleton_key)
VALUES (1)
ON CONFLICT (singleton_key) DO NOTHING;
