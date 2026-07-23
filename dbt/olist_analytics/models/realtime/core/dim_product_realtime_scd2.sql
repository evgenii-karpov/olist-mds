{{
    config(
        materialized='table',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

with product_driven_ranked as (
    select
        products.product_id as product_id,
        products.product_category_name as product_category_name,
        products.product_name_lenght as product_name_lenght,
        products.product_description_lenght as product_description_lenght,
        products.product_photos_qty as product_photos_qty,
        products.product_weight_g as product_weight_g,
        products.product_length_cm as product_length_cm,
        products.product_height_cm as product_height_cm,
        products.product_width_cm as product_width_cm,
        products._event_id as _event_id,
        products._op as _op,
        products._source_ts as _source_ts,
        products._source_lsn as _source_lsn,
        products._tx_order as _tx_order,
        products._partition as _partition,
        products._offset as _offset,
        translations.product_category_name_english,
        translations._op as translation_op,
        row_number() over (
            partition by products._event_id
            order by {{ cdc_order_by('translations', 'desc') }}
        ) as translation_row_number
    from {{ ref('stg_cdc__products_events') }} as products
    left join
        {{ ref('stg_cdc__product_category_translation_events') }}
            as translations
        on
            products.product_category_name
            = translations.product_category_name
            and {{ cdc_order_value('translations') }}
                <= {{ cdc_order_value('products') }}
),

product_driven as (
    select
        product_id,
        product_category_name,
        case
            when translation_op = 'd' then null
            else product_category_name_english
        end as product_category_name_english,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        _event_id as version_event_id,
        _source_ts,
        _source_lsn,
        _tx_order,
        _partition,
        _offset,
        {{ bool_value("_op = 'd'") }} as is_deleted
    from product_driven_ranked
    where translation_row_number = 1
),

translation_driven_ranked as (
    select
        products.product_id as product_id,
        products.product_category_name as product_category_name,
        translations.product_category_name as translation_category_name,
        translations.product_category_name_english,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        translations._event_id as version_event_id,
        translations._source_ts,
        translations._source_lsn,
        translations._tx_order,
        translations._partition,
        translations._offset,
        translations._op as translation_op,
        products._op as product_op,
        row_number() over (
            partition by translations._event_id, products.product_id
            order by {{ cdc_order_by('products', 'desc') }}
        ) as product_row_number
    from
        {{ ref('stg_cdc__product_category_translation_events') }}
            as translations
    inner join {{ ref('stg_cdc__products_events') }} as products
        on
            {{ cdc_order_value('products') }}
            <= {{ cdc_order_value('translations') }}
),

translation_driven as (
    select
        product_id,
        product_category_name,
        case
            when translation_op = 'd' then null
            else product_category_name_english
        end as product_category_name_english,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        version_event_id,
        _source_ts,
        _source_lsn,
        _tx_order,
        _partition,
        _offset,
        {{ bool_value('false') }} as is_deleted
    from translation_driven_ranked
    where
        product_row_number = 1
        and product_op <> 'd'
        and product_category_name = translation_category_name
),

versions as (
    select * from product_driven
    union all
    select * from translation_driven
),

windowed as (
    select
        versions.*,
        lead(versions._source_ts) over (
            partition by versions.product_id
            order by {{ cdc_order_by('versions') }}
        ) as valid_to,
        {{ bool_value(
            'row_number() over (partition by versions.product_id order by '
            ~ cdc_order_by('versions', 'desc')
            ~ ') = 1'
        ) }} as is_current
    from versions
)

select
    {{ hash_key("product_id || '|' || version_event_id") }} as product_key,
    product_id,
    product_category_name,
    product_category_name_english,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    _source_ts as valid_from,
    valid_to,
    is_current,
    is_deleted,
    _source_lsn,
    _tx_order,
    _partition,
    _offset
from windowed
