{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_current_model(
    'stg_cdc__product_category_translation_events',
    ['product_category_name']
) }}
