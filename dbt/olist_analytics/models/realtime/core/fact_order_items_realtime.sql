{{
    config(
        materialized='table',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

-- depends_on: {{ ref('int_cdc__changed_order_ids') }}

with orders as (
    select orders.*
    from {{ ref('stg_cdc__orders_current') }} as orders
    {% if is_incremental() %}
        inner join {{ ref('int_cdc__changed_order_ids') }} as changed
            on orders.order_id = changed.order_id
    {% endif %}
),

order_items as (
    select items.*
    from {{ ref('stg_cdc__order_items_current') }} as items
    inner join orders on items.order_id = orders.order_id
),

customers as (
    select *
    from {{ ref('dim_customer_realtime_scd2') }}
    where is_current and not is_deleted
),

products as (
    select *
    from {{ ref('dim_product_realtime_scd2') }}
    where is_current and not is_deleted
)

select
    {{
        hash_key(
            "items.order_id || '|' || "
            ~ cast_string('items.order_item_id')
        )
    }} as order_item_key,
    items.order_id as order_id,
    items.order_item_id as order_item_id,
    customers.customer_key as customer_key,
    products.product_key as product_key,
    sellers.seller_key as seller_key,
    statuses.order_status_key as order_status_key,
    purchase_date.date_key as order_purchase_date_key,
    orders.customer_id as customer_id,
    customers.customer_unique_id as customer_unique_id,
    items.product_id as product_id,
    items.seller_id as seller_id,
    orders.order_status as order_status,
    orders.order_purchase_timestamp as order_purchase_timestamp,
    orders.order_approved_at as order_approved_at,
    orders.order_delivered_carrier_date as order_delivered_carrier_date,
    orders.order_delivered_customer_date as order_delivered_customer_date,
    orders.order_estimated_delivery_date as order_estimated_delivery_date,
    items.shipping_limit_date as shipping_limit_date,
    items.price as price,
    items.freight_value as freight_value,
    items.price + items.freight_value as gross_item_amount,
    allocations.allocated_payment_value as allocated_payment_value,
    {{ days_between(
        'orders.order_purchase_timestamp',
        'orders.order_delivered_customer_date'
    ) }} as delivery_days,
    {{ days_between(
        'orders.order_estimated_delivery_date',
        'orders.order_delivered_customer_date'
    ) }} as delivery_delay_days,
    coalesce(
        orders.order_delivered_customer_date
        > orders.order_estimated_delivery_date,
        false
    ) as is_delivered_late,
    greatest(orders._source_ts, items._source_ts) as max_source_ts,
    greatest(orders._source_lsn, items._source_lsn) as max_source_lsn
from order_items as items
inner join orders on items.order_id = orders.order_id
left join {{ ref('stg_cdc__customers_current') }} as customer_records
    on orders.customer_id = customer_records.customer_id
left join customers
    on customer_records.customer_unique_id = customers.customer_unique_id
left join products on items.product_id = products.product_id
left join {{ ref('dim_seller_realtime') }} as sellers
    on items.seller_id = sellers.seller_id
left join {{ ref('dim_order_status_realtime') }} as statuses
    on orders.order_status = statuses.order_status
left join {{ ref('dim_date_realtime') }} as purchase_date
    on {{ cast_date('orders.order_purchase_timestamp') }} = purchase_date.date_day
left join {{ ref('int_realtime_order_payment_allocations') }} as allocations
    on
        items.order_id = allocations.order_id
        and items.order_item_id = allocations.order_item_id
