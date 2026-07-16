{{ config(tags=['realtime_transform', 'realtime_quality']) }}

select * from {{ source('raw_cdc', 'order_payments') }}
