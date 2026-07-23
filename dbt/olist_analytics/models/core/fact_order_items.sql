{% if target.type == 'clickhouse' %}
    {{
        config(
            materialized='incremental',
            incremental_strategy='insert_overwrite',
            partition_by="toYYYYMM(coalesce(toDate(order_purchase_timestamp), toDate('1900-01-01')))",
            order_by=[
                'order_purchase_timestamp',
                'order_id',
                'order_item_id'
            ],
            clickhouse_drop_empty_partitions=true,
            pre_hook=[
                "{{ clickhouse_drop_fact_order_items_affected_partitions() }}",
                "{{ clickhouse_prepare_fact_order_items_affected_partitions() }}"
            ],
            post_hook="{{ clickhouse_drop_fact_order_items_affected_partitions() }}"
        )
    }}
{% else %}
    {{
        config(
            materialized='incremental',
            unique_key='order_item_key',
            incremental_strategy='delete+insert',
            pre_hook="{{ delete_stale_fact_order_items() }}"
        )
    }}
{% endif %}

{% if target.type == 'redshift' %}
    {{
        config(
            sort='order_purchase_timestamp',
            dist='order_id'
        )
    }}
{% endif %}

{% set lookback_days = var('lookback_days', 3) | int %}

-- The incremental branch references correction feeds to widen the reprocessing
-- window when SCD2 changes are business-effective in the past.
-- depends_on: {{ ref('stg_olist__customer_profile_changes') }}
-- depends_on: {{ ref('stg_olist__product_attribute_changes') }}

with

source_orders as (
    select *
    from {{ ref('stg_olist__orders') }}
),

source_order_items as (
    select *
    from {{ ref('stg_olist__order_items') }}
),

{% if is_incremental() %}

    {% if target.type != 'clickhouse' %}

        incremental_reprocess_boundaries as (
            select
                coalesce(
                {{ dateadd_days(
                    'max(order_purchase_timestamp)',
                    lookback_days * -1
                ) }},
                    {{ timestamp_literal('1900-01-01') }}
                ) as reprocess_from
            from {{ this }}

            union all

            select min(effective_at) as reprocess_from
            from {{ ref('stg_olist__customer_profile_changes') }}

            union all

            select min(effective_at) as reprocess_from
            from {{ ref('stg_olist__product_attribute_changes') }}

            union all

            select min(source_orders.order_purchase_timestamp) as reprocess_from
            from source_order_items
            inner join source_orders
                on source_order_items.order_id = source_orders.order_id
            left join {{ this }} as existing_fact
                on
                    {{
                        hash_key(
                            "source_order_items.order_id || '|' || "
                            ~ cast_string('source_order_items.order_item_id')
                        )
                    }} = existing_fact.order_item_key
            where existing_fact.order_item_key is null
        ),

        incremental_reprocess_window as (
            select min(reprocess_from) as reprocess_from
            from incremental_reprocess_boundaries
            where reprocess_from is not null
        ),

    {% endif %}

{% endif %}

orders as (
    select *
    from source_orders

    {% if is_incremental() %}
        {% if target.type == 'clickhouse' %}
            where {{ fact_order_items_purchase_partition_id('order_purchase_timestamp') }} in (
                select partition_id
                from {{ fact_order_items_affected_partitions_relation() }}
            )
        {% else %}
            where order_purchase_timestamp >= (
                select incremental_reprocess_window.reprocess_from
                from incremental_reprocess_window
            )
        {% endif %}
    {% endif %}
),

customers as (
    select
        customer_id,
        customer_unique_id
    from {{ ref('stg_olist__customers') }}
),

payment_allocations as (
    select
        order_id,
        order_item_id,
        allocated_payment_value
    from {{ ref('int_order_payment_allocations') }}
),

customer_dim as (
    select
        customer_key,
        customer_unique_id,
        valid_from,
        valid_to
    from {{ ref('dim_customer_scd2') }}
),

product_dim as (
    select
        product_key,
        product_id,
        valid_from,
        valid_to
    from {{ ref('dim_product_scd2') }}
),

seller_dim as (
    select
        seller_key,
        seller_id
    from {{ ref('dim_seller') }}
),

order_status_dim as (
    select
        order_status_key,
        order_status
    from {{ ref('dim_order_status') }}
),

dates as (
    select
        date_key,
        date_day
    from {{ ref('dim_date') }}
),

order_items as (
    select order_items.*
    from source_order_items as order_items
    inner join orders
        on order_items.order_id = orders.order_id
),

