{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['order_month'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

WITH item_facts AS
(
    SELECT
        toDate(toStartOfMonth(order_purchase_timestamp)) AS order_month,
        order_id,
        customer_unique_id,
        coalesce(allocated_payment_value, gross_item_amount) AS revenue_amount
    FROM {{ ref('fact_order_items') }}
    WHERE
        sync_run_seq = {{ sync_run_seq_sql() }}
        AND order_purchase_timestamp IS NOT NULL
        AND customer_unique_id IS NOT NULL
),

customer_month AS
(
    SELECT
        order_month,
        customer_unique_id,
        countDistinct(order_id) AS customer_orders_count,
        sum(revenue_amount) AS customer_revenue
    FROM item_facts
    GROUP BY order_month, customer_unique_id
),

monthly AS
(
    SELECT
        order_month,
        countDistinct(customer_unique_id) AS active_customers,
        sum(customer_revenue) AS total_revenue,
        toInt64(sum(customer_orders_count)) AS orders_count,
        avg(customer_orders_count) AS orders_per_customer,
        countIf(customer_orders_count > 1) AS repeat_customers
    FROM customer_month
    GROUP BY order_month
)

SELECT
    {{ candidate_run_columns() }},
    order_month,
    active_customers,
    CAST(round(total_revenue, 2), 'Decimal(18, 2)') AS total_revenue,
    if(
        active_customers > 0,
        CAST(round(total_revenue / active_customers, 2), 'Nullable(Decimal(18, 2))'),
        CAST(NULL, 'Nullable(Decimal(18, 2))')
    ) AS arpu,
    orders_count,
    CAST(round(orders_per_customer, 2), 'Nullable(Decimal(18, 2))')
        AS orders_per_customer,
    if(
        orders_count > 0,
        CAST(round(total_revenue / orders_count, 2), 'Nullable(Decimal(18, 2))'),
        CAST(NULL, 'Nullable(Decimal(18, 2))')
    ) AS average_order_value,
    if(
        active_customers > 0,
        CAST(
            round(toDecimal64(repeat_customers, 6) / active_customers, 2),
            'Nullable(Decimal(18, 2))'
        ),
        CAST(NULL, 'Nullable(Decimal(18, 2))')
    ) AS repeat_customer_rate
FROM monthly
