{{
    config(
        materialized='table',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

with ordered as (
    select
        {{ hash_key(
            "events.customer_unique_id || '|' || "
            ~ cast_string('events._source_lsn')
            ~ " || '|' || "
            ~ cast_string('coalesce(events._tx_order, 0)')
            ~ " || '|' || "
            ~ cast_string('events._partition')
            ~ " || '|' || "
            ~ cast_string('events._offset')
        ) }} as customer_key,
        events.customer_id as customer_id,
        events.customer_unique_id as customer_unique_id,
        events.customer_zip_code_prefix as customer_zip_code_prefix,
        events.customer_city as customer_city,
        events.customer_state as customer_state,
        events._source_ts as valid_from,
        lead(events._source_ts) over (
            partition by events.customer_unique_id
            order by {{ cdc_order_by('events') }}
        ) as valid_to,
        {{ bool_value(
            'row_number() over (partition by events.customer_unique_id order by '
            ~ cdc_order_by('events', 'desc')
            ~ ') = 1'
        ) }} as is_current,
        {{ bool_value("events._op = 'd'") }} as is_deleted,
        events._source_lsn as _source_lsn,
        events._tx_order as _tx_order,
        events._partition as _partition,
        events._offset as _offset
    from {{ ref('stg_cdc__customers_events') }} as events
)

select * from ordered
