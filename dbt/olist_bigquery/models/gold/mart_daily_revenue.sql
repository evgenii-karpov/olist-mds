{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'order_purchase_date'],
        alias='mart_daily_revenue__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'order_purchase_date'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

WITH item_facts AS
(
    SELECT
        DATE(order_purchase_timestamp) AS order_purchase_date,
        order_id,
        order_item_key,
        customer_unique_id,
        price,
        freight_value,
        gross_item_amount,
        allocated_payment_value,
        delivery_days,
        is_delivered_late
    FROM {{ ref('fact_order_items') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
        AND order_purchase_timestamp IS NOT NULL
),
order_level AS
(
    SELECT
        order_purchase_date,
        order_id,
        customer_unique_id,
        SUM(gross_item_amount) AS order_gross_revenue,
        SUM(COALESCE(allocated_payment_value, gross_item_amount))
            AS order_payment_revenue
    FROM item_facts
    GROUP BY order_purchase_date, order_id, customer_unique_id
),
item_daily AS
(
    SELECT
        order_purchase_date,
        SUM(gross_item_amount) AS gross_revenue,
        SUM(COALESCE(allocated_payment_value, gross_item_amount))
            AS allocated_payment_revenue,
        SUM(price) AS product_revenue,
        SUM(freight_value) AS freight_revenue,
        COUNT(DISTINCT order_item_key) AS items_count,
        AVG(delivery_days) AS average_delivery_days,
        COUNTIF(is_delivered_late) AS late_deliveries_count
    FROM item_facts
    GROUP BY order_purchase_date
),
order_daily AS
(
    SELECT
        order_purchase_date,
        COUNT(DISTINCT order_id) AS orders_count,
        COUNT(DISTINCT customer_unique_id) AS customers_count,
        AVG(order_gross_revenue) AS average_order_value,
        AVG(order_payment_revenue) AS average_paid_order_value
    FROM order_level
    GROUP BY order_purchase_date
)
SELECT
    {{ history_columns("'REPLACE_GRAIN'") }},
    item_daily.order_purchase_date,
    CAST(ROUND(item_daily.gross_revenue, 2) AS NUMERIC) AS gross_revenue,
    CAST(ROUND(item_daily.allocated_payment_revenue, 2) AS NUMERIC)
        AS allocated_payment_revenue,
    CAST(ROUND(item_daily.product_revenue, 2) AS NUMERIC) AS product_revenue,
    CAST(ROUND(item_daily.freight_revenue, 2) AS NUMERIC) AS freight_revenue,
    order_daily.orders_count,
    order_daily.customers_count,
    item_daily.items_count,
    CAST(ROUND(order_daily.average_order_value, 2) AS NUMERIC)
        AS average_order_value,
    CAST(ROUND(order_daily.average_paid_order_value, 2) AS NUMERIC)
        AS average_paid_order_value,
    CAST(ROUND(item_daily.average_delivery_days, 2) AS NUMERIC)
        AS average_delivery_days,
    item_daily.late_deliveries_count
FROM item_daily
LEFT JOIN order_daily USING (order_purchase_date)
