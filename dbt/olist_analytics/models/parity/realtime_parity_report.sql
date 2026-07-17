{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

with

batch_customers as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    from {{ ref('stg_olist__customers') }}
),

realtime_customers as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    from {{ ref('stg_cdc__customers_current') }}
),

customer_mismatches as (
    select
        batch.customer_id as batch_customer_id,
        realtime.customer_id as realtime_customer_id,
        batch.customer_unique_id as batch_customer_unique_id,
        realtime.customer_unique_id as realtime_customer_unique_id,
        batch.customer_zip_code_prefix as batch_customer_zip_code_prefix,
        realtime.customer_zip_code_prefix as realtime_customer_zip_code_prefix,
        batch.customer_city as batch_customer_city,
        realtime.customer_city as realtime_customer_city,
        batch.customer_state as batch_customer_state,
        realtime.customer_state as realtime_customer_state
    from batch_customers as batch
    full outer join realtime_customers as realtime
        on batch.customer_id = realtime.customer_id
),

batch_orders as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp::timestamp as order_purchase_timestamp,
        order_approved_at::timestamp as order_approved_at,
        order_delivered_carrier_date::timestamp as order_delivered_carrier_date,
        order_delivered_customer_date::timestamp as order_delivered_customer_date,
        order_estimated_delivery_date::timestamp
            as order_estimated_delivery_date
    from {{ ref('stg_olist__orders') }}
),

realtime_orders as (
    select
        order_id,
        customer_id,
        order_status,
        (order_purchase_timestamp at time zone 'UTC')::timestamp
            as order_purchase_timestamp,
        (order_approved_at at time zone 'UTC')::timestamp as order_approved_at,
        (order_delivered_carrier_date at time zone 'UTC')::timestamp
            as order_delivered_carrier_date,
        (order_delivered_customer_date at time zone 'UTC')::timestamp
            as order_delivered_customer_date,
        (order_estimated_delivery_date at time zone 'UTC')::timestamp
            as order_estimated_delivery_date
    from {{ ref('stg_cdc__orders_current') }}
),

order_mismatches as (
    select
        batch.order_id as batch_order_id,
        realtime.order_id as realtime_order_id,
        batch.customer_id as batch_customer_id,
        realtime.customer_id as realtime_customer_id,
        batch.order_status as batch_order_status,
        realtime.order_status as realtime_order_status,
        batch.order_purchase_timestamp as batch_order_purchase_timestamp,
        realtime.order_purchase_timestamp as realtime_order_purchase_timestamp,
        batch.order_approved_at as batch_order_approved_at,
        realtime.order_approved_at as realtime_order_approved_at,
        batch.order_delivered_carrier_date
            as batch_order_delivered_carrier_date,
        realtime.order_delivered_carrier_date
            as realtime_order_delivered_carrier_date,
        batch.order_delivered_customer_date
            as batch_order_delivered_customer_date,
        realtime.order_delivered_customer_date
            as realtime_order_delivered_customer_date,
        batch.order_estimated_delivery_date
            as batch_order_estimated_delivery_date,
        realtime.order_estimated_delivery_date
            as realtime_order_estimated_delivery_date
    from batch_orders as batch
    full outer join realtime_orders as realtime
        on batch.order_id = realtime.order_id
),

batch_order_items as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date::timestamp as shipping_limit_date,
        price::numeric(18, 2) as price,
        freight_value::numeric(18, 2) as freight_value
    from {{ ref('stg_olist__order_items') }}
),

realtime_order_items as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        (shipping_limit_date at time zone 'UTC')::timestamp
            as shipping_limit_date,
        price::numeric(18, 2) as price,
        freight_value::numeric(18, 2) as freight_value
    from {{ ref('stg_cdc__order_items_current') }}
),

order_item_mismatches as (
    select
        batch.order_id as batch_order_id,
        realtime.order_id as realtime_order_id,
        batch.order_item_id as batch_order_item_id,
        realtime.order_item_id as realtime_order_item_id,
        batch.product_id as batch_product_id,
        realtime.product_id as realtime_product_id,
        batch.seller_id as batch_seller_id,
        realtime.seller_id as realtime_seller_id,
        batch.shipping_limit_date as batch_shipping_limit_date,
        realtime.shipping_limit_date as realtime_shipping_limit_date,
        batch.price as batch_price,
        realtime.price as realtime_price,
        batch.freight_value as batch_freight_value,
        realtime.freight_value as realtime_freight_value
    from batch_order_items as batch
    full outer join realtime_order_items as realtime
        on
            batch.order_id = realtime.order_id
            and batch.order_item_id = realtime.order_item_id
),

