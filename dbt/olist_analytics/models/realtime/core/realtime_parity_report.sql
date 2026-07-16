{{ config(materialized='view', schema='cdc_audit', tags=['realtime_parity']) }}

with customer_mismatches as (
    select count(*)::decimal as mismatch_count
    from {{ ref('stg_olist__customers') }} as batch
    full outer join {{ ref('stg_cdc__customers_current') }} as realtime
        on batch.customer_id = realtime.customer_id
    where
        batch.customer_id is null
        or realtime.customer_id is null
        or batch.customer_unique_id <> realtime.customer_unique_id
        or batch.customer_zip_code_prefix <> realtime.customer_zip_code_prefix
        or batch.customer_city <> realtime.customer_city
        or batch.customer_state <> realtime.customer_state
),

product_mismatches as (
    select count(*)::decimal as mismatch_count
    from {{ ref('stg_olist__products') }} as batch
    full outer join {{ ref('stg_cdc__products_current') }} as realtime
        on batch.product_id = realtime.product_id
    where
        batch.product_id is null
        or realtime.product_id is null
        or batch.product_category_name
        is distinct from realtime.product_category_name
        or batch.product_weight_g is distinct from realtime.product_weight_g
        or batch.product_length_cm is distinct from realtime.product_length_cm
        or batch.product_height_cm is distinct from realtime.product_height_cm
        or batch.product_width_cm is distinct from realtime.product_width_cm
),

metrics as (
    select
        'customers_current_count' as metric_name,
        (select count(*)::decimal from {{ ref('stg_olist__customers') }})
            as batch_value,
        (select count(*)::decimal from {{ ref('stg_cdc__customers_current') }})
            as realtime_value,
        0::decimal as tolerance

    union all

    select
        'customer_attribute_mismatches' as metric_name,
        0::decimal as batch_value,
        customer_mismatches.mismatch_count as realtime_value,
        0::decimal as tolerance
    from customer_mismatches

    union all

    select
        'product_attribute_mismatches' as metric_name,
        0::decimal as batch_value,
        product_mismatches.mismatch_count as realtime_value,
        0::decimal as tolerance
    from product_mismatches

    union all

    select
        'products_current_count' as metric_name,
        (select count(*)::decimal from {{ ref('stg_olist__products') }})
            as batch_value,
        (select count(*)::decimal from {{ ref('stg_cdc__products_current') }})
            as realtime_value,
        0::decimal as tolerance

    union all

    select
        'fact_order_item_count' as metric_name,
        (select count(*)::decimal from {{ ref('fact_order_items') }})
            as batch_value,
        (select count(*)::decimal from {{ ref('fact_order_items_realtime') }})
            as realtime_value,
        0::decimal as tolerance

    union all

    select
        'fact_allocated_payment_total' as metric_name,
        (
            select coalesce(sum(allocated_payment_value), 0)
            from {{ ref('fact_order_items') }}
        ) as batch_value,
        (
            select coalesce(sum(allocated_payment_value), 0)
            from {{ ref('fact_order_items_realtime') }}
        ) as realtime_value,
        0.01::decimal as tolerance

    union all

    select
        'daily_gross_revenue_total' as metric_name,
        (
            select coalesce(sum(gross_revenue), 0)
            from {{ ref('mart_daily_revenue') }}
        ) as batch_value,
        (
            select coalesce(sum(gross_revenue), 0)
            from {{ ref('mart_daily_revenue_realtime') }}
        ) as realtime_value,
        0.01::decimal as tolerance

    union all

    select
        'monthly_revenue_total' as metric_name,
        (
            select coalesce(sum(total_revenue), 0)
            from {{ ref('mart_monthly_arpu') }}
        ) as batch_value,
        (
            select coalesce(sum(total_revenue), 0)
            from {{ ref('mart_monthly_arpu_realtime') }}
        ) as realtime_value,
        0.01::decimal as tolerance
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
