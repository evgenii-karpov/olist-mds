-- Stable native BigQuery bridge views over the Lakehouse runtime catalog.
--
-- The migration runner replaces {{ project_id }} and {{ catalog_id }} after
-- validating both identifiers. The P.C.N.T source relation is deliberately
-- kept read-only. WP5 must prove this syntax and the resulting type surface
-- in the target GCP project before this migration is applied there.

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.bronze_mysql_cdc_records`
OPTIONS (
  description = 'Read-only normalized bridge over Bronze MySQL CDC records'
)
AS
SELECT
  CAST(`event_id` AS STRING) AS event_id,
  CAST(`record_kind` AS STRING) AS record_kind,
  CAST(`topic` AS STRING) AS topic,
  CAST(`partition` AS INT64) AS `partition`,
  CAST(`offset` AS INT64) AS `offset`,
  CAST(`kafka_timestamp` AS TIMESTAMP) AS kafka_timestamp,
  CAST(`kafka_timestamp_type` AS INT64) AS kafka_timestamp_type,
  ARRAY(
    SELECT AS STRUCT
      CAST(header.`key` AS STRING) AS `key`,
      CAST(header.`value` AS BYTES) AS `value`
    FROM UNNEST(`headers`) AS header
  ) AS headers,
  CAST(`key_bytes` AS BYTES) AS key_bytes,
  CAST(`value_bytes` AS BYTES) AS value_bytes,
  CAST(`is_tombstone` AS BOOL) AS is_tombstone,
  CAST(`key_schema_id` AS INT64) AS key_schema_id,
  CAST(`value_schema_id` AS INT64) AS value_schema_id,
  CAST(`key_sha256` AS STRING) AS key_sha256,
  CAST(`value_sha256` AS STRING) AS value_sha256,
  CAST(`key_framing_valid` AS BOOL) AS key_framing_valid,
  CAST(`value_framing_valid` AS BOOL) AS value_framing_valid,
  CAST(`framing_error` AS STRING) AS framing_error,
  CAST(`ingest_batch_id` AS INT64) AS ingest_batch_id,
  CAST(`spark_query_id` AS STRING) AS spark_query_id,
  CAST(`ingested_at` AS TIMESTAMP) AS ingested_at
FROM `{{ project_id }}.{{ catalog_id }}.bronze.mysql_cdc_records`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_order_items_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver order-item changes'
)
AS
SELECT
  CAST(`event_id` AS STRING) AS event_id,
  CAST(`op` AS STRING) AS op,
  CAST(`is_snapshot` AS BOOL) AS is_snapshot,
  CAST(`is_deleted` AS BOOL) AS is_deleted,
  CAST(`apply_status` AS STRING) AS apply_status,
  CAST(`error_code` AS STRING) AS error_code,
  CAST(`error_message` AS STRING) AS error_message,
  CAST(`order_id` AS STRING) AS order_id,
  CAST(`order_item_id` AS INT64) AS order_item_id,
  CAST(`product_id` AS STRING) AS product_id,
  CAST(`seller_id` AS STRING) AS seller_id,
  CAST(`shipping_limit_date` AS TIMESTAMP) AS shipping_limit_date,
  CAST(`price` AS NUMERIC) AS price,
  CAST(`freight_value` AS NUMERIC) AS freight_value,
  CAST(`source_ts` AS TIMESTAMP) AS source_ts,
  CAST(`source_server_id` AS INT64) AS source_server_id,
  CAST(`source_gtid` AS STRING) AS source_gtid,
  CAST(`source_binlog_file` AS STRING) AS source_binlog_file,
  CAST(`source_binlog_file_index` AS INT64) AS source_binlog_file_index,
  CAST(`source_binlog_pos` AS INT64) AS source_binlog_pos,
  CAST(`source_row` AS INT64) AS source_row,
  CAST(`transaction_id` AS STRING) AS transaction_id,
  CAST(`transaction_total_order` AS INT64) AS transaction_total_order,
  CAST(`transaction_data_collection_order` AS INT64)
    AS transaction_data_collection_order,
  CAST(`kafka_topic` AS STRING) AS kafka_topic,
  CAST(`kafka_partition` AS INT64) AS kafka_partition,
  CAST(`kafka_offset` AS INT64) AS kafka_offset,
  CAST(`kafka_timestamp` AS TIMESTAMP) AS kafka_timestamp,
  CAST(`key_schema_id` AS INT64) AS key_schema_id,
  CAST(`value_schema_id` AS INT64) AS value_schema_id,
  CAST(`schema_fingerprint` AS STRING) AS schema_fingerprint,
  CAST(`contract_version` AS INT64) AS contract_version,
  CAST(`before_row_hash` AS STRING) AS before_row_hash,
  CAST(`after_row_hash` AS STRING) AS after_row_hash,
  CAST(`row_hash` AS STRING) AS row_hash,
  CAST(`bronze_ingested_at` AS TIMESTAMP) AS bronze_ingested_at,
  CAST(`normalized_at` AS TIMESTAMP) AS normalized_at
FROM `{{ project_id }}.{{ catalog_id }}.silver.order_items_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.reference_geolocation`
OPTIONS (
  description = 'Read-only normalized bridge over reference geolocation'
)
AS
SELECT
  CAST(`geolocation_id` AS INT64) AS geolocation_id,
  CAST(`geolocation_zip_code_prefix` AS STRING) AS geolocation_zip_code_prefix,
  CAST(`geolocation_lat` AS BIGNUMERIC) AS geolocation_lat,
  CAST(`geolocation_lng` AS BIGNUMERIC) AS geolocation_lng,
  CAST(`geolocation_city` AS STRING) AS geolocation_city,
  CAST(`geolocation_state` AS STRING) AS geolocation_state,
  CAST(`source_archive_sha256` AS STRING) AS source_archive_sha256,
  CAST(`source_row_number` AS INT64) AS source_row_number,
  CAST(`loaded_at` AS TIMESTAMP) AS loaded_at
FROM `{{ project_id }}.{{ catalog_id }}.reference.geolocation`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.audit_silver_progress`
OPTIONS (
  description = 'Read-only normalized bridge over Silver progress evidence'
)
AS
SELECT
  CAST(`query_name` AS STRING) AS query_name,
  CAST(`entity` AS STRING) AS entity,
  CAST(`contract_version` AS INT64) AS contract_version,
  CAST(`source_topic` AS STRING) AS source_topic,
  CAST(`kafka_partition` AS INT64) AS kafka_partition,
  CAST(`last_kafka_offset` AS INT64) AS last_kafka_offset,
  CAST(`last_event_id` AS STRING) AS last_event_id,
  CAST(`last_source_ts` AS TIMESTAMP) AS last_source_ts,
  CAST(`spark_query_id` AS STRING) AS spark_query_id,
  CAST(`spark_batch_id` AS INT64) AS spark_batch_id,
  CAST(`changes_snapshot_id` AS INT64) AS changes_snapshot_id,
  CAST(`current_snapshot_id` AS INT64) AS current_snapshot_id,
  CAST(`status` AS STRING) AS status,
  CAST(`error_class` AS STRING) AS error_class,
  CAST(`updated_at` AS TIMESTAMP) AS updated_at,
  CAST(`recorded_at` AS TIMESTAMP) AS recorded_at
FROM `{{ project_id }}.{{ catalog_id }}.audit.silver_progress`;
