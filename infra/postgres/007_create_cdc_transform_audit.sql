-- Durable Phase 5 transform boundary and publication approval state.

create schema if not exists realtime_staging;
create schema if not exists realtime_core;
create schema if not exists realtime_marts;
create schema if not exists analytics;

create table if not exists cdc_audit.cdc_transform_runs (
    transform_run_id varchar(256) primary key,
    dag_id varchar(256),
    orchestration_run_id varchar(256),
    status varchar(32) not null check (
        status in ('STARTED', 'SUCCEEDED', 'FAILED')
    ),
    files_selected bigint not null default 0,
    events_selected bigint not null default 0,
    dbt_completed_at timestamptz,
    started_at timestamptz not null default clock_timestamp(),
    finished_at timestamptz,
    failure_summary text
);

alter table cdc_audit.cdc_transform_runs
    add column if not exists dbt_completed_at timestamptz;

create table if not exists cdc_audit.cdc_transform_run_files (
    transform_run_id varchar(256) not null references
        cdc_audit.cdc_transform_runs(transform_run_id),
    manifest_uri varchar(2048) not null references
        cdc_audit.cdc_files(manifest_uri),
    selected_at timestamptz not null default clock_timestamp(),
    primary key (transform_run_id, manifest_uri)
);

create index if not exists cdc_transform_run_files_manifest_idx
    on cdc_audit.cdc_transform_run_files (manifest_uri);

create table if not exists cdc_audit.cdc_publication_state (
    publication_name varchar(256) primary key,
    target_path varchar(32) not null check (target_path in ('batch', 'realtime')),
    parity_status varchar(16) not null check (parity_status in ('PENDING', 'PASS', 'FAIL')),
    approved_by varchar(256),
    approved_at timestamptz,
    updated_at timestamptz not null default clock_timestamp()
);

insert into cdc_audit.cdc_publication_state (
    publication_name, target_path, parity_status
)
values ('olist_marts', 'batch', 'PENDING')
on conflict (publication_name) do nothing;
