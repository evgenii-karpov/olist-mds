with ranked as (
    select
        {{ cast_string('customer_id', 256) }} as customer_id,
        {{ cast_string('customer_unique_id', 256) }} as customer_unique_id,
        {{ cast_string('customer_zip_code_prefix', 16) }}
            as customer_zip_code_prefix,
        {{ cast_string('lower(trim(customer_city))', 256) }} as customer_city,
        {{ cast_string('upper(trim(customer_state))', 2) }} as customer_state,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by customer_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'customers') }}
)

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
