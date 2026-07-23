with ranked as (
    select
        {{ cast_string('order_id', 256) }} as order_id,
        {{ cast_int('order_item_id') }} as order_item_id,
        {{ cast_string('product_id', 256) }} as product_id,
        {{ cast_string('seller_id', 256) }} as seller_id,
        {{ cast_timestamp('shipping_limit_date') }} as shipping_limit_date,
        {{ cast_decimal('price', 18, 2) }} as price,
        {{ cast_decimal('freight_value', 18, 2) }} as freight_value,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by order_id, order_item_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'order_items') }}
)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
