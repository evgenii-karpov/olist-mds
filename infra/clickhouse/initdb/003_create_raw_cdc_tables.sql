CREATE TABLE IF NOT EXISTS raw_cdc.customers
(
    customer_id String,
    customer_unique_id String,
    customer_zip_code_prefix String,
    customer_city String,
    customer_state String,
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.orders
(
    order_id String,
    customer_id String,
    order_status LowCardinality(String),
    order_purchase_timestamp DateTime64(6, 'UTC'),
    order_approved_at Nullable(DateTime64(6, 'UTC')),
    order_delivered_carrier_date Nullable(DateTime64(6, 'UTC')),
    order_delivered_customer_date Nullable(DateTime64(6, 'UTC')),
    order_estimated_delivery_date DateTime64(6, 'UTC'),
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.order_items
(
    order_id String,
    order_item_id Int32,
    product_id String,
    seller_id String,
    shipping_limit_date DateTime64(6, 'UTC'),
    price Decimal(18, 2),
    freight_value Decimal(18, 2),
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.order_payments
(
    order_id String,
    payment_sequential Int32,
    payment_type LowCardinality(String),
    payment_installments Int32,
    payment_value Decimal(18, 2),
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.order_reviews
(
    review_id String,
    order_id String,
    review_score Int32,
    review_comment_title Nullable(String),
    review_comment_message Nullable(String),
    review_creation_date DateTime64(6, 'UTC'),
    review_answer_timestamp DateTime64(6, 'UTC'),
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.products
(
    product_id String,
    product_category_name Nullable(String),
    product_name_lenght Nullable(Int32),
    product_description_lenght Nullable(Int32),
    product_photos_qty Nullable(Int32),
    product_weight_g Nullable(Int32),
    product_length_cm Nullable(Int32),
    product_height_cm Nullable(Int32),
    product_width_cm Nullable(Int32),
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.sellers
(
    seller_id String,
    seller_zip_code_prefix String,
    seller_city String,
    seller_state String,
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;

CREATE TABLE IF NOT EXISTS raw_cdc.product_category_translation
(
    product_category_name String,
    product_category_name_english String,
    _event_id String,
    _op LowCardinality(String),
    _source_ts Nullable(DateTime64(6, 'UTC')),
    _source_lsn Int64,
    _tx_id Nullable(Int64),
    _tx_order Nullable(Int64),
    _topic String,
    _partition Int32,
    _offset Int64,
    _kafka_ts Nullable(DateTime64(6, 'UTC')),
    _key_schema_id Nullable(Int32),
    _schema_id Int32,
    _nifi_written_at DateTime64(6, 'UTC'),
    _warehouse_loaded_at DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),
    _source_object_uri String
)
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(coalesce(_source_ts, _kafka_ts, _nifi_written_at))
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000;
