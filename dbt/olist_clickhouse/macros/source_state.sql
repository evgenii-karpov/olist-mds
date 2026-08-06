{% macro current_order_tuple(alias) -%}
    tuple(
        if({{ alias }}last_is_snapshot, 0, 1),
        coalesce({{ alias }}last_source_binlog_file_index, -1),
        coalesce({{ alias }}last_source_binlog_pos, -1),
        coalesce({{ alias }}last_source_row, -1),
        coalesce(toInt64({{ alias }}last_transaction_total_order), -1),
        coalesce(toInt64({{ alias }}last_transaction_data_collection_order), -1),
        {{ alias }}last_source_ts,
        {{ alias }}kafka_partition,
        {{ alias }}kafka_offset,
        {{ alias }}last_event_id,
        {{ alias }}sync_run_seq
    )
{%- endmacro %}

{% macro current_state(source_table, primary_key) -%}
WITH ranked_versions AS
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY
            {%- for column in primary_key %}
                {{ column }}{% if not loop.last %}, {% endif %}
            {%- endfor %}
            ORDER BY {{ current_order_tuple('') }} DESC
        ) AS _version_rank
    FROM {{ source('serving_cdc', source_table) }}
    WHERE
        sync_run_seq = {{ sync_run_seq_sql() }}
        OR sync_run_seq IN
        (
            SELECT sync_run_seq
            FROM {{ source('serving_control', 'published_runs_current') }}
            WHERE publication_status = 'PUBLISHED'
        )
)
SELECT * EXCEPT (_version_rank)
FROM ranked_versions
WHERE _version_rank = 1 AND NOT is_deleted
{%- endmacro %}

{% macro applied_events(source_table) -%}
SELECT *
FROM {{ source('serving_cdc', source_table) }}
WHERE
    (
        sync_run_seq = {{ sync_run_seq_sql() }}
        OR sync_run_seq IN
        (
            SELECT sync_run_seq
            FROM {{ source('serving_control', 'published_runs_current') }}
            WHERE publication_status = 'PUBLISHED'
        )
    )
    AND lower(apply_status) = 'applied'
{%- endmacro %}

{% macro event_order_tuple(alias) -%}
    {%- set prefix = alias ~ '.' if alias else '' -%}
    tuple(
        if({{ prefix }}is_snapshot, 0, 1),
        coalesce({{ prefix }}source_binlog_file_index, -1),
        coalesce({{ prefix }}source_binlog_pos, -1),
        coalesce({{ prefix }}source_row, -1),
        coalesce(toInt64({{ prefix }}transaction_total_order), -1),
        coalesce(toInt64({{ prefix }}transaction_data_collection_order), -1),
        {{ prefix }}source_ts,
        {{ prefix }}kafka_partition,
        {{ prefix }}kafka_offset,
        {{ prefix }}event_id
    )
{%- endmacro %}

{% macro scd_valid_from(alias) -%}
    if(
        {{ alias }}.is_snapshot
            OR {{ alias }}.source_ts = min({{ alias }}.source_ts) OVER (
                PARTITION BY {{ alias }}.customer_unique_id
            ),
        toDateTime64('1900-01-01 00:00:00', 6, 'UTC'),
        {{ alias }}.source_ts
    )
{%- endmacro %}
