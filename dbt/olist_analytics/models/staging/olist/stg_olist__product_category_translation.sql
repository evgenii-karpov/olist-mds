with ranked as (
    select
        {{ cast_string('lower(trim(product_category_name))', 256) }}
            as product_category_name,
        {{ cast_string('lower(trim(product_category_name_english))', 256) }}
            as product_category_name_english,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by lower(trim(product_category_name))
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'product_category_translation') }}
)

select
    product_category_name,
    product_category_name_english,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
