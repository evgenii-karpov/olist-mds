with ranked as (
    select
        {{ cast_string('order_id', 256) }} as order_id,
        {{ cast_int('payment_sequential') }} as payment_sequential,
        {{ cast_string('lower(trim(payment_type))', 64) }} as payment_type,
        {{ cast_int('payment_installments') }} as payment_installments,
        {{ cast_decimal('payment_value', 18, 2) }} as payment_value,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by order_id, payment_sequential
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'order_payments') }}
)

select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
