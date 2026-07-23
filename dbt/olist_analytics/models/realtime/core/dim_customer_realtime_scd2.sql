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
        {{ output_column('events.customer_id', 'customer_id') }},
        {{
            output_column(
                'events.customer_unique_id',
                'customer_unique_id'
            )
        }},
        {{
            output_column(
                'events.customer_zip_code_prefix',
                'customer_zip_code_prefix'
            )
        }},
        {{ output_column('events.customer_city', 'customer_city') }},
        {{ output_column('events.customer_state', 'customer_state') }},
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
        {{ output_column('events._source_lsn', '_source_lsn') }},
        {{ output_column('events._tx_order', '_tx_order') }},
        {{ output_column('events._partition', '_partition') }},
        {{ output_column('events._offset', '_offset') }}
    from {{ ref('stg_cdc__customers_events') }} as events
)

select * from ordered
