{{ config(tags=['realtime_transform', 'realtime_quality']) }}

{{ cdc_history_model(
    'stg_cdc__order_payments_events',
    ['order_id', 'payment_sequential']
) }}
