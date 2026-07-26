{{ config(tags=['realtime_transform', 'realtime_quality']) }}

with dates as (
    select {{ cast_date('order_purchase_timestamp') }} as date_day
    from {{ ref('stg_cdc__orders_current') }}
    union distinct
    select {{ cast_date('order_approved_at') }}
    from {{ ref('stg_cdc__orders_current') }}
    union distinct
    select {{ cast_date('order_delivered_customer_date') }}
    from {{ ref('stg_cdc__orders_current') }}
    union distinct
    select {{ cast_date('order_estimated_delivery_date') }}
    from {{ ref('stg_cdc__orders_current') }}
)

select
    {{ date_key('date_day') }} as date_key,
    date_day
from dates
where date_day is not null
