with ranked as (
    select
        {{ cast_string('product_id', 256) }} as product_id,
        {{ cast_string('lower(trim(product_category_name))', 256) }}
            as product_category_name,
        {{ cast_int('product_name_lenght') }} as product_name_length,
        {{ cast_int('product_description_lenght') }}
            as product_description_length,
        {{ cast_int('product_photos_qty') }} as product_photos_qty,
        {{ cast_int('product_weight_g') }} as product_weight_g,
        {{ cast_int('product_length_cm') }} as product_length_cm,
        {{ cast_int('product_height_cm') }} as product_height_cm,
        {{ cast_int('product_width_cm') }} as product_width_cm,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by product_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'products') }}
)

select
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
