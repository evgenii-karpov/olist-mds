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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
    AND apply_status = 'applied'
{%- endmacro %}

{% macro event_order_tuple(alias) -%}
    tuple(
        {{ alias }}.source_ts,
        {{ alias }}.kafka_topic,
        {{ alias }}.kafka_partition,
        {{ alias }}.kafka_offset
    )
{%- endmacro %}

{% macro scd_valid_from(alias) -%}
    if(
        {{ alias }}.is_snapshot,
        toDateTime64('1900-01-01 00:00:00', 6, 'UTC'),
        {{ alias }}.source_ts
    )
{%- endmacro %}
