{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['date_key'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

WITH date_spine AS
(
    SELECT DISTINCT toDate(order_purchase_timestamp) AS date_day
    FROM {{ ref('stg_orders_current') }}

    UNION DISTINCT

    SELECT DISTINCT toDate(order_approved_at) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE order_approved_at IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT toDate(order_delivered_carrier_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE order_delivered_carrier_date IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT toDate(order_delivered_customer_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
    WHERE order_delivered_customer_date IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT toDate(order_estimated_delivery_date) AS date_day
    FROM {{ ref('stg_orders_current') }}
)

SELECT
    {{ candidate_run_columns() }},
    toInt32(formatDateTime(assumeNotNull(date_day), '%Y%m%d')) AS date_key,
    assumeNotNull(date_day) AS date_day,
    toYear(assumeNotNull(date_day)) AS year_number,
    toMonth(assumeNotNull(date_day)) AS month_number,
    toDayOfMonth(assumeNotNull(date_day)) AS day_number,
    toQuarter(assumeNotNull(date_day)) AS quarter_number,
    toISOWeek(assumeNotNull(date_day)) AS week_number,
    modulo(toDayOfWeek(assumeNotNull(date_day)), 7) AS day_of_week_number,
    formatDateTime(assumeNotNull(date_day), '%Y-%m') AS year_month,
    rightPad(monthName(assumeNotNull(date_day)), 9, ' ') AS month_name,
    modulo(toDayOfWeek(assumeNotNull(date_day)), 7) IN (0, 6) AS is_weekend
FROM date_spine
WHERE date_day IS NOT NULL
