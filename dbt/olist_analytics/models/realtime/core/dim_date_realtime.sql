{{ config(tags=['realtime_transform', 'realtime_quality']) }}

with dates as (
    select order_purchase_timestamp::date as date_day
    from {{ ref('stg_cdc__orders_current') }}
    union
    select order_approved_at::date from {{ ref('stg_cdc__orders_current') }}
    union
    select order_delivered_customer_date::date
    from {{ ref('stg_cdc__orders_current') }}
    union
    select order_estimated_delivery_date::date
    from {{ ref('stg_cdc__orders_current') }}
)

select
    to_char(date_day, 'YYYYMMDD')::integer as date_key,
    date_day
from dates
where date_day is not null
