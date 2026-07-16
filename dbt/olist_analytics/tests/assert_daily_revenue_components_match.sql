{{ config(tags=['batch_quality']) }}

select
    order_purchase_date,
    gross_revenue,
    product_revenue,
    freight_revenue
from {{ ref('mart_daily_revenue') }}
where abs(gross_revenue - (product_revenue + freight_revenue)) > 0.05
