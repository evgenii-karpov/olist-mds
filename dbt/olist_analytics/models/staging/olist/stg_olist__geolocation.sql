with ranked as (
    select
        {{ cast_string('geolocation_zip_code_prefix', 16) }}
            as geolocation_zip_code_prefix,
        {{ cast_decimal('geolocation_lat', 18, 14) }} as geolocation_lat,
        {{ cast_decimal('geolocation_lng', 18, 14) }} as geolocation_lng,
        {{ cast_string('lower(trim(geolocation_city))', 256) }}
            as geolocation_city,
        {{ cast_string('upper(trim(geolocation_state))', 2) }}
            as geolocation_state,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                lower(trim(geolocation_city)),
                upper(trim(geolocation_state))
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'geolocation') }}
)

select
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
