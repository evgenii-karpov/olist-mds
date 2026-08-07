-- Additional read-only bridge views required by the independent BigQuery Gold
-- project. V002 owns the order_items slice; this migration adds the remaining
-- Silver change streams without exposing Iceberg metadata tables.

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_customers_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver customer changes'
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
  CAST(`customer_id` AS STRING) AS customer_id,
  CAST(`customer_unique_id` AS STRING) AS customer_unique_id,
  CAST(`customer_zip_code_prefix` AS STRING) AS customer_zip_code_prefix,
  CAST(`customer_city` AS STRING) AS customer_city,
  CAST(`customer_state` AS STRING) AS customer_state,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.customers_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_orders_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver order changes'
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
  CAST(`customer_id` AS STRING) AS customer_id,
  CAST(`order_status` AS STRING) AS order_status,
  CAST(`order_purchase_timestamp` AS TIMESTAMP) AS order_purchase_timestamp,
  CAST(`order_approved_at` AS TIMESTAMP) AS order_approved_at,
  CAST(`order_delivered_carrier_date` AS TIMESTAMP)
    AS order_delivered_carrier_date,
  CAST(`order_delivered_customer_date` AS TIMESTAMP)
    AS order_delivered_customer_date,
  CAST(`order_estimated_delivery_date` AS TIMESTAMP)
    AS order_estimated_delivery_date,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.orders_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_order_payments_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver payment changes'
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
  CAST(`payment_sequential` AS INT64) AS payment_sequential,
  CAST(`payment_type` AS STRING) AS payment_type,
  CAST(`payment_installments` AS INT64) AS payment_installments,
  CAST(`payment_value` AS NUMERIC) AS payment_value,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.order_payments_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_order_reviews_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver review changes'
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
  CAST(`review_id` AS STRING) AS review_id,
  CAST(`order_id` AS STRING) AS order_id,
  CAST(`review_score` AS INT64) AS review_score,
  CAST(`review_comment_title` AS STRING) AS review_comment_title,
  CAST(`review_comment_message` AS STRING) AS review_comment_message,
  CAST(`review_creation_date` AS TIMESTAMP) AS review_creation_date,
  CAST(`review_answer_timestamp` AS TIMESTAMP) AS review_answer_timestamp,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.order_reviews_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_products_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver product changes'
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
  CAST(`product_id` AS STRING) AS product_id,
  CAST(`product_category_name` AS STRING) AS product_category_name,
  CAST(`product_name_lenght` AS INT64) AS product_name_lenght,
  CAST(`product_description_lenght` AS INT64) AS product_description_lenght,
  CAST(`product_photos_qty` AS INT64) AS product_photos_qty,
  CAST(`product_weight_g` AS INT64) AS product_weight_g,
  CAST(`product_length_cm` AS INT64) AS product_length_cm,
  CAST(`product_height_cm` AS INT64) AS product_height_cm,
  CAST(`product_width_cm` AS INT64) AS product_width_cm,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.products_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_sellers_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver seller changes'
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
  CAST(`seller_id` AS STRING) AS seller_id,
  CAST(`seller_zip_code_prefix` AS STRING) AS seller_zip_code_prefix,
  CAST(`seller_city` AS STRING) AS seller_city,
  CAST(`seller_state` AS STRING) AS seller_state,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.sellers_changes`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.silver_product_category_translation_changes`
OPTIONS (
  description = 'Read-only normalized bridge over Silver category translation changes'
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
  CAST(`product_category_name` AS STRING) AS product_category_name,
  CAST(`product_category_name_english` AS STRING)
    AS product_category_name_english,
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
FROM `{{ project_id }}.{{ catalog_id }}.silver.product_category_translation_changes`;
