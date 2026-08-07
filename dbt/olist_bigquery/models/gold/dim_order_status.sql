{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'order_status'],
        alias='dim_order_status__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'order_status'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

SELECT
    {{ history_columns("'REPLACE_GRAIN'") }},
    LOWER(TO_HEX(MD5(order_status))) AS order_status_key,
    order_status,
    CAST(order_status = 'delivered' AS BOOL) AS is_successful_status,
    CAST(order_status IN ('canceled', 'unavailable') AS BOOL) AS is_failed_status
FROM
(
    SELECT DISTINCT order_status
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted AND order_status IS NOT NULL
)
