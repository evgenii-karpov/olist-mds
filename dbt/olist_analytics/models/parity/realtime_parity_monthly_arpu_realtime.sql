{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

select
    order_month::date as order_month,
    active_customers::bigint as active_customers,
    total_revenue::numeric(18, 2) as total_revenue,
    arpu::numeric(18, 2) as arpu,
    orders_count::bigint as orders_count,
    orders_per_customer::numeric(18, 2) as orders_per_customer,
    average_order_value::numeric(18, 2) as average_order_value,
    repeat_customer_rate::numeric(18, 2) as repeat_customer_rate
from {{ ref('mart_monthly_arpu_realtime') }}
