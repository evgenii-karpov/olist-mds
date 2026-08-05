{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['customer_unique_id', 'valid_from'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

WITH prepared_events AS
(
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        event_id,
        source_ts,
        kafka_topic,
        kafka_partition,
        kafka_offset,
        is_deleted,
        {{ scd_valid_from('events') }} AS valid_from,
        lower(hex(MD5(concat(row_hash, '|', toString(is_deleted)))))
            AS dimension_row_hash
    FROM {{ ref('stg_customers_events') }} AS events
),

same_timestamp_ranked AS
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY customer_unique_id, valid_from
            ORDER BY
                source_ts DESC,
                kafka_topic DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                customer_id DESC
        ) AS timestamp_rank
    FROM prepared_events
),

deduplicated_events AS
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
            PARTITION BY customer_unique_id
            ORDER BY
                valid_from,
                source_ts,
                kafka_topic,
                kafka_partition,
                kafka_offset,
                customer_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_dimension_row_hash
    FROM deduplicated_events
),

collapsed_events AS
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
            PARTITION BY customer_unique_id
            ORDER BY
                valid_from,
                source_ts,
                kafka_topic,
                kafka_partition,
                kafka_offset,
                customer_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS valid_to
    FROM collapsed_events
)

SELECT
    {{ candidate_run_columns() }},
    lower(hex(MD5(concat(customer_unique_id, '|', event_id)))) AS customer_key,
    customer_id,
    assumeNotNull(customer_unique_id) AS customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    assumeNotNull(valid_from) AS valid_from,
    valid_to,
    valid_to IS NULL AS is_current,
    event_id AS opening_event_id,
    dimension_row_hash,
    source_ts AS opening_source_ts,
    kafka_topic AS opening_kafka_topic,
    kafka_partition AS opening_kafka_partition,
    kafka_offset AS opening_kafka_offset
FROM windowed_versions
WHERE NOT is_deleted AND customer_unique_id IS NOT NULL
