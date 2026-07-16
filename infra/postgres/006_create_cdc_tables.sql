-- Append-only CDC event storage and durable ingest control state.

create schema if not exists raw_cdc;
create schema if not exists cdc_audit;

create table if not exists raw_cdc.customers (
    customer_id varchar(256) not null,
    customer_unique_id varchar(256) not null,
    customer_zip_code_prefix varchar(16) not null,
    customer_city varchar(256) not null,
    customer_state varchar(8) not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.orders (
    order_id varchar(256) not null,
    customer_id varchar(256) not null,
    order_status varchar(64) not null,
    order_purchase_timestamp timestamptz not null,
    order_approved_at timestamptz,
    order_delivered_carrier_date timestamptz,
    order_delivered_customer_date timestamptz,
    order_estimated_delivery_date timestamptz not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.order_items (
    order_id varchar(256) not null,
    order_item_id integer not null,
    product_id varchar(256) not null,
    seller_id varchar(256) not null,
    shipping_limit_date timestamptz not null,
    price decimal(18, 2) not null,
    freight_value decimal(18, 2) not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.order_payments (
    order_id varchar(256) not null,
    payment_sequential integer not null,
    payment_type varchar(64) not null,
    payment_installments integer not null,
    payment_value decimal(18, 2) not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.order_reviews (
    review_id varchar(256) not null,
    order_id varchar(256) not null,
    review_score integer not null,
    review_comment_title varchar(1024),
    review_comment_message text,
    review_creation_date timestamptz not null,
    review_answer_timestamp timestamptz not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.products (
    product_id varchar(256) not null,
    product_category_name varchar(256),
    product_name_lenght integer,
    product_description_lenght integer,
    product_photos_qty integer,
    product_weight_g integer,
    product_length_cm integer,
    product_height_cm integer,
    product_width_cm integer,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.sellers (
    seller_id varchar(256) not null,
    seller_zip_code_prefix varchar(16) not null,
    seller_city varchar(256) not null,
    seller_state varchar(8) not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists raw_cdc.product_category_translation (
    product_category_name varchar(256) not null,
    product_category_name_english varchar(256) not null,
    _event_id varchar(512) primary key,
    _op char(1) not null check (_op in ('r', 'c', 'u', 'd')),
    _source_ts timestamptz,
    _source_lsn bigint not null,
    _tx_id bigint,
    _tx_order bigint,
    _topic varchar(512) not null,
    _partition integer not null,
    _offset bigint not null,
    _kafka_ts timestamptz,
    _key_schema_id integer,
    _schema_id integer not null,
    _nifi_written_at timestamptz not null,
    _warehouse_loaded_at timestamptz not null default clock_timestamp(),
    _source_object_uri varchar(2048) not null,
    unique (_topic, _partition, _offset)
);

create table if not exists cdc_audit.cdc_ingest_runs (
    ingest_run_id varchar(256) primary key,
    dag_id varchar(256),
    orchestration_run_id varchar(256),
    run_kind varchar(32) not null check (run_kind in ('SCHEDULED', 'MANUAL', 'REPLAY')),
    status varchar(32) not null check (status in ('STARTED', 'SUCCEEDED', 'FAILED')),
    files_discovered bigint not null default 0,
    coverage_manifests_discovered bigint not null default 0,
    files_claimed bigint not null default 0,
    files_loaded bigint not null default 0,
    object_rows bigint not null default 0,
    inserted_rows bigint not null default 0,
    duplicate_rows bigint not null default 0,
    rejected_rows bigint not null default 0,
    gap_count bigint not null default 0,
    started_at timestamptz not null default clock_timestamp(),
    finished_at timestamptz,
    failure_summary text
);

create table if not exists cdc_audit.cdc_files (
    manifest_uri varchar(2048) primary key,
    manifest_etag varchar(256) not null,
    object_uri varchar(2048) not null,
    object_etag varchar(256) not null,
    object_sha256 char(64) not null,
    object_size_bytes bigint not null,
    source_table varchar(128) not null,
    topic varchar(512) not null,
    partition_id integer not null,
    offset_ranges jsonb not null,
    min_offset bigint not null,
    max_offset bigint not null,
    schema_id varchar(128) not null,
    manifest_row_count bigint not null,
    operation_counts jsonb not null,
    ingest_date date not null,
    source_ts_min timestamptz,
    source_ts_max timestamptz,
    closed_at timestamptz not null,
    status varchar(32) not null check (status in ('DISCOVERED', 'REPLAY_REQUESTED', 'CLAIMED', 'LOADED', 'FAILED')),
    first_seen_at timestamptz not null default clock_timestamp(),
    first_attempt_at timestamptz,
    last_attempt_at timestamptz,
    attempt_count integer not null default 0,
    claimed_by_run_id varchar(256),
    claim_expires_at timestamptz,
    loaded_by_run_id varchar(256),
    replay_request_id varchar(256),
    loaded_at timestamptz,
    last_error text,
    unique (object_uri, object_etag)
);

alter table cdc_audit.cdc_files
    add column if not exists ingest_date date;
update cdc_audit.cdc_files
set ingest_date = substring(
    manifest_uri from 'ingest_date=([0-9]{4}-[0-9]{2}-[0-9]{2})'
)::date
where ingest_date is null;
alter table cdc_audit.cdc_files
    alter column ingest_date set not null;

create table if not exists cdc_audit.cdc_file_attempts (
    file_attempt_id bigserial primary key,
    manifest_uri varchar(2048) not null references cdc_audit.cdc_files(manifest_uri),
    ingest_run_id varchar(256) not null references cdc_audit.cdc_ingest_runs(ingest_run_id),
    attempt_number integer not null,
    status varchar(32) not null check (status in ('CLAIMED', 'SUCCEEDED', 'FAILED')),
    object_rows bigint,
    inserted_rows bigint,
    duplicate_rows bigint,
    rejected_rows bigint,
    started_at timestamptz not null default clock_timestamp(),
    finished_at timestamptz,
    error_message text,
    unique (manifest_uri, attempt_number)
);

create table if not exists cdc_audit.cdc_coverage_files (
    coverage_uri varchar(2048) primary key,
    coverage_etag varchar(256) not null,
    source_table varchar(128) not null,
    topic varchar(512) not null,
    partition_id integer not null,
    consumed_offset_ranges jsonb not null,
    business_event_offset_ranges jsonb not null,
    tombstone_offset_ranges jsonb not null,
    consumed_row_count bigint not null,
    business_event_count bigint not null,
    tombstone_count bigint not null,
    ingest_date date not null,
    closed_at timestamptz not null,
    landing_manifest_uri varchar(2048) not null,
    landing_manifest_etag varchar(256) not null,
    landing_object_uri varchar(2048) not null,
    landing_object_etag varchar(256) not null,
    landing_object_sha256 char(64) not null,
    landing_object_size_bytes bigint not null,
    status varchar(32) not null check (status in ('VERIFIED')),
    verified_by_run_id varchar(256) not null,
    verified_at timestamptz not null default clock_timestamp()
);

create table if not exists cdc_audit.cdc_offset_coverage (
    coverage_kind varchar(32) not null check (
        coverage_kind in ('SOURCE_CONSUMED', 'NORMALIZED_LOADED', 'TOMBSTONE_AUDITED')
    ),
    source_uri varchar(2048) not null,
    source_etag varchar(256) not null,
    topic varchar(512) not null,
    partition_id integer not null,
    range_start bigint not null,
    range_end bigint not null,
    recorded_by_run_id varchar(256) not null,
    recorded_at timestamptz not null default clock_timestamp(),
    primary key (coverage_kind, source_uri, range_start, range_end),
    check (range_start >= 0 and range_end >= range_start)
);

create table if not exists cdc_audit.cdc_partition_watermarks (
    topic varchar(512) not null,
    partition_id integer not null,
    first_seen_offset bigint not null,
    last_contiguous_offset bigint not null,
    last_seen_offset bigint not null,
    last_loaded_event_offset bigint,
    gap_count bigint not null,
    gap_ranges jsonb not null,
    source_lsn bigint,
    source_ts timestamptz,
    updated_at timestamptz not null default clock_timestamp(),
    primary key (topic, partition_id)
);

create table if not exists cdc_audit.cdc_reconciliation (
    reconciliation_id bigserial primary key,
    ingest_run_id varchar(256) not null references cdc_audit.cdc_ingest_runs(ingest_run_id),
    manifest_uri varchar(2048) not null references cdc_audit.cdc_files(manifest_uri),
    source_table varchar(128) not null,
    object_rows bigint not null,
    warehouse_inserted_rows bigint not null,
    duplicate_rows bigint not null,
    rejected_rows bigint not null,
    gap_count bigint not null,
    status varchar(16) not null check (status in ('PASS', 'FAIL')),
    failure_reason text,
    created_at timestamptz not null default clock_timestamp(),
    unique (ingest_run_id, manifest_uri)
);

create table if not exists cdc_audit.cdc_replay_requests (
    replay_request_id varchar(256) primary key,
    requested_by varchar(256) not null,
    source_table varchar(128),
    ingest_date_from date,
    ingest_date_to date,
    object_uri_pattern varchar(2048),
    status varchar(32) not null check (status in ('STARTED', 'READY', 'FAILED')),
    selected_file_count bigint not null default 0,
    requested_at timestamptz not null default clock_timestamp(),
    completed_at timestamptz,
    error_message text
);

create table if not exists cdc_audit.cdc_dead_letters (
    dead_letter_id bigserial primary key,
    topic varchar(512),
    partition_id integer,
    offset_value bigint,
    stage varchar(128) not null,
    reason text not null,
    schema_id varchar(128),
    object_uri varchar(2048),
    resolution_status varchar(32) not null default 'OPEN',
    created_at timestamptz not null default clock_timestamp(),
    resolved_at timestamptz
);

create table if not exists cdc_audit.cdc_mart_freshness (
    model_name varchar(256) primary key,
    max_source_ts timestamptz,
    build_time timestamptz not null,
    latency_seconds decimal(18, 3),
    build_run_id varchar(256) not null
);

create index if not exists cdc_files_claimable_idx
    on cdc_audit.cdc_files (status, claim_expires_at, closed_at);
create index if not exists cdc_files_partition_offsets_idx
    on cdc_audit.cdc_files (topic, partition_id, min_offset, max_offset)
    where status = 'LOADED';
create index if not exists cdc_reconciliation_run_idx
    on cdc_audit.cdc_reconciliation (ingest_run_id);
create index if not exists cdc_offset_coverage_partition_idx
    on cdc_audit.cdc_offset_coverage (
        topic, partition_id, range_start, range_end
    );

alter table cdc_audit.cdc_ingest_runs
    add column if not exists coverage_manifests_discovered bigint not null default 0;
alter table cdc_audit.cdc_partition_watermarks
    add column if not exists last_loaded_event_offset bigint;
alter table cdc_audit.cdc_files
    add column if not exists replay_request_id varchar(256);
alter table cdc_audit.cdc_files
    drop constraint if exists cdc_files_status_check;
alter table cdc_audit.cdc_files
    add constraint cdc_files_status_check check (
        status in ('DISCOVERED', 'REPLAY_REQUESTED', 'CLAIMED', 'LOADED', 'FAILED')
    );
alter table cdc_audit.cdc_offset_coverage
    drop constraint if exists cdc_offset_coverage_coverage_kind_check;
alter table cdc_audit.cdc_offset_coverage
    add constraint cdc_offset_coverage_coverage_kind_check check (
        coverage_kind in ('SOURCE_CONSUMED', 'NORMALIZED_LOADED', 'TOMBSTONE_AUDITED')
    );

insert into cdc_audit.cdc_offset_coverage (
    coverage_kind, source_uri, source_etag, topic, partition_id,
    range_start, range_end, recorded_by_run_id
)
select
    'NORMALIZED_LOADED', f.manifest_uri, f.manifest_etag, f.topic,
    f.partition_id, (value->>0)::bigint, (value->>1)::bigint,
    coalesce(f.loaded_by_run_id, 'bootstrap-backfill')
from cdc_audit.cdc_files f
cross join lateral jsonb_array_elements(f.offset_ranges) as ranges(value)
where f.status = 'LOADED'
on conflict do nothing;
