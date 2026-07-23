{% macro order_payment_allocations(order_items_model, payments_model) -%}
with order_item_amounts as (
    select
        order_id,
        order_item_id,
        price,
        freight_value,
        price + freight_value as item_gross_amount,
        sum(price + freight_value) over (partition by order_id) as order_gross_amount
    from {{ ref(order_items_model) }}
),

order_payments as (
    select order_id, sum(payment_value) as order_payment_value
    from {{ ref(payments_model) }}
    group by order_id
)

select
    order_item_amounts.order_id,
    order_item_amounts.order_item_id,
    order_item_amounts.item_gross_amount,
    order_item_amounts.order_gross_amount,
    order_payments.order_payment_value,
    case
        when order_item_amounts.order_gross_amount > 0
            then {{ cast_decimal(
                "round("
                ~ "order_payments.order_payment_value "
                ~ "* order_item_amounts.item_gross_amount "
                ~ "/ order_item_amounts.order_gross_amount, 2)",
                18,
                2
            ) }}
    end as allocated_payment_value
from order_item_amounts
left join order_payments using (order_id)
{%- endmacro %}

{% macro parity_checksum_row(metric_name, batch_model, realtime_model, batch_key, realtime_key) -%}
select
    '{{ metric_name }}' as metric_name,
    (select {{ ordered_string_checksum(batch_key) }}
        from {{ ref(batch_model) }}) as batch_checksum,
    (select {{ ordered_string_checksum(realtime_key) }}
        from {{ ref(realtime_model) }}) as realtime_checksum,
    case
        when
            coalesce(
                (select {{ ordered_string_checksum(batch_key) }}
                    from {{ ref(batch_model) }}),
                ''
            ) = coalesce(
                (select {{ ordered_string_checksum(realtime_key) }}
                    from {{ ref(realtime_model) }}),
                ''
            )
            then 'PASS'
        else 'FAIL'
    end as status
{%- endmacro %}

{% macro ordered_string_checksum(expression) -%}
    {{ return(adapter.dispatch('ordered_string_checksum', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__ordered_string_checksum(expression) -%}
    md5(string_agg({{ expression }}, ',' order by {{ expression }}))
{%- endmacro %}

{% macro clickhouse__ordered_string_checksum(expression) -%}
    lower(hex(MD5(arrayStringConcat(arraySort(groupArray({{ expression }})), ','))))
{%- endmacro %}
