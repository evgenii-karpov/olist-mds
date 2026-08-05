{% macro require_run_context() -%}
    {%- set run_seq = var('sync_run_seq', 0) | int -%}
    {%- set run_id = var('sync_run_id', '') | string | trim -%}
    {%- if run_seq <= 0 -%}
        {{ exceptions.raise_compiler_error('sync_run_seq must be a positive integer') }}
    {%- endif -%}
    {%- if run_id == '' -%}
        {{ exceptions.raise_compiler_error('sync_run_id must be non-empty') }}
    {%- endif -%}
{%- endmacro %}

{% macro sync_run_seq_sql() -%}
    toUInt64({{ var('sync_run_seq') | int }})
{%- endmacro %}

{% macro sync_run_id_sql() -%}
    '{{ (var('sync_run_id') | string).replace("'", "''") }}'
{%- endmacro %}

{% macro candidate_run_columns() -%}
    {{ sync_run_seq_sql() }} AS sync_run_seq,
    {{ sync_run_id_sql() }} AS sync_run_id
{%- endmacro %}

{% macro create_or_replace_gold_view() -%}
    CREATE OR REPLACE VIEW gold.{{ this.identifier }} AS
    SELECT
    {%- if this.identifier == 'mart_daily_revenue' %}
        order_purchase_date,
        gross_revenue,
        allocated_payment_revenue,
        product_revenue,
        freight_revenue,
        orders_count,
        customers_count,
        items_count,
        average_order_value,
        average_paid_order_value,
        average_delivery_days,
        late_deliveries_count
    {%- elif this.identifier == 'mart_monthly_arpu' %}
        order_month,
        active_customers,
        total_revenue,
        arpu,
        orders_count,
        orders_per_customer,
        average_order_value,
        repeat_customer_rate
    {%- else %}
        * EXCEPT (sync_run_seq, sync_run_id)
    {%- endif %}
    FROM {{ this }}
    WHERE sync_run_seq =
    (
        SELECT coalesce(max(sync_run_seq), toUInt64(0))
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
{%- endmacro %}
