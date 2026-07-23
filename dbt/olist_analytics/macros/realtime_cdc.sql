{% macro cdc_order_by(alias, direction='') -%}
    {{ alias }}._source_lsn {{ direction }},
    coalesce({{ alias }}._tx_order, 0) {{ direction }},
    {{ alias }}._partition {{ direction }},
    {{ alias }}._offset {{ direction }}
{%- endmacro %}

{% macro cdc_key_match(left_alias, right_alias, key_columns) -%}
    {% for key in key_columns -%}
        {{ left_alias }}.{{ key }} = {{ right_alias }}.{{ key }}
        {%- if not loop.last %} and {% endif -%}
    {%- endfor %}
{%- endmacro %}

{% macro cdc_current_model(events_model, key_columns) -%}
    with events as (
        select * from {{ ref(events_model) }}
    )

    select current_event.*
    from events as current_event
    where
        current_event._op <> 'd'
        and not exists (
            select 1
            from events as newer_event
            where
                {{ cdc_key_match('newer_event', 'current_event', key_columns) }}
                and (
                    {{ cdc_order_by('newer_event') }}
                ) > (
                    {{ cdc_order_by('current_event') }}
                )
        )
{%- endmacro %}

{% macro cdc_history_model(events_model, key_columns) -%}
    with ordered as (
        select
            events.*,
            lead(_source_ts) over (
                partition by
                    {% for key in key_columns -%}
                        {{ key }}{% if not loop.last %}, {% endif %}
                    {%- endfor %}
                order by {{ cdc_order_by('events') }}
            ) as valid_to,
            row_number() over (
                partition by
                    {% for key in key_columns -%}
                        {{ key }}{% if not loop.last %}, {% endif %}
                    {%- endfor %}
                order by {{ cdc_order_by('events', 'desc') }}
            ) as reverse_row_number
        from {{ ref(events_model) }} as events
    )

    select
        ordered.*,
        _source_ts as valid_from,
        reverse_row_number = 1 as is_current,
        _op = 'd' as is_deleted
    from ordered
{%- endmacro %}

{% macro cdc_selected_file_predicate(alias='') -%}
    {{ return(adapter.dispatch('cdc_selected_file_predicate', 'olist_analytics')(alias)) }}
{%- endmacro %}

{% macro default__cdc_selected_file_predicate(alias='') -%}
    {% set transform_run_id = var('cdc_transform_run_id', '') %}
    {% if transform_run_id %}
        exists (
            select 1
            from {{ source('cdc_audit', 'cdc_transform_run_files') }} as run_files
            inner join {{ source('cdc_audit', 'cdc_files') }} as files
                on run_files.manifest_uri = files.manifest_uri
            where
                run_files.transform_run_id = '{{ transform_run_id | replace("'", "''") }}'
                and files.object_uri = {% if alias %}{{ alias }}.{% endif %}_source_object_uri
        )
    {% else %}
        true
    {% endif %}
{%- endmacro %}

{% macro clickhouse__cdc_selected_file_predicate(alias='') -%}
    {% set transform_run_id = var('cdc_transform_run_id', '') %}
    {% if transform_run_id %}
        exists (
            select 1
            from {{ source('pipeline_runtime', 'cdc_transform_run_files') }} as run_files
            where
                run_files.transform_run_id = '{{ transform_run_id | replace("'", "''") }}'
                and run_files.object_uri = {% if alias %}{{ alias }}.{% endif %}_source_object_uri
        )
    {% else %}
        true
    {% endif %}
{%- endmacro %}

{% macro delete_impacted_periods(date_column, changed_period_model, period_column) -%}
    {% if is_incremental() %}
        delete from {{ this }}
        where {{ date_column }} in (
            select {{ period_column }} from {{ ref(changed_period_model) }}
        )
    {% else %}
        select 1
    {% endif %}
{%- endmacro %}

{% macro delete_impacted_orders(order_id_column='order_id') -%}
    {% if is_incremental() %}
        delete from {{ this }}
        where {{ order_id_column }} in (
            select order_id from {{ ref('int_cdc__changed_order_ids') }}
        )
    {% else %}
        select 1
    {% endif %}
{%- endmacro %}
