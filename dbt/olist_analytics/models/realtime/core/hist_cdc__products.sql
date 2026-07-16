{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_history_model('stg_cdc__products_events', ['product_id']) }}
