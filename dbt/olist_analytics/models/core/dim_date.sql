with date_spine as (
    select distinct {{ cast_date('order_purchase_timestamp') }} as date_day
    from {{ ref('stg_olist__orders') }}
    where order_purchase_timestamp is not null

    union distinct

    select distinct {{ cast_date('order_approved_at') }} as date_day
    from {{ ref('stg_olist__orders') }}
    where order_approved_at is not null

    union distinct

    select distinct {{ cast_date('order_delivered_carrier_date') }} as date_day
    from {{ ref('stg_olist__orders') }}
    where order_delivered_carrier_date is not null

    union distinct

    select distinct {{ cast_date('order_delivered_customer_date') }} as date_day
    from {{ ref('stg_olist__orders') }}
    where order_delivered_customer_date is not null

    union distinct

    select distinct {{ cast_date('order_estimated_delivery_date') }} as date_day
    from {{ ref('stg_olist__orders') }}
    where order_estimated_delivery_date is not null
)

select
    {{ date_key('date_day') }} as date_key,
    date_day,
    {{ date_part('year', 'date_day') }} as year_number,
    {{ date_part('month', 'date_day') }} as month_number,
    {{ date_part('day', 'date_day') }} as day_number,
    {{ date_part('quarter', 'date_day') }} as quarter_number,
    {{ date_part('week', 'date_day') }} as week_number,
    {{ date_part('dow', 'date_day') }} as day_of_week_number,
    {{ year_month('date_day') }} as year_month,
    {{ month_name('date_day') }} as month_name,
    coalesce({{ date_part('dow', 'date_day') }} in (0, 6), false) as is_weekend
from date_spine