batch_order_payments as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value::numeric(18, 2) as payment_value
    from {{ ref('stg_olist__order_payments') }}
),

realtime_order_payments as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value::numeric(18, 2) as payment_value
    from {{ ref('stg_cdc__order_payments_current') }}
),

order_payment_mismatches as (
    select
        batch.order_id as batch_order_id,
        realtime.order_id as realtime_order_id,
        batch.payment_sequential as batch_payment_sequential,
        realtime.payment_sequential as realtime_payment_sequential,
        batch.payment_type as batch_payment_type,
        realtime.payment_type as realtime_payment_type,
        batch.payment_installments as batch_payment_installments,
        realtime.payment_installments as realtime_payment_installments,
        batch.payment_value as batch_payment_value,
        realtime.payment_value as realtime_payment_value
    from batch_order_payments as batch
    full outer join realtime_order_payments as realtime
        on
            batch.order_id = realtime.order_id
            and batch.payment_sequential = realtime.payment_sequential
),

batch_order_reviews as (
    select
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date::timestamp as review_creation_date,
        review_answer_timestamp::timestamp as review_answer_timestamp
    from {{ ref('stg_olist__order_reviews') }}
),

realtime_order_reviews as (
    select
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        (review_creation_date at time zone 'UTC')::timestamp
            as review_creation_date,
        (review_answer_timestamp at time zone 'UTC')::timestamp
            as review_answer_timestamp
    from {{ ref('stg_cdc__order_reviews_current') }}
),

order_review_mismatches as (
    select
        batch.review_id as batch_review_id,
        realtime.review_id as realtime_review_id,
        batch.order_id as batch_order_id,
        realtime.order_id as realtime_order_id,
        batch.review_score as batch_review_score,
        realtime.review_score as realtime_review_score,
        batch.review_comment_title as batch_review_comment_title,
        realtime.review_comment_title as realtime_review_comment_title,
        batch.review_comment_message as batch_review_comment_message,
        realtime.review_comment_message as realtime_review_comment_message,
        batch.review_creation_date as batch_review_creation_date,
        realtime.review_creation_date as realtime_review_creation_date,
        batch.review_answer_timestamp as batch_review_answer_timestamp,
        realtime.review_answer_timestamp as realtime_review_answer_timestamp
    from batch_order_reviews as batch
    full outer join realtime_order_reviews as realtime
        on batch.review_id = realtime.review_id
        and batch.order_id = realtime.order_id
),

batch_products as (
    select
        product_id,
        product_category_name,
        product_name_length,
        product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    from {{ ref('stg_olist__products') }}
),

realtime_products as (
    select
        product_id,
        product_category_name,
        product_name_lenght as product_name_length,
        product_description_lenght as product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    from {{ ref('stg_cdc__products_current') }}
),

product_mismatches as (
    select
        batch.product_id as batch_product_id,
        realtime.product_id as realtime_product_id,
        batch.product_category_name as batch_product_category_name,
        realtime.product_category_name as realtime_product_category_name,
        batch.product_name_length as batch_product_name_length,
        realtime.product_name_length as realtime_product_name_length,
        batch.product_description_length as batch_product_description_length,
        realtime.product_description_length
            as realtime_product_description_length,
        batch.product_photos_qty as batch_product_photos_qty,
        realtime.product_photos_qty as realtime_product_photos_qty,
        batch.product_weight_g as batch_product_weight_g,
        realtime.product_weight_g as realtime_product_weight_g,
        batch.product_length_cm as batch_product_length_cm,
        realtime.product_length_cm as realtime_product_length_cm,
        batch.product_height_cm as batch_product_height_cm,
        realtime.product_height_cm as realtime_product_height_cm,
        batch.product_width_cm as batch_product_width_cm,
        realtime.product_width_cm as realtime_product_width_cm
    from batch_products as batch
    full outer join realtime_products as realtime
        on batch.product_id = realtime.product_id
),

batch_sellers as (
    select seller_id, seller_zip_code_prefix, seller_city, seller_state
    from {{ ref('stg_olist__sellers') }}
),

realtime_sellers as (
    select seller_id, seller_zip_code_prefix, seller_city, seller_state
    from {{ ref('stg_cdc__sellers_current') }}
),

