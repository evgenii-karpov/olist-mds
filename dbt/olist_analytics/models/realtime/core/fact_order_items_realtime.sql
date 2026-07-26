{{
    config(
        materialized='table',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

-- depends_on: {{ ref('int_cdc__changed_order_ids') }}

with orders as (
    select orders.*
    from {{ ref('stg_cdc__orders_current') }} as orders
    {% if is_incremental() %}
        inner join {{ ref('int_cdc__changed_order_ids') }} as changed
            on orders.order_id = changed.order_id
    {% endif %}
),

order_items as (
    select items.*
    from {{ ref('stg_cdc__order_items_current') }} as items
    inner join orders on items.order_id = orders.order_id
),

customers as (
    select *
    from {{ ref('dim_customer_realtime_scd2') }}
    where is_current and not is_deleted
),

products as (
    select *
    from {{ ref('dim_product_realtime_scd2') }}
    where is_current and not is_deleted
)

select
    {{
        hash_key(
            "items.order_id || '|' || "
            ~ cast_string('items.order_item_id')
        )
    }} as order_item_key,
    {{ output_column('items.order_id', 'order_id') }},
    {{ output_column('items.order_item_id', 'order_item_id') }},
    {{ output_column('customers.customer_key', 'customer_key') }},
    {{ output_column('products.product_key', 'product_key') }},
    {{ output_column('sellers.seller_key', 'seller_key') }},
    {{ output_column('statuses.order_status_key', 'order_status_key') }},
    {{ output_column('purchase_date.date_key', 'order_purchase_date_key') }},
    {{ output_column('orders.customer_id', 'customer_id') }},
    {{
        output_column(
            'customers.customer_unique_id',
            'customer_unique_id'
        )
    }},
    {{ output_column('items.product_id', 'product_id') }},
    {{ output_column('items.seller_id', 'seller_id') }},
    {{ output_column('orders.order_status', 'order_status') }},
    {{
        output_column(
            'orders.order_purchase_timestamp',
            'order_purchase_timestamp'
        )
    }},
    {{ output_column('orders.order_approved_at', 'order_approved_at') }},
    {{
        output_column(
            'orders.order_delivered_carrier_date',
            'order_delivered_carrier_date'
        )
    }},
    {{
        output_column(
            'orders.order_delivered_customer_date',
            'order_delivered_customer_date'
        )
    }},
    {{
        output_column(
            'orders.order_estimated_delivery_date',
            'order_estimated_delivery_date'
        )
    }},
    {{
        output_column(
            'items.shipping_limit_date',
            'shipping_limit_date'
        )
    }},
    {{ output_column('items.price', 'price') }},
    {{ output_column('items.freight_value', 'freight_value') }},
    items.price + items.freight_value as gross_item_amount,
    {{
        output_column(
            'allocations.allocated_payment_value',
            'allocated_payment_value'
        )
    }},
    {{ days_between(
        'orders.order_purchase_timestamp',
        'orders.order_delivered_customer_date'
    ) }} as delivery_days,
    {{ days_between(
        'orders.order_estimated_delivery_date',
        'orders.order_delivered_customer_date'
    ) }} as delivery_delay_days,
    coalesce(
        orders.order_delivered_customer_date
        > orders.order_estimated_delivery_date,
        false
    ) as is_delivered_late,
    greatest(orders._source_ts, items._source_ts) as max_source_ts,
    greatest(orders._source_lsn, items._source_lsn) as max_source_lsn
from order_items as items
inner join orders on items.order_id = orders.order_id
left join {{ ref('stg_cdc__customers_current') }} as customer_records
    on orders.customer_id = customer_records.customer_id
left join customers
    on customer_records.customer_unique_id = customers.customer_unique_id
left join products on items.product_id = products.product_id
left join {{ ref('dim_seller_realtime') }} as sellers
    on items.seller_id = sellers.seller_id
left join {{ ref('dim_order_status_realtime') }} as statuses
    on orders.order_status = statuses.order_status
left join {{ ref('dim_date_realtime') }} as purchase_date
    on
        {{ cast_date('orders.order_purchase_timestamp') }}
        = purchase_date.date_day
left join {{ ref('int_realtime_order_payment_allocations') }} as allocations
    on
        items.order_id = allocations.order_id
        and items.order_item_id = allocations.order_item_id
