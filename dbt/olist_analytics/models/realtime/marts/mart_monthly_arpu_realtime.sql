{{
    config(
        unique_key='order_month',
        incremental_strategy='merge',
        pre_hook="{{ delete_impacted_periods('order_month', 'int_cdc__changed_periods', 'order_month') }}",
        tags=['realtime_transform', 'realtime_quality']
    )
}}

-- depends_on: {{ ref('int_cdc__changed_periods') }}

with item_facts as (
    select
        date_trunc('month', order_purchase_timestamp)::date as order_month,
        order_id,
        customer_unique_id,
        coalesce(allocated_payment_value, gross_item_amount) as revenue_amount,
        max_source_ts
    from {{ ref('fact_order_items_realtime') }}
    where
        order_purchase_timestamp is not null and customer_unique_id is not null
        {% if is_incremental() %}
            and date_trunc('month', order_purchase_timestamp)::date in (
                select changed.order_month
                from {{ ref('int_cdc__changed_periods') }} as changed
            )
        {% endif %}
),

customer_month as (
    select
        order_month,
        customer_unique_id,
        count(distinct order_id) as customer_orders_count,
        sum(revenue_amount) as customer_revenue,
        max(max_source_ts) as max_source_ts
    from item_facts
    group by order_month, customer_unique_id
),

monthly as (
    select
        order_month,
        count(distinct customer_unique_id) as active_customers,
        sum(customer_revenue) as total_revenue,
        sum(customer_orders_count) as orders_count,
        avg(customer_orders_count) as orders_per_customer,
        sum(case when customer_orders_count > 1 then 1 else 0 end)
            as repeat_customers,
        max(max_source_ts) as max_source_ts
    from customer_month
    group by order_month
)

select
    order_month,
    active_customers,
    {{ round_two_decimals('total_revenue') }} as total_revenue,
    case
        when
            active_customers > 0
            then {{ round_two_decimals('total_revenue / active_customers') }}
    end as arpu,
    orders_count,
    {{ round_two_decimals('orders_per_customer') }} as orders_per_customer,
    case
        when
            orders_count > 0
            then {{ round_two_decimals('total_revenue / orders_count') }}
    end
        as average_order_value,
    case
        when active_customers > 0
            then
                {{ round_two_decimals(
                    'repeat_customers::decimal(18, 6) / active_customers'
                ) }}
    end as repeat_customer_rate,
    max_source_ts
from monthly
