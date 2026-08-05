CREATE TABLE IF NOT EXISTS serving_cdc.customers_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    customer_id String,
    customer_unique_id String,
    customer_zip_code_prefix String,
    customer_city String,
    customer_state FixedString(2),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, customer_id);

CREATE TABLE IF NOT EXISTS serving_cdc.orders_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    order_id String,
    customer_id String,
    order_status LowCardinality(String),
    order_purchase_timestamp DateTime64(6, 'UTC'),
    order_approved_at Nullable(DateTime64(6, 'UTC')),
    order_delivered_carrier_date Nullable(DateTime64(6, 'UTC')),
    order_delivered_customer_date Nullable(DateTime64(6, 'UTC')),
    order_estimated_delivery_date DateTime64(6, 'UTC'),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, order_id);

CREATE TABLE IF NOT EXISTS serving_cdc.order_items_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    order_id String,
    order_item_id Int32,
    product_id String,
    seller_id String,
    shipping_limit_date DateTime64(6, 'UTC'),
    price Decimal(18, 2),
    freight_value Decimal(18, 2),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, order_id, order_item_id);

CREATE TABLE IF NOT EXISTS serving_cdc.order_payments_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    order_id String,
    payment_sequential Int32,
    payment_type LowCardinality(String),
    payment_installments Int32,
    payment_value Decimal(18, 2),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, order_id, payment_sequential);

CREATE TABLE IF NOT EXISTS serving_cdc.order_reviews_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    review_id String,
    order_id String,
    review_score Int32,
    review_comment_title Nullable(String),
    review_comment_message Nullable(String),
    review_creation_date DateTime64(6, 'UTC'),
    review_answer_timestamp DateTime64(6, 'UTC'),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, review_id, order_id);

CREATE TABLE IF NOT EXISTS serving_cdc.products_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    product_id String,
    product_category_name Nullable(String),
    product_name_lenght Nullable(Int32),
    product_description_lenght Nullable(Int32),
    product_photos_qty Nullable(Int32),
    product_weight_g Nullable(Int32),
    product_length_cm Nullable(Int32),
    product_height_cm Nullable(Int32),
    product_width_cm Nullable(Int32),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, product_id);

CREATE TABLE IF NOT EXISTS serving_cdc.sellers_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    seller_id String,
    seller_zip_code_prefix String,
    seller_city String,
    seller_state FixedString(2),
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, seller_id);

CREATE TABLE IF NOT EXISTS serving_cdc.product_category_translation_current_versions
(
    sync_run_seq UInt64,
    sync_run_id String,
    product_category_name String,
    product_category_name_english String,
    is_deleted Bool,
    deleted_at Nullable(DateTime64(6, 'UTC')),
    last_event_id String,
    last_source_ts DateTime64(6, 'UTC'),
    last_transaction_id Nullable(String),
    kafka_partition Int32,
    kafka_offset Int64,
    last_row_hash String,
    contract_version UInt32,
    updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, product_category_name);
