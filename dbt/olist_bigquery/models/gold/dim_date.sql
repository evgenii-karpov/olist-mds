{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'date_key'],
        alias='dim_date__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'date_key'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

WITH date_spine AS
(
    SELECT DISTINCT DATE(order_purchase_timestamp) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted

    UNION DISTINCT

    SELECT DISTINCT DATE(order_approved_at) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted AND order_approved_at IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT DATE(order_delivered_carrier_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted AND order_delivered_carrier_date IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT DATE(order_delivered_customer_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted AND order_delivered_customer_date IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT DATE(order_estimated_delivery_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE NOT is_deleted AND order_estimated_delivery_date IS NOT NULL
)
SELECT
    {{ history_columns("'REPLACE_GRAIN'") }},
    CAST(FORMAT_DATE('%Y%m%d', date_day) AS INT64) AS date_key,
    date_day,
    EXTRACT(YEAR FROM date_day) AS year_number,
    EXTRACT(MONTH FROM date_day) AS month_number,
    EXTRACT(DAY FROM date_day) AS day_number,
    EXTRACT(QUARTER FROM date_day) AS quarter_number,
    EXTRACT(ISOWEEK FROM date_day) AS week_number,
    MOD(EXTRACT(DAYOFWEEK FROM date_day) + 6, 7) AS day_of_week_number,
    FORMAT_DATE('%Y-%m', date_day) AS year_month,
    RPAD(FORMAT_DATE('%B', date_day), 9, ' ') AS month_name,
    MOD(EXTRACT(DAYOFWEEK FROM date_day) + 6, 7) IN (0, 6) AS is_weekend
FROM date_spine
WHERE date_day IS NOT NULL