fact_base as (
    select
        {{
            hash_key(
                "order_items.order_id || '|' || "
                ~ cast_string('order_items.order_item_id')
            )
        }} as order_item_key,
        {{ output_column('order_items.order_id', 'order_id') }},
        {{ output_column('order_items.order_item_id', 'order_item_id') }},
        {{ output_column('orders.customer_id', 'customer_id') }},
        {{
            output_column(
                'customers.customer_unique_id',
                'customer_unique_id'
            )
        }},
        {{ output_column('order_items.product_id', 'product_id') }},
        {{ output_column('order_items.seller_id', 'seller_id') }},
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
                'order_items.shipping_limit_date',
                'shipping_limit_date'
            )
        }},
        {{ output_column('order_items.price', 'price') }},
        {{ output_column('order_items.freight_value', 'freight_value') }},
        {{
            cast_decimal(
                'order_items.price + order_items.freight_value',
                18,
                2
            )
        }} as gross_item_amount,
        {{
            output_column(
                'payment_allocations.allocated_payment_value',
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
        {{ output_column('orders._batch_id', '_batch_id') }},
        greatest(orders._loaded_at, order_items._loaded_at) as _loaded_at
    from order_items
    inner join orders
        on order_items.order_id = orders.order_id
    left join customers
        on orders.customer_id = customers.customer_id
    left join payment_allocations
        on
            order_items.order_id = payment_allocations.order_id
            and order_items.order_item_id = payment_allocations.order_item_id
)

select
    fact_base.order_item_key,
    fact_base.order_id,
    fact_base.order_item_id,
    customer_dim.customer_key,
    product_dim.product_key,
    seller_dim.seller_key,
    order_status_dim.order_status_key,
    purchase_date.date_key as order_purchase_date_key,
    approved_date.date_key as order_approved_date_key,
    delivered_date.date_key as order_delivered_customer_date_key,
    estimated_delivery_date.date_key as order_estimated_delivery_date_key,
    {{ output_column('fact_base.customer_id', 'customer_id') }},
    {{ output_column('fact_base.customer_unique_id', 'customer_unique_id') }},
    {{ output_column('fact_base.product_id', 'product_id') }},
    {{ output_column('fact_base.seller_id', 'seller_id') }},
    {{ output_column('fact_base.order_status', 'order_status') }},
    {{
        output_column(
            'fact_base.order_purchase_timestamp',
            'order_purchase_timestamp'
        )
    }},
    {{ output_column('fact_base.order_approved_at', 'order_approved_at') }},
    {{
        output_column(
            'fact_base.order_delivered_carrier_date',
            'order_delivered_carrier_date'
        )
    }},
    {{
        output_column(
            'fact_base.order_delivered_customer_date',
            'order_delivered_customer_date'
        )
    }},
    {{
        output_column(
            'fact_base.order_estimated_delivery_date',
            'order_estimated_delivery_date'
        )
    }},
    {{ output_column('fact_base.shipping_limit_date', 'shipping_limit_date') }},
    {{ output_column('fact_base.price', 'price') }},
    {{ output_column('fact_base.freight_value', 'freight_value') }},
    {{ output_column('fact_base.gross_item_amount', 'gross_item_amount') }},
    {{
        output_column(
            'fact_base.allocated_payment_value',
            'allocated_payment_value'
        )
    }},
    {{ output_column('fact_base.delivery_days', 'delivery_days') }},
    {{ output_column('fact_base.delivery_delay_days', 'delivery_delay_days') }},
    {{ output_column('fact_base.is_delivered_late', 'is_delivered_late') }},
    {{ output_column('fact_base._batch_id', '_batch_id') }},
    {{ output_column('fact_base._loaded_at', '_loaded_at') }}
from fact_base
left join customer_dim
    on
        fact_base.customer_unique_id = customer_dim.customer_unique_id
        and fact_base.order_purchase_timestamp >= customer_dim.valid_from
        and fact_base.order_purchase_timestamp
        < coalesce(customer_dim.valid_to, {{ max_valid_timestamp() }})
left join product_dim
    on
        fact_base.product_id = product_dim.product_id
        and fact_base.order_purchase_timestamp >= product_dim.valid_from
        and fact_base.order_purchase_timestamp
        < coalesce(product_dim.valid_to, {{ max_valid_timestamp() }})
left join seller_dim
    on fact_base.seller_id = seller_dim.seller_id
left join order_status_dim
    on fact_base.order_status = order_status_dim.order_status
left join dates as purchase_date
    on
        {{ cast_date('fact_base.order_purchase_timestamp') }}
        = purchase_date.date_day
left join dates as approved_date
    on {{ cast_date('fact_base.order_approved_at') }} = approved_date.date_day
left join dates as delivered_date
    on
        {{ cast_date('fact_base.order_delivered_customer_date') }}
        = delivered_date.date_day
left join dates as estimated_delivery_date
    on
        {{ cast_date('fact_base.order_estimated_delivery_date') }}
        = estimated_delivery_date.date_day
