{{
    config(
        materialized='incremental',
        unique_key='customer_key',
        incremental_strategy='merge',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

with ordered as (
    select
        md5(
            events.customer_unique_id
            || '|'
            || events._source_lsn::varchar
            || '|'
            || coalesce(events._tx_order, 0)::varchar
            || '|'
            || events._partition::varchar
            || '|' || events._offset::varchar
        ) as customer_key,
        events.customer_id,
        events.customer_unique_id,
        events.customer_zip_code_prefix,
        events.customer_city,
        events.customer_state,
        events._source_ts as valid_from,
        lead(events._source_ts) over (
            partition by events.customer_unique_id
            order by {{ cdc_order_by('events') }}
        ) as valid_to,
        row_number() over (
            partition by events.customer_unique_id
            order by {{ cdc_order_by('events', 'desc') }}
        ) = 1 as is_current,
        events._op = 'd' as is_deleted,
        events._source_lsn,
        events._tx_order,
        events._partition,
        events._offset
    from {{ ref('stg_cdc__customers_events') }} as events
)

select * from ordered