seller_mismatches as (
    select
        batch.seller_id as batch_seller_id,
        realtime.seller_id as realtime_seller_id,
        batch.seller_zip_code_prefix as batch_seller_zip_code_prefix,
        realtime.seller_zip_code_prefix as realtime_seller_zip_code_prefix,
        batch.seller_city as batch_seller_city,
        realtime.seller_city as realtime_seller_city,
        batch.seller_state as batch_seller_state,
        realtime.seller_state as realtime_seller_state
    from batch_sellers as batch
    full outer join realtime_sellers as realtime
        on batch.seller_id = realtime.seller_id
),

batch_translations as (
    select product_category_name, product_category_name_english
    from {{ ref('stg_olist__product_category_translation') }}
),

realtime_translations as (
    select product_category_name, product_category_name_english
    from {{ ref('stg_cdc__product_category_translation_current') }}
),

translation_mismatches as (
    select
        batch.product_category_name as batch_product_category_name,
        realtime.product_category_name as realtime_product_category_name,
        batch.product_category_name_english
            as batch_product_category_name_english,
        realtime.product_category_name_english
            as realtime_product_category_name_english
    from batch_translations as batch
    full outer join realtime_translations as realtime
        on batch.product_category_name = realtime.product_category_name
),

fact_mismatches as (
    select
        batch.order_id as batch_order_id,
        realtime.order_id as realtime_order_id,
        batch.order_item_id as batch_order_item_id,
        realtime.order_item_id as realtime_order_item_id,
        batch.customer_id as batch_customer_id,
        realtime.customer_id as realtime_customer_id,
        batch.product_id as batch_product_id,
        realtime.product_id as realtime_product_id,
        batch.seller_id as batch_seller_id,
        realtime.seller_id as realtime_seller_id,
        batch.order_status as batch_order_status,
        realtime.order_status as realtime_order_status,
        batch.order_purchase_timestamp::timestamp
            as batch_order_purchase_timestamp,
        (realtime.order_purchase_timestamp at time zone 'UTC')::timestamp
            as realtime_order_purchase_timestamp,
        batch.price as batch_price,
        realtime.price as realtime_price,
        batch.freight_value as batch_freight_value,
        realtime.freight_value as realtime_freight_value,
        batch.gross_item_amount as batch_gross_item_amount,
        realtime.gross_item_amount as realtime_gross_item_amount,
        batch.allocated_payment_value as batch_allocated_payment_value,
        realtime.allocated_payment_value as realtime_allocated_payment_value
    from {{ ref('fact_order_items') }} as batch
    full outer join {{ ref('fact_order_items_realtime') }} as realtime
        on
            batch.order_id = realtime.order_id
            and batch.order_item_id = realtime.order_item_id
),

