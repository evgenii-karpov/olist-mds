{{ config(tags=['realtime_transform', 'realtime_quality']) }}

select distinct
    {{ hash_key('order_status') }} as order_status_key,
    order_status
from {{ ref('stg_cdc__orders_current') }}
