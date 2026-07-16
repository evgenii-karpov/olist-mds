{{ config(materialized='view', tags=['realtime_transform']) }}

{{ order_payment_allocations(
    'stg_cdc__order_items_current',
    'stg_cdc__order_payments_current'
) }}
