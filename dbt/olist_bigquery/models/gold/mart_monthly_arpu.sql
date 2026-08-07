{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'order_month'],
        alias='mart_monthly_arpu__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'order_month'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

WITH item_facts AS
(
    SELECT
        DATE_TRUNC(DATE(order_purchase_timestamp), MONTH) AS order_month,
        order_id,
        customer_unique_id,
        COALESCE(allocated_payment_value, gross_item_amount) AS revenue_amount
    FROM {{ ref('fact_order_items') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
        AND order_purchase_timestamp IS NOT NULL
        AND customer_unique_id IS NOT NULL
),
customer_month AS
(
    SELECT
        order_month,
        customer_unique_id,
        COUNT(DISTINCT order_id) AS customer_orders_count,
        SUM(revenue_amount) AS customer_revenue
    FROM item_facts
    GROUP BY order_month, customer_unique_id
),
monthly AS
(
    SELECT
        order_month,
        COUNT(DISTINCT customer_unique_id) AS active_customers,
        SUM(customer_revenue) AS total_revenue,
        SUM(customer_orders_count) AS orders_count,
        AVG(customer_orders_count) AS orders_per_customer,
        COUNTIF(customer_orders_count > 1) AS repeat_customers
    FROM customer_month
    GROUP BY order_month
)
SELECT
    {{ history_columns("'REPLACE_GRAIN'") }},
    order_month,
    active_customers,
    CAST(ROUND(total_revenue, 2) AS NUMERIC) AS total_revenue,
    CASE
        WHEN active_customers > 0
        THEN CAST(ROUND(SAFE_DIVIDE(total_revenue, active_customers), 2) AS NUMERIC)
        ELSE CAST(NULL AS NUMERIC)
    END AS arpu,
    orders_count,
    CAST(ROUND(orders_per_customer, 2) AS NUMERIC) AS orders_per_customer,
    CASE
        WHEN orders_count > 0
        THEN CAST(ROUND(SAFE_DIVIDE(total_revenue, orders_count), 2) AS NUMERIC)
        ELSE CAST(NULL AS NUMERIC)
    END AS average_order_value,
    CASE
        WHEN active_customers > 0
        THEN CAST(
            ROUND(SAFE_DIVIDE(repeat_customers, active_customers), 2) AS NUMERIC
        )
        ELSE CAST(NULL AS NUMERIC)
    END AS repeat_customer_rate
FROM monthly
