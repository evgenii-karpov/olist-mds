{% macro delete_stale_fact_order_items() -%}
    {% if is_incremental() -%}
        delete from {{ this }}
        where order_item_key not in (
            select source_keys.order_item_key
            from (
                select
                    {{
                        hash_key(
                            "order_items.order_id || '|' || "
                            ~ cast_string('order_items.order_item_id')
                        )
                    }} as order_item_key
                from {{ ref('stg_olist__order_items') }} as order_items
                inner join {{ ref('stg_olist__orders') }} as orders
                    on order_items.order_id = orders.order_id
            ) as source_keys
            where source_keys.order_item_key is not null
        )
    {%- else -%}
        select 1
    {%- endif %}
{%- endmacro %}
