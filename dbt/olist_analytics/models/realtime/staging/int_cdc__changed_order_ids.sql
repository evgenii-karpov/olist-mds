{{ config(tags=['realtime_transform']) }}

with direct_order_events as (
    select order_id
    from {{ ref('stg_cdc__orders_events') }}
    where {{ cdc_selected_file_predicate() }}

    union distinct

    select order_id
    from {{ ref('stg_cdc__order_items_events') }}
    where {{ cdc_selected_file_predicate() }}

    union distinct

    select order_id
    from {{ ref('stg_cdc__order_payments_events') }}
    where {{ cdc_selected_file_predicate() }}
),

changed_customers as (
    select customer_id
    from {{ ref('stg_cdc__customers_events') }}
    where {{ cdc_selected_file_predicate() }}
),

changed_products as (
    select product_id
    from {{ ref('stg_cdc__products_events') }}
    where {{ cdc_selected_file_predicate() }}
),

changed_sellers as (
    select seller_id
    from {{ ref('stg_cdc__sellers_events') }}
    where {{ cdc_selected_file_predicate() }}
),

changed_categories as (
    select product_category_name
    from {{ ref('stg_cdc__product_category_translation_events') }}
    where {{ cdc_selected_file_predicate() }}
),

related_orders as (
    select orders.order_id
    from {{ ref('hist_cdc__orders') }} as orders
    inner join changed_customers
        on orders.customer_id = changed_customers.customer_id

    union distinct

    select items.order_id
    from {{ ref('hist_cdc__order_items') }} as items
    inner join
        changed_products
        on items.product_id = changed_products.product_id

    union distinct

    select items.order_id
    from {{ ref('hist_cdc__order_items') }} as items
    inner join changed_sellers on items.seller_id = changed_sellers.seller_id

    union distinct

    select items.order_id
    from {{ ref('hist_cdc__order_items') }} as items
    inner join {{ ref('hist_cdc__products') }} as products
        on items.product_id = products.product_id
    inner join changed_categories
        on
            products.product_category_name
            = changed_categories.product_category_name
)

select distinct order_id
from (
    select order_id from direct_order_events
    union all
    select order_id from related_orders
) as changed
where order_id is not null
