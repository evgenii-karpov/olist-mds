{{ config(tags=['realtime_transform']) }}

select distinct
    {{ cast_date('orders.order_purchase_timestamp') }} as order_purchase_date,
    {{ month_start('orders.order_purchase_timestamp') }} as order_month
from {{ ref('hist_cdc__orders') }} as orders
inner join {{ ref('int_cdc__changed_order_ids') }} as changed
    on orders.order_id = changed.order_id
where orders.order_purchase_timestamp is not null
