{{
    config(
        materialized='table',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

-- depends_on: {{ ref('int_cdc__changed_periods') }}

with item_facts as (
    select
        {{ cast_date('facts.order_purchase_timestamp') }} as order_purchase_date,
        facts.order_id,
        facts.order_item_key,
        facts.customer_unique_id,
        facts.price,
        facts.freight_value,
        facts.gross_item_amount,
        facts.allocated_payment_value,
        facts.delivery_days,
        facts.is_delivered_late,
        facts.max_source_ts
    from {{ ref('fact_order_items_realtime') }} as facts
    {% if is_incremental() %}
        inner join {{ ref('int_cdc__changed_periods') }} as changed
            on
                {{ cast_date('facts.order_purchase_timestamp') }}
                = changed.order_purchase_date
    {% endif %}
    where
        facts.order_purchase_timestamp is not null
),

order_level as (
    select
        order_purchase_date,
        order_id,
        customer_unique_id,
        sum(gross_item_amount) as order_gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount))
            as order_payment_revenue
    from item_facts
    group by order_purchase_date, order_id, customer_unique_id
),

item_daily as (
    select
        order_purchase_date,
        sum(gross_item_amount) as gross_revenue,
        sum(coalesce(allocated_payment_value, gross_item_amount))
            as allocated_payment_revenue,
        sum(price) as product_revenue,
        sum(freight_value) as freight_revenue,
        count(distinct order_item_key) as items_count,
        avg(delivery_days) as average_delivery_days,
        sum(case when is_delivered_late then 1 else 0 end)
            as late_deliveries_count,
        max(max_source_ts) as max_source_ts
    from item_facts
    group by order_purchase_date
),

order_daily as (
    select
        order_purchase_date,
        count(distinct order_id) as orders_count,
        count(distinct customer_unique_id) as customers_count,
        avg(order_gross_revenue) as average_order_value,
        avg(order_payment_revenue) as average_paid_order_value
    from order_level
    group by order_purchase_date
)

select
    item_daily.order_purchase_date,
    {{ round_two_decimals('item_daily.gross_revenue') }} as gross_revenue,
    {{ round_two_decimals('item_daily.allocated_payment_revenue') }}
        as allocated_payment_revenue,
    {{ round_two_decimals('item_daily.product_revenue') }} as product_revenue,
    {{ round_two_decimals('item_daily.freight_revenue') }} as freight_revenue,
    order_daily.orders_count,
    order_daily.customers_count,
    item_daily.items_count,
    {{ round_two_decimals('order_daily.average_order_value') }}
        as average_order_value,
    {{ round_two_decimals('order_daily.average_paid_order_value') }}
        as average_paid_order_value,
    {{ round_two_decimals('item_daily.average_delivery_days') }}
        as average_delivery_days,
    item_daily.late_deliveries_count,
    item_daily.max_source_ts
from item_daily
left join
    order_daily
    on item_daily.order_purchase_date = order_daily.order_purchase_date
