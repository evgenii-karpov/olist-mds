-- Audit tables for local PostgreSQL load and dbt observability.

create table if not exists audit.load_runs (
    load_run_id varchar(128) not null,
    batch_id varchar(128) not null,
    entity_name varchar(128) not null,
    source_uri varchar(1024),
    target_table varchar(256) not null,
    status varchar(32) not null,
    rows_loaded bigint,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);

create table if not exists audit.dbt_runs (
    dbt_run_id varchar(128) not null,
    batch_id varchar(128) not null,
    command varchar(1024) not null,
    status varchar(32) not null,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);

create table if not exists audit.batch_runs (
    batch_id varchar(128) not null,
    batch_date date not null,
    orchestration_run_id varchar(128) not null,
    dag_id varchar(256),
    status varchar(64) not null,
    started_at timestamp not null,
    updated_at timestamp not null,
    finished_at timestamp,
    raw_manifest_uri varchar(1024),
    correction_manifest_uri varchar(1024),
    error_message varchar(65535)
);

create table if not exists audit.batch_reconciliation (
    reconciliation_run_id varchar(128) not null,
    batch_id varchar(128) not null,
    entity_name varchar(128) not null,
    source_uri varchar(1024),
    expected_source_rows bigint,
    prepared_total_rows bigint,
    prepared_valid_rows bigint,
    dead_letter_rows bigint,
    replayed_rows bigint not null,
    expected_loaded_rows bigint,
    raw_loaded_rows bigint not null,
    source_to_prepared_delta bigint,
    prepared_to_loaded_delta bigint,
    status varchar(32) not null,
    failed_checks varchar(1024),
    created_at timestamp not null
);

create table if not exists audit.dead_letter_events (
    dead_letter_event_id varchar(256) not null,
    batch_id varchar(128) not null,
    load_run_id varchar(128) not null,
    entity_name varchar(128) not null,
    source_uri varchar(1024),
    dead_letter_uri varchar(1024),
    total_rows bigint not null,
    valid_rows bigint not null,
    failed_rows bigint not null,
    threshold_max_rows bigint not null,
    threshold_max_rate decimal(18, 8) not null,
    reason_summary varchar(65535),
    created_at timestamp not null
);

create table if not exists audit.dead_letter_replays (
    dead_letter_replay_id varchar(256) not null,
    batch_id varchar(128) not null,
    entity_name varchar(128) not null,
    dead_letter_uri varchar(1024) not null,
    target_table varchar(256) not null,
    replay_source_file varchar(512) not null,
    status varchar(32) not null,
    rows_replayed bigint,
    started_at timestamp not null,
    finished_at timestamp,
    error_message varchar(65535)
);
