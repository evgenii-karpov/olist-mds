{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

select
    {{ cast_date('order_month') }} as order_month,
    {{ cast_bigint('active_customers') }} as active_customers,
    {{ cast_decimal('total_revenue', 18, 2) }} as total_revenue,
    {{ cast_decimal('arpu', 18, 2) }} as arpu,
    {{ cast_bigint('orders_count') }} as orders_count,
    {{ cast_decimal('orders_per_customer', 18, 2) }} as orders_per_customer,
    {{ cast_decimal('average_order_value', 18, 2) }} as average_order_value,
    {{ cast_decimal('repeat_customer_rate', 18, 2) }} as repeat_customer_rate
from {{ ref('mart_monthly_arpu') }}
