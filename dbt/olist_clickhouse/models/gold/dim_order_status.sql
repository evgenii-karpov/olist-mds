{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['order_status'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

SELECT
    {{ candidate_run_columns() }},
    lower(hex(MD5(order_status))) AS order_status_key,
    order_status,
    CAST(order_status = 'delivered' AS UInt8) AS is_successful_status,
    CAST(order_status IN ('canceled', 'unavailable') AS UInt8) AS is_failed_status
FROM
(
    SELECT DISTINCT order_status
    FROM {{ ref('stg_orders_current') }}
)
