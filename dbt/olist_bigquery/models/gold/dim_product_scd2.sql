{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'product_key'],
        alias='dim_product_scd2__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'product_id'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

WITH product_events AS
(
    SELECT *
    FROM {{ ref('stg_products_events') }}
),
translation_events AS
(
    SELECT *
    FROM {{ ref('stg_product_category_translation_events') }}
),
translations_current AS
(
    SELECT *
    FROM {{ ref('stg_product_category_translation_current') }}
    WHERE NOT is_deleted
),
products_current AS
(
    SELECT *
    FROM {{ ref('stg_products_current') }}
    WHERE NOT is_deleted
),
product_driven_ranked AS
(
    SELECT
        products.product_id,
        products.product_category_name,
        products.product_name_lenght,
        products.product_description_lenght,
        products.product_photos_qty,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        translations.product_category_name_english,
        products.event_id,
        products.event_id AS version_event_id,
        products.source_ts,
        products.source_binlog_file_index,
        products.source_binlog_pos,
        products.source_row,
        products.transaction_total_order,
        products.transaction_data_collection_order,
        products.kafka_topic,
        products.kafka_partition,
        products.kafka_offset,
        products.is_snapshot,
        products.is_deleted,
        ROW_NUMBER() OVER (
            PARTITION BY products.event_id
            ORDER BY {{ event_order('translations') }}
        ) AS translation_rank
    FROM product_events AS products
    LEFT JOIN translations_current AS translations
        ON products.product_category_name = translations.product_category_name
),
product_driven AS
(
    SELECT * EXCEPT (translation_rank)
    FROM product_driven_ranked
    WHERE translation_rank = 1
),
translation_driven_ranked AS
(
    SELECT
        products.product_id,
        products.product_category_name,
        products.product_name_lenght,
        products.product_description_lenght,
        products.product_photos_qty,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        IF(
            translations.is_deleted,
            CAST(NULL AS STRING),
            translations.product_category_name_english
        ) AS product_category_name_english,
        translations.event_id,
        translations.event_id AS version_event_id,
        translations.source_ts,
        translations.source_binlog_file_index,
        translations.source_binlog_pos,
        translations.source_row,
        translations.transaction_total_order,
        translations.transaction_data_collection_order,
        translations.kafka_topic,
        translations.kafka_partition,
        translations.kafka_offset,
        translations.is_snapshot,
        translations.is_deleted,
        ROW_NUMBER() OVER (
            PARTITION BY translations.event_id, products.product_id
            ORDER BY {{ event_order('products') }}
        ) AS product_rank
    FROM translation_events AS translations
    INNER JOIN products_current AS products
        ON products.product_category_name = translations.product_category_name
),
translation_driven AS
(
    SELECT * EXCEPT (product_rank)
    FROM translation_driven_ranked
    WHERE product_rank = 1
),
all_versions AS
(
    SELECT * FROM product_driven
    UNION ALL
    SELECT * FROM translation_driven
),
prepared_versions AS
(
    SELECT
        *,
        IF(
            is_snapshot
                OR source_ts = MIN(source_ts) OVER (PARTITION BY product_id),
            TIMESTAMP('1900-01-01 00:00:00+00'),
            source_ts
        ) AS valid_from,
        LOWER(TO_HEX(MD5(TO_JSON_STRING(STRUCT(
            product_category_name,
            product_category_name_english,
            product_name_lenght,
            product_description_lenght,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm,
            is_deleted
        ))))) AS dimension_row_hash
    FROM all_versions
),
same_timestamp_ranked AS
(
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY product_id, valid_from
            ORDER BY {{ event_order() }}, version_event_id DESC
        ) AS timestamp_rank
    FROM prepared_versions
),
deduplicated_versions AS
(
    SELECT * EXCEPT (timestamp_rank)
    FROM same_timestamp_ranked
    WHERE timestamp_rank = 1
),
with_previous_hash AS
(
    SELECT
        *,
        LAG(dimension_row_hash) OVER (
            PARTITION BY product_id
            ORDER BY valid_from, source_ts, kafka_partition, kafka_offset, version_event_id
        ) AS previous_dimension_row_hash
    FROM deduplicated_versions
),
collapsed_versions AS
(
    SELECT * EXCEPT (previous_dimension_row_hash)
    FROM with_previous_hash
    WHERE previous_dimension_row_hash IS NULL
        OR previous_dimension_row_hash != dimension_row_hash
),
windowed_versions AS
(
    SELECT
        *,
        LEAD(valid_from) OVER (
            PARTITION BY product_id
            ORDER BY valid_from, source_ts, kafka_partition, kafka_offset, version_event_id
        ) AS valid_to
    FROM collapsed_versions
)
SELECT
    {{ history_columns(
        "CASE WHEN is_deleted THEN 'DELETE' "
        "WHEN valid_to IS NULL THEN 'INSERT' ELSE 'CLOSE' END"
    ) }},
    LOWER(TO_HEX(MD5(CONCAT(product_id, '|', version_event_id)))) AS product_key,
    product_id,
    product_category_name,
    product_category_name_english,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    valid_from,
    valid_to,
    valid_to IS NULL AS is_current,
    version_event_id AS opening_event_id,
    dimension_row_hash,
    source_ts AS opening_source_ts,
    kafka_topic AS opening_kafka_topic,
    kafka_partition AS opening_kafka_partition,
    kafka_offset AS opening_kafka_offset
FROM windowed_versions
WHERE product_id IS NOT NULL