metrics as (
    select
        'customers_current_count' as metric_name,
        (select count(*)::decimal from batch_customers) as batch_value,
        (select count(*)::decimal from realtime_customers) as realtime_value,
        0::decimal as tolerance

    union all

    select
        'customers.customer_id' as metric_name,
        0::decimal as batch_value,
        count(*) filter (
            where
                batch_customer_id is null
                or realtime_customer_id is null
                or batch_customer_id is distinct from realtime_customer_id
        )::decimal as realtime_value,
        0::decimal as tolerance
    from customer_mismatches

    union all

    select
        'customers.customer_unique_id' as metric_name,
        0::decimal,
        count(*) filter (
            where
                batch_customer_id is null
                or realtime_customer_id is null
                or batch_customer_unique_id
                is distinct from realtime_customer_unique_id
        )::decimal,
        0::decimal
    from customer_mismatches

    union all

    select
        'customers.customer_zip_code_prefix' as metric_name,
        0::decimal,
        count(*) filter (
            where
                batch_customer_id is null
                or realtime_customer_id is null
                or batch_customer_zip_code_prefix
                is distinct from realtime_customer_zip_code_prefix
        )::decimal,
        0::decimal
    from customer_mismatches

    union all

    select
        'customers.customer_city' as metric_name,
        0::decimal,
        count(*) filter (
            where
                batch_customer_id is null
                or realtime_customer_id is null
                or batch_customer_city is distinct from realtime_customer_city
        )::decimal,
        0::decimal
    from customer_mismatches

    union all

    select
        'customers.customer_state' as metric_name,
        0::decimal,
        count(*) filter (
            where
                batch_customer_id is null
                or realtime_customer_id is null
                or batch_customer_state is distinct from realtime_customer_state
        )::decimal,
        0::decimal
    from customer_mismatches

    union all

    select
        'orders_current_count',
        (select count(*)::decimal from batch_orders),
        (select count(*)::decimal from realtime_orders),
        0::decimal

    union all

    select
        'orders.order_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_id is distinct from realtime_order_id
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.customer_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_customer_id is distinct from realtime_customer_id
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_status',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_status is distinct from realtime_order_status
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_purchase_timestamp',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_purchase_timestamp
                is distinct from realtime_order_purchase_timestamp
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_approved_at',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_approved_at is distinct from realtime_order_approved_at
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_delivered_carrier_date',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_delivered_carrier_date
                is distinct from realtime_order_delivered_carrier_date
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_delivered_customer_date',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_delivered_customer_date
                is distinct from realtime_order_delivered_customer_date
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'orders.order_estimated_delivery_date',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_estimated_delivery_date
                is distinct from realtime_order_estimated_delivery_date
        )::decimal,
        0::decimal
    from order_mismatches

    union all

    select
        'order_items_current_count',
        (select count(*)::decimal from batch_order_items),
        (select count(*)::decimal from realtime_order_items),
        0::decimal

    union all

    select
        'order_items.order_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_id is distinct from realtime_order_id
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.order_item_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_item_id is distinct from realtime_order_item_id
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.product_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_product_id is distinct from realtime_product_id
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.seller_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_seller_id is distinct from realtime_seller_id
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.shipping_limit_date',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_shipping_limit_date
                is distinct from realtime_shipping_limit_date
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.price',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_price is distinct from realtime_price
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_items.freight_value',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_freight_value is distinct from realtime_freight_value
        )::decimal,
        0::decimal
    from order_item_mismatches

    union all

    select
        'order_payments_current_count',
        (select count(*)::decimal from batch_order_payments),
        (select count(*)::decimal from realtime_order_payments),
        0::decimal

    union all

    select
        'order_payments.order_id',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_id is distinct from realtime_order_id
        )::decimal,
        0::decimal
    from order_payment_mismatches

    union all

    select
        'order_payments.payment_sequential',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_payment_sequential
                is distinct from realtime_payment_sequential
        )::decimal,
        0::decimal
    from order_payment_mismatches

    union all

    select
        'order_payments.payment_type',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_payment_type is distinct from realtime_payment_type
        )::decimal,
        0::decimal
    from order_payment_mismatches

    union all

    select
        'order_payments.payment_installments',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_payment_installments
                is distinct from realtime_payment_installments
        )::decimal,
        0::decimal
    from order_payment_mismatches

    union all

    select
        'order_payments.payment_value',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_payment_value is distinct from realtime_payment_value
        )::decimal,
        0::decimal
    from order_payment_mismatches

    union all

    select
        'order_reviews_current_count',
        (select count(*)::decimal from batch_order_reviews),
        (select count(*)::decimal from realtime_order_reviews),
        0::decimal

    union all

    select
        'order_reviews.review_id',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_id is distinct from realtime_review_id
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.order_id',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_order_id is distinct from realtime_order_id
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.review_score',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_score is distinct from realtime_review_score
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.review_comment_title',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_comment_title
                is distinct from realtime_review_comment_title
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.review_comment_message',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_comment_message
                is distinct from realtime_review_comment_message
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.review_creation_date',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_creation_date
                is distinct from realtime_review_creation_date
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'order_reviews.review_answer_timestamp',
        0::decimal,
        count(*) filter (
            where
                batch_review_id is null
                or realtime_review_id is null
                or batch_review_answer_timestamp
                is distinct from realtime_review_answer_timestamp
        )::decimal,
        0::decimal
    from order_review_mismatches

    union all

    select
        'products_current_count',
        (select count(*)::decimal from batch_products),
        (select count(*)::decimal from realtime_products),
        0::decimal

    union all

    select
        'products.product_id',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_id is distinct from realtime_product_id
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_category_name',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_category_name
                is distinct from realtime_product_category_name
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_name_length',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_name_length
                is distinct from realtime_product_name_length
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_description_length',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_description_length
                is distinct from realtime_product_description_length
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_photos_qty',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_photos_qty
                is distinct from realtime_product_photos_qty
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_weight_g',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_weight_g is distinct from realtime_product_weight_g
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_length_cm',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_length_cm is distinct from realtime_product_length_cm
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_height_cm',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_height_cm
                is distinct from realtime_product_height_cm
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'products.product_width_cm',
        0::decimal,
        count(*) filter (
            where
                batch_product_id is null
                or realtime_product_id is null
                or batch_product_width_cm is distinct from realtime_product_width_cm
        )::decimal,
        0::decimal
    from product_mismatches

    union all

    select
        'sellers_current_count',
        (select count(*)::decimal from batch_sellers),
        (select count(*)::decimal from realtime_sellers),
        0::decimal

    union all

    select
        'sellers.seller_id',
        0::decimal,
        count(*) filter (
            where
                batch_seller_id is null
                or realtime_seller_id is null
                or batch_seller_id is distinct from realtime_seller_id
        )::decimal,
        0::decimal
    from seller_mismatches

    union all

    select
        'sellers.seller_zip_code_prefix',
        0::decimal,
        count(*) filter (
            where
                batch_seller_id is null
                or realtime_seller_id is null
                or batch_seller_zip_code_prefix
                is distinct from realtime_seller_zip_code_prefix
        )::decimal,
        0::decimal
    from seller_mismatches

    union all

    select
        'sellers.seller_city',
        0::decimal,
        count(*) filter (
            where
                batch_seller_id is null
                or realtime_seller_id is null
                or batch_seller_city is distinct from realtime_seller_city
        )::decimal,
        0::decimal
    from seller_mismatches

    union all

    select
        'sellers.seller_state',
        0::decimal,
        count(*) filter (
            where
                batch_seller_id is null
                or realtime_seller_id is null
                or batch_seller_state is distinct from realtime_seller_state
        )::decimal,
        0::decimal
    from seller_mismatches

    union all

    select
        'product_category_translation_current_count',
        (select count(*)::decimal from batch_translations),
        (select count(*)::decimal from realtime_translations),
        0::decimal

    union all

    select
        'product_category_translation.product_category_name',
        0::decimal,
        count(*) filter (
            where
                batch_product_category_name is null
                or realtime_product_category_name is null
                or batch_product_category_name
                is distinct from realtime_product_category_name
        )::decimal,
        0::decimal
    from translation_mismatches

    union all

    select
        'product_category_translation.product_category_name_english',
        0::decimal,
        count(*) filter (
            where
                batch_product_category_name is null
                or realtime_product_category_name is null
                or batch_product_category_name_english
                is distinct from realtime_product_category_name_english
        )::decimal,
        0::decimal
    from translation_mismatches

    union all

    select
        'fact_order_item_count',
        (select count(*)::decimal from {{ ref('fact_order_items') }}),
        (select count(*)::decimal from {{ ref('fact_order_items_realtime') }}),
        0::decimal

    union all

    select
        'fact_order_items_business_mismatches',
        0::decimal,
        count(*) filter (
            where
                batch_order_id is null
                or realtime_order_id is null
                or batch_order_id is distinct from realtime_order_id
                or batch_order_item_id is distinct from realtime_order_item_id
                or batch_customer_id is distinct from realtime_customer_id
                or batch_product_id is distinct from realtime_product_id
                or batch_seller_id is distinct from realtime_seller_id
                or batch_order_status is distinct from realtime_order_status
                or batch_order_purchase_timestamp
                is distinct from realtime_order_purchase_timestamp
                or batch_price is distinct from realtime_price
                or batch_freight_value is distinct from realtime_freight_value
                or batch_gross_item_amount
                is distinct from realtime_gross_item_amount
                or batch_allocated_payment_value
                is distinct from realtime_allocated_payment_value
        )::decimal,
        0::decimal
    from fact_mismatches

    union all

    select
        'fact_allocated_payment_total',
        (
            select coalesce(sum(allocated_payment_value), 0)
            from {{ ref('fact_order_items') }}
        ),
        (
            select coalesce(sum(allocated_payment_value), 0)
            from {{ ref('fact_order_items_realtime') }}
        ),
        0.01::decimal

    union all

    select
        'daily_gross_revenue_total',
        (
            select coalesce(sum(gross_revenue), 0)
            from {{ ref('mart_daily_revenue') }}
        ),
        (
            select coalesce(sum(gross_revenue), 0)
            from {{ ref('mart_daily_revenue_realtime') }}
        ),
        0.01::decimal

    union all

    select
        'monthly_revenue_total',
        (
            select coalesce(sum(total_revenue), 0)
            from {{ ref('mart_monthly_arpu') }}
        ),
        (
            select coalesce(sum(total_revenue), 0)
            from {{ ref('mart_monthly_arpu_realtime') }}
        ),
        0.01::decimal
)

select
    metric_name,
    batch_value,
    realtime_value,
    realtime_value - batch_value as difference,
    tolerance,
    case
        when abs(realtime_value - batch_value) <= tolerance then 'PASS'
        else 'FAIL'
    end as status
from metrics
