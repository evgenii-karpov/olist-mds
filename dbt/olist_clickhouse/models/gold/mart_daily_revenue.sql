{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['order_purchase_date'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

WITH item_facts AS
(
    SELECT
        toDate(order_purchase_timestamp) AS order_purchase_date,
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
    WHERE
        sync_run_seq = {{ sync_run_seq_sql() }}
        AND order_purchase_timestamp IS NOT NULL
),

order_level AS
(
    SELECT
        order_purchase_date,
        order_id,
        customer_unique_id,
        sum(gross_item_amount) AS order_gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount))
            AS order_payment_revenue
    FROM item_facts
    GROUP BY order_purchase_date, order_id, customer_unique_id
),

item_daily AS
(
    SELECT
        order_purchase_date,
        sum(gross_item_amount) AS gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount))
            AS allocated_payment_revenue,
        sum(price) AS product_revenue,
        sum(freight_value) AS freight_revenue,
        countDistinct(order_item_key) AS items_count,
        avg(delivery_days) AS average_delivery_days,
        countIf(is_delivered_late) AS late_deliveries_count
    FROM item_facts
    GROUP BY order_purchase_date
),

order_daily AS
(
    SELECT
        order_purchase_date,
        countDistinct(order_id) AS orders_count,
        countDistinct(customer_unique_id) AS customers_count,
        avg(order_gross_revenue) AS average_order_value,
        avg(order_payment_revenue) AS average_paid_order_value
    FROM order_level
    GROUP BY order_purchase_date
)

SELECT
    {{ candidate_run_columns() }},
    item_daily.order_purchase_date,
    CAST(round(item_daily.gross_revenue, 2), 'Decimal(18, 2)')
        AS gross_revenue,
    CAST(round(item_daily.allocated_payment_revenue, 2), 'Decimal(18, 2)')
        AS allocated_payment_revenue,
    CAST(round(item_daily.product_revenue, 2), 'Decimal(18, 2)')
        AS product_revenue,
    CAST(round(item_daily.freight_revenue, 2), 'Decimal(18, 2)')
        AS freight_revenue,
    order_daily.orders_count,
    order_daily.customers_count,
    item_daily.items_count,
    CAST(round(order_daily.average_order_value, 2), 'Nullable(Decimal(18, 2))')
        AS average_order_value,
    CAST(
        round(order_daily.average_paid_order_value, 2),
        'Nullable(Decimal(18, 2))'
    ) AS average_paid_order_value,
    CAST(
        round(item_daily.average_delivery_days, 2),
        'Nullable(Decimal(18, 2))'
    ) AS average_delivery_days,
    item_daily.late_deliveries_count
FROM item_daily
LEFT JOIN order_daily USING (order_purchase_date)
