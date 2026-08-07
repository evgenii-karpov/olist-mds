{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'order_id', 'order_item_id'],
        alias='fact_order_items__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'order_id'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

WITH orders AS
(
    SELECT *
    FROM {{ ref('stg_orders_current') }}
),
order_items AS
(
    SELECT *
    FROM {{ ref('stg_order_items_current') }}
),
customers AS
(
    SELECT customer_id, customer_unique_id
    FROM {{ ref('stg_customers_current') }}
    WHERE NOT is_deleted
),
payment_allocations AS
(
    SELECT order_id, order_item_id, allocated_payment_value
    FROM {{ ref('int_order_payment_allocations') }}
),
customer_dimension AS
(
    SELECT *
    FROM {{ ref('dim_customer_scd2') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
        AND is_current
),
product_dimension AS
(
    SELECT *
    FROM {{ ref('dim_product_scd2') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
        AND is_current
),
seller_dimension AS
(
    SELECT *
    FROM {{ ref('dim_seller') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
),
status_dimension AS
(
    SELECT *
    FROM {{ ref('dim_order_status') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
        AND operation_type != 'DELETE'
),
date_dimension AS
(
    SELECT *
    FROM {{ ref('dim_date') }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
)
SELECT
    {{ history_columns(
        "CASE WHEN order_items.is_deleted OR orders.is_deleted "
        "THEN 'DELETE' ELSE 'UPSERT' END"
    ) }},
    LOWER(TO_HEX(MD5(CONCAT(
        order_items.order_id, '|', CAST(order_items.order_item_id AS STRING)
    )))) AS order_item_key,
    order_items.order_id,
    order_items.order_item_id,
    customer_dimension.customer_key,
    product_dimension.product_key,
    seller_dimension.seller_key,
    status_dimension.order_status_key,
    purchase_date.date_key AS order_purchase_date_key,
    approved_date.date_key AS order_approved_date_key,
    delivered_date.date_key AS order_delivered_customer_date_key,
    estimated_date.date_key AS order_estimated_delivery_date_key,
    orders.customer_id,
    customers.customer_unique_id,
    order_items.product_id,
    order_items.seller_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    order_items.shipping_limit_date,
    order_items.price,
    order_items.freight_value,
    CAST(order_items.price + order_items.freight_value AS NUMERIC)
        AS gross_item_amount,
    payment_allocations.allocated_payment_value,
    DATE_DIFF(
        DATE(orders.order_delivered_customer_date),
        DATE(orders.order_purchase_timestamp),
        DAY
    ) AS delivery_days,
    DATE_DIFF(
        DATE(orders.order_delivered_customer_date),
        DATE(orders.order_estimated_delivery_date),
        DAY
    ) AS delivery_delay_days,
    COALESCE(
        orders.order_delivered_customer_date > orders.order_estimated_delivery_date,
        FALSE
    ) AS is_delivered_late
FROM order_items
LEFT JOIN orders
    ON order_items.order_id = orders.order_id
LEFT JOIN customers
    ON orders.customer_id = customers.customer_id
LEFT JOIN payment_allocations
    ON order_items.order_id = payment_allocations.order_id
    AND order_items.order_item_id = payment_allocations.order_item_id
LEFT JOIN customer_dimension
    ON customers.customer_unique_id = customer_dimension.customer_unique_id
    AND orders.order_purchase_timestamp >= customer_dimension.valid_from
    AND orders.order_purchase_timestamp < COALESCE(
        customer_dimension.valid_to,
        TIMESTAMP('2299-12-31 00:00:00+00')
    )
LEFT JOIN product_dimension
    ON order_items.product_id = product_dimension.product_id
    AND orders.order_purchase_timestamp >= product_dimension.valid_from
    AND orders.order_purchase_timestamp < COALESCE(
        product_dimension.valid_to,
        TIMESTAMP('2299-12-31 00:00:00+00')
    )
LEFT JOIN seller_dimension
    ON order_items.seller_id = seller_dimension.seller_id
LEFT JOIN status_dimension
    ON orders.order_status = status_dimension.order_status
LEFT JOIN date_dimension AS purchase_date
    ON DATE(orders.order_purchase_timestamp) = purchase_date.date_day
LEFT JOIN date_dimension AS approved_date
    ON DATE(orders.order_approved_at) = approved_date.date_day
LEFT JOIN date_dimension AS delivered_date
    ON DATE(orders.order_delivered_customer_date) = delivered_date.date_day
LEFT JOIN date_dimension AS estimated_date
    ON DATE(orders.order_estimated_delivery_date) = estimated_date.date_day
