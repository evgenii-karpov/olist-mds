{% macro cleanup_gold_partitions(keep_published=2, dry_run=true) -%}
    {%- if keep_published | int < 2 -%}
        {{ exceptions.raise_compiler_error(
            'Gold cleanup must retain at least the current and previous published runs'
        ) }}
    {%- endif -%}

    {%- if not execute -%}
        {{ return('') }}
    {%- endif -%}

    {%- set published_query -%}
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
        ORDER BY sync_run_seq DESC
        LIMIT {{ keep_published | int }}
    {%- endset -%}
    {%- set published_result = run_query(published_query) -%}
    {%- set keep_sequences = published_result.columns[0].values() | list -%}

    {%- if keep_sequences | length < 2 -%}
        {{ exceptions.raise_compiler_error(
            'Gold cleanup refuses to run before two published sequences exist'
        ) }}
    {%- endif -%}

    {%- set model_names = [
        'dim_date',
        'dim_order_status',
        'dim_seller',
        'dim_customer_scd2',
        'dim_product_scd2',
        'fact_order_items',
        'mart_daily_revenue',
        'mart_monthly_arpu'
    ] -%}

    {%- for model_name in model_names -%}
        {%- set relation = adapter.get_relation(
            database=target.database,
            schema='gold_store',
            identifier=model_name
        ) -%}
        {%- if relation is not none -%}
            {%- set partition_query -%}
                SELECT DISTINCT sync_run_seq
                FROM {{ relation }}
                WHERE sync_run_seq NOT IN (
                    {{ keep_sequences | join(', ') }}
                )
                ORDER BY sync_run_seq
            {%- endset -%}
            {%- set partition_result = run_query(partition_query) -%}
            {%- for sequence in partition_result.columns[0].values() -%}
                {%- set drop_statement -%}
                    ALTER TABLE {{ relation }} DROP PARTITION {{ sequence | int }}
                {%- endset -%}
                {%- if dry_run -%}
                    {{ log('[dry-run] ' ~ drop_statement | trim, info=true) }}
                {%- else -%}
                    {% do run_query(drop_statement) %}
                    {{ log('Dropped ' ~ model_name ~ ' partition ' ~ sequence, info=true) }}
                {%- endif -%}
            {%- endfor -%}
        {%- endif -%}
    {%- endfor -%}
{%- endmacro %}
