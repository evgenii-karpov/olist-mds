{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

with fact_diff as (
    select
        'fact_order_items' as metric_name,
        coalesce(batch.order_id, realtime.order_id)
        || '|' || {{ cast_string(
            'coalesce(batch.order_item_id, realtime.order_item_id)'
        ) }}
            as grain_key
    from {{ ref('fact_order_items') }} as batch
    full outer join {{ ref('fact_order_items_realtime') }} as realtime
        on
            batch.order_id = realtime.order_id
            and batch.order_item_id = realtime.order_item_id
    where
        batch.order_id is null
        or realtime.order_id is null
        or {{ is_distinct('batch.customer_id', 'realtime.customer_id') }}
        or {{ is_distinct('batch.product_id', 'realtime.product_id') }}
        or {{ is_distinct('batch.seller_id', 'realtime.seller_id') }}
        or {{ is_distinct('batch.order_status', 'realtime.order_status') }}
        or {{ is_distinct(
            utc_timestamp('batch.order_purchase_timestamp'),
            utc_timestamp('realtime.order_purchase_timestamp')
        ) }}
        or {{ is_distinct('batch.price', 'realtime.price') }}
        or {{ is_distinct('batch.freight_value', 'realtime.freight_value') }}
        or {{ is_distinct(
            'batch.gross_item_amount',
            'realtime.gross_item_amount'
        ) }}
        or {{ is_distinct(
            'batch.allocated_payment_value',
            'realtime.allocated_payment_value'
        ) }}
),

daily_diff as (
    select
        'mart_daily_revenue' as metric_name,
        {{ cast_string(
            'coalesce(batch.order_purchase_date, realtime.order_purchase_date)'
        ) }}
            as grain_key
    from {{ ref('mart_daily_revenue') }} as batch
    full outer join {{ ref('mart_daily_revenue_realtime') }} as realtime
        on batch.order_purchase_date = realtime.order_purchase_date
    where
        batch.order_purchase_date is null
        or realtime.order_purchase_date is null
        or {{ is_distinct('batch.gross_revenue', 'realtime.gross_revenue') }}
        or {{ is_distinct(
            'batch.allocated_payment_revenue',
            'realtime.allocated_payment_revenue'
        ) }}
        or {{ is_distinct(
            'batch.product_revenue',
            'realtime.product_revenue'
        ) }}
        or {{ is_distinct(
            'batch.freight_revenue',
            'realtime.freight_revenue'
        ) }}
        or {{ is_distinct('batch.orders_count', 'realtime.orders_count') }}
        or {{ is_distinct(
            'batch.customers_count',
            'realtime.customers_count'
        ) }}
        or {{ is_distinct('batch.items_count', 'realtime.items_count') }}
        or {{ is_distinct(
            'batch.average_order_value',
            'realtime.average_order_value'
        ) }}
        or {{ is_distinct(
            'batch.average_paid_order_value',
            'realtime.average_paid_order_value'
        ) }}
        or {{ is_distinct(
            'batch.average_delivery_days',
            'realtime.average_delivery_days'
        ) }}
        or {{ is_distinct(
            'batch.late_deliveries_count',
            'realtime.late_deliveries_count'
        ) }}
),

monthly_diff as (
    select
        'mart_monthly_arpu' as metric_name,
        {{ cast_string('coalesce(batch.order_month, realtime.order_month)') }}
            as grain_key
    from {{ ref('mart_monthly_arpu') }} as batch
    full outer join {{ ref('mart_monthly_arpu_realtime') }} as realtime
        on batch.order_month = realtime.order_month
    where
        batch.order_month is null
        or realtime.order_month is null
        or {{ is_distinct(
            'batch.active_customers',
            'realtime.active_customers'
        ) }}
        or {{ is_distinct('batch.total_revenue', 'realtime.total_revenue') }}
        or {{ is_distinct('batch.arpu', 'realtime.arpu') }}
        or {{ is_distinct('batch.orders_count', 'realtime.orders_count') }}
        or {{ is_distinct(
            'batch.orders_per_customer',
            'realtime.orders_per_customer'
        ) }}
        or {{ is_distinct(
            'batch.average_order_value',
            'realtime.average_order_value'
        ) }}
        or {{ is_distinct(
            'batch.repeat_customer_rate',
            'realtime.repeat_customer_rate'
        ) }}
)

select * from fact_diff
union all
select * from daily_diff
union all
select * from monthly_diff
