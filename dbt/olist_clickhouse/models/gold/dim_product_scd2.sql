{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['product_id', 'valid_from'],
        post_hook="{{ create_or_replace_gold_view() }}"
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

product_driven_ranked AS
(
    SELECT
        products.product_id,
        products.product_category_name AS product_category_name,
        products.product_name_lenght,
        products.product_description_lenght,
        products.product_photos_qty,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        if(
            ifNull(translations.is_deleted, false),
            CAST(NULL, 'Nullable(String)'),
            toNullable(translations.product_category_name_english)
        ) AS product_category_name_english,
        products.event_id AS version_event_id,
        products.source_ts,
        products.kafka_topic,
        products.kafka_partition,
        products.kafka_offset,
        products.is_snapshot,
        products.is_deleted,
        row_number() OVER (
            PARTITION BY products.event_id
            ORDER BY
                translations.source_ts DESC,
                translations.kafka_topic DESC,
                translations.kafka_partition DESC,
                translations.kafka_offset DESC
        ) AS translation_rank
    FROM product_events AS products
    LEFT JOIN translation_events AS translations
        ON
            products.product_category_name
                = translations.product_category_name
            AND {{ event_order_tuple('translations') }}
                <= {{ event_order_tuple('products') }}
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
        products.product_category_name AS product_category_name,
        translations.product_category_name AS translation_category_name,
        products.product_name_lenght,
        products.product_description_lenght,
        products.product_photos_qty,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        if(
            translations.is_deleted,
            CAST(NULL, 'Nullable(String)'),
            toNullable(translations.product_category_name_english)
        ) AS product_category_name_english,
        translations.event_id AS version_event_id,
        translations.source_ts,
        translations.kafka_topic,
        translations.kafka_partition,
        translations.kafka_offset,
        translations.is_snapshot,
        false AS is_deleted,
        products.is_deleted AS product_is_deleted,
        row_number() OVER (
            PARTITION BY translations.event_id, products.product_id
            ORDER BY
                products.source_ts DESC,
                products.kafka_topic DESC,
                products.kafka_partition DESC,
                products.kafka_offset DESC
        ) AS product_rank
    FROM translation_events AS translations
    INNER JOIN product_events AS products
        ON
            {{ event_order_tuple('products') }}
                <= {{ event_order_tuple('translations') }}
),

translation_driven_filtered AS
(
    SELECT *
    FROM translation_driven_ranked
    WHERE
        product_rank = 1
        AND NOT product_is_deleted
        AND product_category_name = translation_category_name
),

translation_driven AS
(
    SELECT * EXCEPT (
        translation_category_name,
        product_rank,
        product_is_deleted
    )
    FROM translation_driven_filtered
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
        if(
            is_snapshot,
            toDateTime64('1900-01-01 00:00:00', 6, 'UTC'),
            source_ts
        ) AS valid_from,
        lower(hex(MD5(concat(
            ifNull(product_category_name, '<NULL>'), '|',
            ifNull(product_category_name_english, '<NULL>'), '|',
            ifNull(toString(product_name_lenght), '<NULL>'), '|',
            ifNull(toString(product_description_lenght), '<NULL>'), '|',
            ifNull(toString(product_photos_qty), '<NULL>'), '|',
            ifNull(toString(product_weight_g), '<NULL>'), '|',
            ifNull(toString(product_length_cm), '<NULL>'), '|',
            ifNull(toString(product_height_cm), '<NULL>'), '|',
            ifNull(toString(product_width_cm), '<NULL>'), '|',
            toString(is_deleted)
        )))) AS dimension_row_hash
    FROM all_versions
),

same_timestamp_ranked AS
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY product_id, valid_from
            ORDER BY
                source_ts DESC,
                kafka_topic DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                version_event_id DESC
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
        lagInFrame(toNullable(dimension_row_hash)) OVER (
            PARTITION BY product_id
            ORDER BY
                valid_from,
                source_ts,
                kafka_topic,
                kafka_partition,
                kafka_offset,
                version_event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_dimension_row_hash
    FROM deduplicated_versions
),

collapsed_versions AS
(
    SELECT * EXCEPT (previous_dimension_row_hash)
    FROM with_previous_hash
    WHERE
        previous_dimension_row_hash IS NULL
        OR previous_dimension_row_hash != dimension_row_hash
),

windowed_versions AS
(
    SELECT
        *,
        leadInFrame(toNullable(valid_from)) OVER (
            PARTITION BY product_id
            ORDER BY
                valid_from,
                source_ts,
                kafka_topic,
                kafka_partition,
                kafka_offset,
                version_event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS valid_to
    FROM collapsed_versions
)

SELECT
    {{ candidate_run_columns() }},
    lower(hex(MD5(concat(product_id, '|', version_event_id)))) AS product_key,
    assumeNotNull(product_id) AS product_id,
    product_category_name,
    product_category_name_english,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    assumeNotNull(valid_from) AS valid_from,
    valid_to,
    valid_to IS NULL AS is_current,
    version_event_id AS opening_event_id,
    dimension_row_hash,
    source_ts AS opening_source_ts,
    kafka_topic AS opening_kafka_topic,
    kafka_partition AS opening_kafka_partition,
    kafka_offset AS opening_kafka_offset
FROM windowed_versions
WHERE NOT is_deleted AND product_id IS NOT NULL
