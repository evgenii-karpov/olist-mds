{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_history_model('stg_cdc__sellers_events', ['seller_id']) }}
