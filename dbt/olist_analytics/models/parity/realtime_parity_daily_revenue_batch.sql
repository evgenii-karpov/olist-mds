{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

select
    {{ cast_date('order_purchase_date') }} as order_purchase_date,
    {{ cast_decimal('gross_revenue', 18, 2) }} as gross_revenue,
    {{ cast_decimal('allocated_payment_revenue', 18, 2) }}
        as allocated_payment_revenue,
    {{ cast_decimal('product_revenue', 18, 2) }} as product_revenue,
    {{ cast_decimal('freight_revenue', 18, 2) }} as freight_revenue,
    {{ cast_bigint('orders_count') }} as orders_count,
    {{ cast_bigint('customers_count') }} as customers_count,
    {{ cast_bigint('items_count') }} as items_count,
    {{ cast_decimal('average_order_value', 18, 2) }} as average_order_value,
    {{ cast_decimal('average_paid_order_value', 18, 2) }}
        as average_paid_order_value,
    {{ cast_decimal('average_delivery_days', 18, 2) }} as average_delivery_days,
    {{ cast_bigint('late_deliveries_count') }} as late_deliveries_count
from {{ ref('mart_daily_revenue') }}
