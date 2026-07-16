{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_current_model('stg_cdc__customers_events', ['customer_id']) }}
