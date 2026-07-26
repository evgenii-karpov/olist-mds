{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

with

entity_counts as (
    select
        'customers_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__customers') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__customers_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'orders_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__orders') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__orders_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'order_items_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__order_items') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__order_items_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'order_payments_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_olist__order_payments')
                ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__order_payments_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'order_reviews_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__order_reviews') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__order_reviews_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'products_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__products') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__products_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'sellers_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('stg_olist__sellers') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__sellers_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'product_category_translation_current_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_olist__product_category_translation')
                ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('stg_cdc__product_category_translation_current')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance
),

fact_business_mismatches as (
    select
        {{ count_where(
            'batch.order_id is null'
            ~ ' or realtime.order_id is null'
            ~ ' or ' ~ is_distinct('batch.customer_id', 'realtime.customer_id')
            ~ ' or ' ~ is_distinct('batch.product_id', 'realtime.product_id')
            ~ ' or ' ~ is_distinct('batch.seller_id', 'realtime.seller_id')
            ~ ' or ' ~ is_distinct('batch.order_status', 'realtime.order_status')
            ~ ' or ' ~ is_distinct(
                utc_timestamp('batch.order_purchase_timestamp'),
                utc_timestamp('realtime.order_purchase_timestamp')
            )
            ~ ' or ' ~ is_distinct('batch.price', 'realtime.price')
            ~ ' or ' ~ is_distinct('batch.freight_value', 'realtime.freight_value')
            ~ ' or ' ~ is_distinct(
                'batch.gross_item_amount',
                'realtime.gross_item_amount'
            )
            ~ ' or ' ~ is_distinct(
                'batch.allocated_payment_value',
                'realtime.allocated_payment_value'
            )
        ) }} as mismatch_count
    from {{ ref('fact_order_items') }} as batch
    full outer join {{ ref('fact_order_items_realtime') }} as realtime
        on
            batch.order_id = realtime.order_id
            and batch.order_item_id = realtime.order_item_id
),

business_metrics as (
    select
        'fact_order_items_business_mismatches' as metric_name,
        {{ decimal_zero() }} as batch_value,
        {{ cast_decimal('mismatch_count', 18, 2) }} as realtime_value,
        {{ decimal_zero() }} as tolerance
    from fact_business_mismatches

    union all

    select
        'fact_order_item_count' as metric_name,
        {{
            cast_decimal(
                '(select count(*) from ' ~ ref('fact_order_items') ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select count(*) from '
                ~ ref('fact_order_items_realtime')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_zero() }} as tolerance

    union all

    select
        'fact_allocated_payment_total' as metric_name,
        {{
            cast_decimal(
                '(select coalesce(sum(allocated_payment_value), 0) from '
                ~ ref('fact_order_items')
                ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select coalesce(sum(allocated_payment_value), 0) from '
                ~ ref('fact_order_items_realtime')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_literal('0.01') }} as tolerance

    union all

    select
        'daily_gross_revenue_total' as metric_name,
        {{
            cast_decimal(
                '(select coalesce(sum(gross_revenue), 0) from '
                ~ ref('mart_daily_revenue')
                ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select coalesce(sum(gross_revenue), 0) from '
                ~ ref('mart_daily_revenue_realtime')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_literal('0.01') }} as tolerance

    union all

    select
        'monthly_revenue_total' as metric_name,
        {{
            cast_decimal(
                '(select coalesce(sum(total_revenue), 0) from '
                ~ ref('mart_monthly_arpu')
                ~ ')',
                18,
                2
            )
        }} as batch_value,
        {{
            cast_decimal(
                '(select coalesce(sum(total_revenue), 0) from '
                ~ ref('mart_monthly_arpu_realtime')
                ~ ')',
                18,
                2
            )
        }} as realtime_value,
        {{ decimal_literal('0.01') }} as tolerance
),

metrics as (
    select * from entity_counts
    union all
    select * from business_metrics
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
