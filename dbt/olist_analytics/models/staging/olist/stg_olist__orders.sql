with ranked as (
    select
        {{ cast_string('order_id', 256) }} as order_id,
        {{ cast_string('customer_id', 256) }} as customer_id,
        {{ cast_string('lower(trim(order_status))', 64) }} as order_status,
        {{ cast_timestamp('order_purchase_timestamp') }}
            as order_purchase_timestamp,
        {{ cast_timestamp('order_approved_at') }} as order_approved_at,
        {{ cast_timestamp('order_delivered_carrier_date') }}
            as order_delivered_carrier_date,
        {{ cast_timestamp('order_delivered_customer_date') }}
            as order_delivered_customer_date,
        {{ cast_timestamp('order_estimated_delivery_date') }}
            as order_estimated_delivery_date,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by order_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'orders') }}
)

select
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
