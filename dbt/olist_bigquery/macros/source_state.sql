{% macro event_order(alias='') -%}
    {%- set prefix = alias ~ '.' if alias else '' -%}
    IF({{ prefix }}is_snapshot, 0, 1) DESC,
    COALESCE({{ prefix }}source_binlog_file_index, -1) DESC,
    COALESCE({{ prefix }}source_binlog_pos, -1) DESC,
    COALESCE({{ prefix }}source_row, -1) DESC,
    COALESCE({{ prefix }}transaction_total_order, -1) DESC,
    COALESCE({{ prefix }}transaction_data_collection_order, -1) DESC,
    {{ prefix }}source_ts DESC,
    {{ prefix }}kafka_partition DESC,
    {{ prefix }}kafka_offset DESC,
    {{ prefix }}event_id DESC
{%- endmacro %}

{% macro bounded_changes(source_name) -%}
SELECT changes.*
FROM {{ source('lakehouse_bridge', source_name) }} AS changes
INNER JOIN {{ source('serving_control', 'boundary_offsets') }} AS boundary
    ON boundary.target = {{ target_sql() }}
    AND boundary.sync_run_seq = {{ sync_run_seq_sql() }}
    AND boundary.topic = changes.kafka_topic
    AND boundary.partition_id = changes.kafka_partition
WHERE changes.kafka_offset > COALESCE(boundary.previous_offset, -1)
    AND changes.kafka_offset <= boundary.target_offset
    AND LOWER(changes.apply_status) = 'applied'
{%- endmacro %}

{% macro latest_changes(model_name, key_columns) -%}
WITH ranked AS
(
    SELECT
        changes.*,
        ROW_NUMBER() OVER (
            PARTITION BY
                {% for column in key_columns %}
                changes.{{ column }}{% if not loop.last %}, {% endif %}
                {% endfor %}
            ORDER BY {{ event_order('changes') }}
        ) AS _version_rank
    FROM {{ ref(model_name) }} AS changes
)
SELECT * EXCEPT (_version_rank)
FROM ranked
WHERE _version_rank = 1
{%- endmacro %}
