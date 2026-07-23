CREATE TABLE IF NOT EXISTS raw_data.customers
(
    customer_id Nullable(String),
    customer_unique_id Nullable(String),
    customer_zip_code_prefix Nullable(String),
    customer_city Nullable(String),
    customer_state Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(customer_id, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.geolocation
(
    geolocation_zip_code_prefix Nullable(String),
    geolocation_lat Nullable(Decimal(18, 14)),
    geolocation_lng Nullable(Decimal(18, 14)),
    geolocation_city Nullable(String),
    geolocation_state Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (
    ifNull(geolocation_zip_code_prefix, ''),
    ifNull(geolocation_lat, toDecimal64(0, 14)),
    ifNull(geolocation_lng, toDecimal64(0, 14)),
    _loaded_at
);

CREATE TABLE IF NOT EXISTS raw_data.order_items
(
    order_id Nullable(String),
    order_item_id Nullable(Int32),
    product_id Nullable(String),
    seller_id Nullable(String),
    shipping_limit_date Nullable(DateTime64(6, 'UTC')),
    price Nullable(Decimal(18, 2)),
    freight_value Nullable(Decimal(18, 2)),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(order_id, ''), ifNull(order_item_id, 0), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.order_payments
(
    order_id Nullable(String),
    payment_sequential Nullable(Int32),
    payment_type Nullable(String),
    payment_installments Nullable(Int32),
    payment_value Nullable(Decimal(18, 2)),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(order_id, ''), ifNull(payment_sequential, 0), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.order_reviews
(
    review_id Nullable(String),
    order_id Nullable(String),
    review_score Nullable(Int32),
    review_comment_title Nullable(String),
    review_comment_message Nullable(String),
    review_creation_date Nullable(DateTime64(6, 'UTC')),
    review_answer_timestamp Nullable(DateTime64(6, 'UTC')),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(review_id, ''), ifNull(order_id, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.orders
(
    order_id Nullable(String),
    customer_id Nullable(String),
    order_status Nullable(String),
    order_purchase_timestamp Nullable(DateTime64(6, 'UTC')),
    order_approved_at Nullable(DateTime64(6, 'UTC')),
    order_delivered_carrier_date Nullable(DateTime64(6, 'UTC')),
    order_delivered_customer_date Nullable(DateTime64(6, 'UTC')),
    order_estimated_delivery_date Nullable(DateTime64(6, 'UTC')),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(order_id, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.products
(
    product_id Nullable(String),
    product_category_name Nullable(String),
    product_name_lenght Nullable(Int32),
    product_description_lenght Nullable(Int32),
    product_photos_qty Nullable(Int32),
    product_weight_g Nullable(Int32),
    product_length_cm Nullable(Int32),
    product_height_cm Nullable(Int32),
    product_width_cm Nullable(Int32),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(product_id, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.sellers
(
    seller_id Nullable(String),
    seller_zip_code_prefix Nullable(String),
    seller_city Nullable(String),
    seller_state Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(seller_id, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.product_category_translation
(
    product_category_name Nullable(String),
    product_category_name_english Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (ifNull(product_category_name, ''), _loaded_at);

CREATE TABLE IF NOT EXISTS raw_data.customer_profile_changes
(
    customer_unique_id Nullable(String),
    effective_at Nullable(DateTime64(6, 'UTC')),
    customer_zip_code_prefix Nullable(String),
    customer_city Nullable(String),
    customer_state Nullable(String),
    change_reason Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (
    ifNull(customer_unique_id, ''),
    ifNull(effective_at, toDateTime64(0, 6, 'UTC')),
    _loaded_at
);

CREATE TABLE IF NOT EXISTS raw_data.product_attribute_changes
(
    product_id Nullable(String),
    effective_at Nullable(DateTime64(6, 'UTC')),
    product_category_name Nullable(String),
    product_weight_g Nullable(Int32),
    product_length_cm Nullable(Int32),
    product_height_cm Nullable(Int32),
    product_width_cm Nullable(Int32),
    change_reason Nullable(String),
    _batch_id String,
    _loaded_at DateTime64(6, 'UTC'),
    _source_file String,
    _source_system LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (
    ifNull(product_id, ''),
    ifNull(effective_at, toDateTime64(0, 6, 'UTC')),
    _loaded_at
);
