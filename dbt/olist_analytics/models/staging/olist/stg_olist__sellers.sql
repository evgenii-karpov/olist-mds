with ranked as (
    select
        {{ cast_string('seller_id', 256) }} as seller_id,
        {{ cast_string('seller_zip_code_prefix', 16) }}
            as seller_zip_code_prefix,
        {{ cast_string('lower(trim(seller_city))', 256) }} as seller_city,
        {{ cast_string('upper(trim(seller_state))', 2) }} as seller_state,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by seller_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'sellers') }}
)

select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
