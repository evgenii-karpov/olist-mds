{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

{{ parity_checksum_row(
    'customers_primary_keys', 'stg_olist__customers',
    'stg_cdc__customers_current', 'customer_id', 'customer_id'
) }}
union all
{{ parity_checksum_row(
    'orders_primary_keys', 'stg_olist__orders',
    'stg_cdc__orders_current', 'order_id', 'order_id'
) }}
union all
{{ parity_checksum_row(
    'order_items_primary_keys', 'stg_olist__order_items',
    'stg_cdc__order_items_current',
    "order_id || '|' || order_item_id::varchar",
    "order_id || '|' || order_item_id::varchar"
) }}
union all
{{ parity_checksum_row(
    'order_payments_primary_keys', 'stg_olist__order_payments',
    'stg_cdc__order_payments_current',
    "order_id || '|' || payment_sequential::varchar",
    "order_id || '|' || payment_sequential::varchar"
) }}
union all
{{ parity_checksum_row(
    'order_reviews_primary_keys', 'stg_olist__order_reviews',
    'stg_cdc__order_reviews_current',
    "review_id || '|' || order_id", "review_id || '|' || order_id"
) }}
union all
{{ parity_checksum_row(
    'products_primary_keys', 'stg_olist__products',
    'stg_cdc__products_current', 'product_id', 'product_id'
) }}
union all
{{ parity_checksum_row(
    'sellers_primary_keys', 'stg_olist__sellers',
    'stg_cdc__sellers_current', 'seller_id', 'seller_id'
) }}
union all
{{ parity_checksum_row(
    'translations_primary_keys', 'stg_olist__product_category_translation',
    'stg_cdc__product_category_translation_current',
    'product_category_name', 'product_category_name'
) }}
