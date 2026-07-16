{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_current_model(
    'stg_cdc__order_reviews_events',
    ['review_id', 'order_id']
) }}
