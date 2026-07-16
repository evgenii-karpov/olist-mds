{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_current_model(
    'stg_cdc__order_items_events',
    ['order_id', 'order_item_id']
) }}
