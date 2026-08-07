{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'customer_key'],
        alias='dim_customer_scd2__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'customer_unique_id'],
        pre_hook="{{ delete_same_run_history(this) }}"
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
        is_snapshot,
        source_binlog_file_index,
        source_binlog_pos,
        source_row,
        transaction_total_order,
        transaction_data_collection_order,
        kafka_topic,
        kafka_partition,
        kafka_offset,
        is_deleted,
        IF(
            is_snapshot
                OR source_ts = MIN(source_ts) OVER (
                    PARTITION BY customer_unique_id
                ),
            TIMESTAMP('1900-01-01 00:00:00+00'),
            source_ts
        ) AS valid_from,
        LOWER(TO_HEX(MD5(CONCAT(
            COALESCE(row_hash, '<NULL>'), '|', CAST(is_deleted AS STRING)
        )))) AS dimension_row_hash
    FROM {{ ref('stg_customers_events') }}
    WHERE customer_unique_id IS NOT NULL
),
same_timestamp_ranked AS
(
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_unique_id, valid_from
            ORDER BY {{ event_order() }}
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
        LAG(dimension_row_hash) OVER (
            PARTITION BY customer_unique_id
            ORDER BY
                valid_from,
                is_snapshot,
                source_binlog_file_index,
                source_binlog_pos,
                source_row,
                transaction_total_order,
                transaction_data_collection_order,
                source_ts,
                kafka_partition,
                kafka_offset,
                event_id
        ) AS previous_dimension_row_hash
    FROM deduplicated_events
),
collapsed_events AS
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
            PARTITION BY customer_unique_id
            ORDER BY
                valid_from,
                is_snapshot,
                source_binlog_file_index,
                source_binlog_pos,
                source_row,
                transaction_total_order,
                transaction_data_collection_order,
                source_ts,
                kafka_partition,
                kafka_offset,
                event_id
        ) AS valid_to
    FROM collapsed_events
)
SELECT
    {{ history_columns(
        "CASE WHEN is_deleted THEN 'DELETE' "
        "WHEN valid_to IS NULL THEN 'INSERT' ELSE 'CLOSE' END"
    ) }},
    LOWER(TO_HEX(MD5(CONCAT(customer_unique_id, '|', event_id)))) AS customer_key,
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    valid_from,
    valid_to,
    valid_to IS NULL AS is_current,
    event_id AS opening_event_id,
    dimension_row_hash,
    source_ts AS opening_source_ts,
    kafka_topic AS opening_kafka_topic,
    kafka_partition AS opening_kafka_partition,
    kafka_offset AS opening_kafka_offset
FROM windowed_versions
