{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

select
    order_purchase_date::date as order_purchase_date,
    gross_revenue::numeric(18, 2) as gross_revenue,
    allocated_payment_revenue::numeric(18, 2) as allocated_payment_revenue,
    product_revenue::numeric(18, 2) as product_revenue,
    freight_revenue::numeric(18, 2) as freight_revenue,
    orders_count::bigint as orders_count,
    customers_count::bigint as customers_count,
    items_count::bigint as items_count,
    average_order_value::numeric(18, 2) as average_order_value,
    average_paid_order_value::numeric(18, 2) as average_paid_order_value,
    average_delivery_days::numeric(18, 2) as average_delivery_days,
    late_deliveries_count::bigint as late_deliveries_count
from {{ ref('mart_daily_revenue_realtime') }}
