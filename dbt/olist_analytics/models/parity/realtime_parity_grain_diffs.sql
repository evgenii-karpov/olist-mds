{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

with fact_diff as (
    select
        'fact_order_items' as metric_name,
        coalesce(batch.order_id, realtime.order_id)
        || '|' || coalesce(batch.order_item_id, realtime.order_item_id)::varchar
            as grain_key
    from {{ ref('fact_order_items') }} as batch
    full outer join {{ ref('fact_order_items_realtime') }} as realtime
        on
            batch.order_id = realtime.order_id
            and batch.order_item_id = realtime.order_item_id
    where
        batch.order_id is null
        or realtime.order_id is null
        or batch.customer_id is distinct from realtime.customer_id
        or batch.product_id is distinct from realtime.product_id
        or batch.seller_id is distinct from realtime.seller_id
        or batch.order_status is distinct from realtime.order_status
        or batch.order_purchase_timestamp::timestamp
        is distinct from (realtime.order_purchase_timestamp at time zone 'UTC')::timestamp
        or batch.price is distinct from realtime.price
        or batch.freight_value is distinct from realtime.freight_value
        or batch.gross_item_amount is distinct from realtime.gross_item_amount
        or batch.allocated_payment_value
        is distinct from realtime.allocated_payment_value
),

daily_diff as (
    select
        'mart_daily_revenue' as metric_name,
        coalesce(
            batch.order_purchase_date, realtime.order_purchase_date
        )::varchar
            as grain_key
    from {{ ref('mart_daily_revenue') }} as batch
    full outer join {{ ref('mart_daily_revenue_realtime') }} as realtime
        on batch.order_purchase_date = realtime.order_purchase_date
    where
        batch.order_purchase_date is null
        or realtime.order_purchase_date is null
        or batch.gross_revenue is distinct from realtime.gross_revenue
        or batch.allocated_payment_revenue
        is distinct from realtime.allocated_payment_revenue
        or batch.product_revenue is distinct from realtime.product_revenue
        or batch.freight_revenue is distinct from realtime.freight_revenue
        or batch.orders_count is distinct from realtime.orders_count
        or batch.customers_count is distinct from realtime.customers_count
        or batch.items_count is distinct from realtime.items_count
        or batch.average_order_value
        is distinct from realtime.average_order_value
        or batch.average_paid_order_value
        is distinct from realtime.average_paid_order_value
        or batch.average_delivery_days
        is distinct from realtime.average_delivery_days
        or batch.late_deliveries_count
        is distinct from realtime.late_deliveries_count
),

monthly_diff as (
    select
        'mart_monthly_arpu' as metric_name,
        coalesce(batch.order_month, realtime.order_month)::varchar as grain_key
    from {{ ref('mart_monthly_arpu') }} as batch
    full outer join {{ ref('mart_monthly_arpu_realtime') }} as realtime
        on batch.order_month = realtime.order_month
    where
        batch.order_month is null
        or realtime.order_month is null
        or batch.active_customers is distinct from realtime.active_customers
        or batch.total_revenue is distinct from realtime.total_revenue
        or batch.arpu is distinct from realtime.arpu
        or batch.orders_count is distinct from realtime.orders_count
        or batch.orders_per_customer
        is distinct from realtime.orders_per_customer
        or batch.average_order_value
        is distinct from realtime.average_order_value
        or batch.repeat_customer_rate
        is distinct from realtime.repeat_customer_rate
)

select * from fact_diff
union all
select * from daily_diff
union all
select * from monthly_diff
