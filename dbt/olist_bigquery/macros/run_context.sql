{% macro require_run_context() -%}
    {%- set run_seq = var('sync_run_seq', 0) | int -%}
    {%- set run_id = var('sync_run_id', '') | string | trim -%}
    {%- set mode = var('build_mode', 'initial') | string | trim -%}
    {%- if execute and run_seq <= 0 -%}
        {{ exceptions.raise_compiler_error('sync_run_seq must be a positive integer') }}
    {%- endif -%}
    {%- if execute and run_id == '' -%}
        {{ exceptions.raise_compiler_error('sync_run_id must be non-empty') }}
    {%- endif -%}
    {%- if execute and mode not in ['initial', 'incremental'] -%}
        {{ exceptions.raise_compiler_error('build_mode must be initial or incremental') }}
    {%- endif -%}
{%- endmacro %}

{% macro sync_run_seq_sql() -%}
    CAST({{ var('sync_run_seq', 0) | int }} AS INT64)
{%- endmacro %}

{% macro sync_run_id_sql() -%}
    CAST('{{ (var('sync_run_id', '') | string).replace("'", "''") }}' AS STRING)
{%- endmacro %}

{% macro target_sql() -%}
    CAST('{{ (var('target', 'gcp') | string).replace("'", "''") }}' AS STRING)
{%- endmacro %}

{% macro candidate_columns() -%}
    {{ sync_run_seq_sql() }} AS sync_run_seq,
    {{ sync_run_id_sql() }} AS sync_run_id
{%- endmacro %}

{% macro history_columns(operation_expression) -%}
    {{ sync_run_seq_sql() }} AS sync_run_seq,
    {{ sync_run_id_sql() }} AS sync_run_id,
    {{ operation_expression }} AS operation_type,
    CAST('{{ (var('build_mode', 'initial') | string).replace("'", "''") }}' AS STRING)
        AS build_mode,
    CAST('{{ (var('previous_boundary_id', '') | string).replace("'", "''") }}' AS STRING)
        AS previous_boundary_id,
    CAST('{{ (var('current_boundary_id', '') | string).replace("'", "''") }}' AS STRING)
        AS current_boundary_id,
    CURRENT_TIMESTAMP() AS built_at
{%- endmacro %}

{% macro delete_same_run_history(relation) -%}
    {%- if execute and is_incremental() -%}
        DELETE FROM {{ relation }}
        WHERE sync_run_seq = {{ sync_run_seq_sql() }}
    {%- endif -%}
{%- endmacro %}
