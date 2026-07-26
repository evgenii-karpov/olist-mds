{% macro cast_string(expression, length=None) -%}
    {{ return(adapter.dispatch('cast_string', 'olist_analytics')(expression, length)) }}
{%- endmacro %}

{% macro default__cast_string(expression, length=None) -%}
    cast({{ expression }} as varchar{% if length is not none %}({{ length }}){% endif %})
{%- endmacro %}

{% macro clickhouse__cast_string(expression, length=None) -%}
    cast({{ expression }} as String)
{%- endmacro %}

{% macro cast_int(expression) -%}
    {{ return(adapter.dispatch('cast_int', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__cast_int(expression) -%}
    cast({{ expression }} as integer)
{%- endmacro %}

{% macro clickhouse__cast_int(expression) -%}
    cast({{ expression }} as Int32)
{%- endmacro %}

{% macro cast_bigint(expression) -%}
    {{ return(adapter.dispatch('cast_bigint', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__cast_bigint(expression) -%}
    cast({{ expression }} as bigint)
{%- endmacro %}

{% macro clickhouse__cast_bigint(expression) -%}
    cast({{ expression }} as Int64)
{%- endmacro %}

{% macro cast_decimal(expression, precision=18, scale=2) -%}
    {{ return(adapter.dispatch('cast_decimal', 'olist_analytics')(expression, precision, scale)) }}
{%- endmacro %}

{% macro default__cast_decimal(expression, precision=18, scale=2) -%}
    cast({{ expression }} as decimal({{ precision }}, {{ scale }}))
{%- endmacro %}

{% macro clickhouse__cast_decimal(expression, precision=18, scale=2) -%}
    cast({{ expression }} as Decimal({{ precision }}, {{ scale }}))
{%- endmacro %}

{% macro cast_timestamp(expression) -%}
    {{ return(adapter.dispatch('cast_timestamp', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__cast_timestamp(expression) -%}
    cast({{ expression }} as timestamp)
{%- endmacro %}

{% macro clickhouse__cast_timestamp(expression) -%}
    cast({{ expression }} as DateTime64(6, 'UTC'))
{%- endmacro %}

{% macro cast_date(expression) -%}
    {{ return(adapter.dispatch('cast_date', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__cast_date(expression) -%}
    cast({{ expression }} as date)
{%- endmacro %}

{% macro clickhouse__cast_date(expression) -%}
    toDate({{ expression }})
{%- endmacro %}

{% macro null_timestamp() -%}
    {{ return(adapter.dispatch('null_timestamp', 'olist_analytics')()) }}
{%- endmacro %}

{% macro default__null_timestamp() -%}
    cast(null as timestamp)
{%- endmacro %}

{% macro clickhouse__null_timestamp() -%}
    cast(null, 'Nullable(DateTime64(6, ''UTC''))')
{%- endmacro %}

{% macro null_string(length=None) -%}
    {{ return(adapter.dispatch('null_string', 'olist_analytics')(length)) }}
{%- endmacro %}

{% macro default__null_string(length=None) -%}
    cast(null as varchar{% if length is not none %}({{ length }}){% endif %})
{%- endmacro %}

{% macro clickhouse__null_string(length=None) -%}
    cast(null, 'Nullable(String)')
{%- endmacro %}

{% macro timestamp_literal(value) -%}
    {{ return(adapter.dispatch('timestamp_literal', 'olist_analytics')(value)) }}
{%- endmacro %}

{% macro default__timestamp_literal(value) -%}
    cast('{{ value }}' as timestamp)
{%- endmacro %}

{% macro clickhouse__timestamp_literal(value) -%}
    toDateTime64('{{ value }} 00:00:00', 6, 'UTC')
{%- endmacro %}

{% macro max_valid_timestamp() -%}
    {{ return(adapter.dispatch('max_valid_timestamp', 'olist_analytics')()) }}
{%- endmacro %}

{% macro default__max_valid_timestamp() -%}
    {{ timestamp_literal('9999-12-31') }}
{%- endmacro %}

{% macro clickhouse__max_valid_timestamp() -%}
    toDateTime64('2299-12-31 00:00:00', 6, 'UTC')
{%- endmacro %}

{% macro hash_key(expression) -%}
    {{ return(adapter.dispatch('hash_key', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__hash_key(expression) -%}
    md5({{ expression }})
{%- endmacro %}

{% macro clickhouse__hash_key(expression) -%}
    lower(hex(MD5({{ expression }})))
{%- endmacro %}

{% macro timestamp_key_string(expression) -%}
    {{ return(adapter.dispatch('timestamp_key_string', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__timestamp_key_string(expression) -%}
    to_char({{ expression }}, 'YYYY-MM-DD HH24:MI:SS')
{%- endmacro %}

{% macro clickhouse__timestamp_key_string(expression) -%}
    formatDateTime({{ expression }}, '%Y-%m-%d %H:%i:%S')
{%- endmacro %}

{% macro dateadd_days(timestamp_expression, days) -%}
    {{ return(adapter.dispatch('dateadd_days', 'olist_analytics')(timestamp_expression, days)) }}
{%- endmacro %}

{% macro default__dateadd_days(timestamp_expression, days) -%}
    ({{ timestamp_expression }} + ({{ days }} * interval '1 day'))
{%- endmacro %}

{% macro redshift__dateadd_days(timestamp_expression, days) -%}
    dateadd(day, {{ days }}, {{ timestamp_expression }})
{%- endmacro %}

{% macro clickhouse__dateadd_days(timestamp_expression, days) -%}
    addDays({{ timestamp_expression }}, {{ days }})
{%- endmacro %}

{% macro days_between(start_expression, end_expression) -%}
    {{ return(adapter.dispatch('days_between', 'olist_analytics')(start_expression, end_expression)) }}
{%- endmacro %}

{% macro default__days_between(start_expression, end_expression) -%}
    (({{ end_expression }})::date - ({{ start_expression }})::date)
{%- endmacro %}

{% macro redshift__days_between(start_expression, end_expression) -%}
    datediff(day, {{ start_expression }}, {{ end_expression }})
{%- endmacro %}

{% macro clickhouse__days_between(start_expression, end_expression) -%}
    dateDiff('day', {{ start_expression }}, {{ end_expression }})
{%- endmacro %}

{% macro month_start(expression) -%}
    {{ return(adapter.dispatch('month_start', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__month_start(expression) -%}
    cast(date_trunc('month', {{ expression }}) as date)
{%- endmacro %}

{% macro clickhouse__month_start(expression) -%}
    toDate(toStartOfMonth({{ expression }}))
{%- endmacro %}

{% macro date_key(expression) -%}
    {{ return(adapter.dispatch('date_key', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__date_key(expression) -%}
    cast(to_char({{ expression }}, 'YYYYMMDD') as integer)
{%- endmacro %}

{% macro clickhouse__date_key(expression) -%}
    toInt32(formatDateTime({{ expression }}, '%Y%m%d'))
{%- endmacro %}

{% macro date_part(part_name, expression) -%}
    {{ return(adapter.dispatch('date_part', 'olist_analytics')(part_name, expression)) }}
{%- endmacro %}

{% macro default__date_part(part_name, expression) -%}
    cast(extract({{ part_name }} from {{ expression }}) as integer)
{%- endmacro %}

{% macro clickhouse__date_part(part_name, expression) -%}
    {%- if part_name == 'year' -%}
        toYear({{ expression }})
    {%- elif part_name == 'month' -%}
        toMonth({{ expression }})
    {%- elif part_name == 'day' -%}
        toDayOfMonth({{ expression }})
    {%- elif part_name == 'quarter' -%}
        toQuarter({{ expression }})
    {%- elif part_name == 'week' -%}
        toISOWeek({{ expression }})
    {%- elif part_name == 'dow' -%}
        modulo(toDayOfWeek({{ expression }}), 7)
    {%- else -%}
        {{ exceptions.raise_compiler_error("Unsupported ClickHouse date part: " ~ part_name) }}
    {%- endif -%}
{%- endmacro %}

{% macro year_month(expression) -%}
    {{ return(adapter.dispatch('year_month', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__year_month(expression) -%}
    to_char({{ expression }}, 'YYYY-MM')
{%- endmacro %}

{% macro clickhouse__year_month(expression) -%}
    formatDateTime({{ expression }}, '%Y-%m')
{%- endmacro %}

{% macro month_name(expression) -%}
    {{ return(adapter.dispatch('month_name', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__month_name(expression) -%}
    to_char({{ expression }}, 'Month')
{%- endmacro %}

{% macro clickhouse__month_name(expression) -%}
    rightPad(monthName({{ expression }}), 9, ' ')
{%- endmacro %}

{% macro nullable_window_value(expression) -%}
    {{ return(adapter.dispatch('nullable_window_value', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__nullable_window_value(expression) -%}
    {{ expression }}
{%- endmacro %}

{% macro clickhouse__nullable_window_value(expression) -%}
    toNullable({{ expression }})
{%- endmacro %}

{% macro output_column(expression, column_name) -%}
    {{ return(adapter.dispatch('output_column', 'olist_analytics')(expression, column_name)) }}
{%- endmacro %}

{% macro default__output_column(expression, column_name) -%}
    {{ expression }}
{%- endmacro %}

{% macro clickhouse__output_column(expression, column_name) -%}
    {{ expression }} as {{ column_name }}
{%- endmacro %}

{% macro count_where(predicate) -%}
    {{ return(adapter.dispatch('count_where', 'olist_analytics')(predicate)) }}
{%- endmacro %}

{% macro default__count_where(predicate) -%}
    count(*) filter (where {{ predicate }})
{%- endmacro %}

{% macro clickhouse__count_where(predicate) -%}
    countIf({{ predicate }})
{%- endmacro %}

{% macro is_distinct(left_expression, right_expression) -%}
    {{ return(adapter.dispatch('is_distinct', 'olist_analytics')(left_expression, right_expression)) }}
{%- endmacro %}

{% macro default__is_distinct(left_expression, right_expression) -%}
    {{ left_expression }} is distinct from {{ right_expression }}
{%- endmacro %}

{% macro clickhouse__is_distinct(left_expression, right_expression) -%}
    ifNull({{ left_expression }} != {{ right_expression }}, isNull({{ left_expression }}) != isNull({{ right_expression }}))
{%- endmacro %}

{% macro utc_timestamp(expression) -%}
    {{ return(adapter.dispatch('utc_timestamp', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__utc_timestamp(expression) -%}
    cast({{ expression }} as timestamp)
{%- endmacro %}

{% macro clickhouse__utc_timestamp(expression) -%}
    {{ cast_timestamp(expression) }}
{%- endmacro %}

{% macro decimal_literal(value, precision=18, scale=2) -%}
    {{ cast_decimal(value, precision, scale) }}
{%- endmacro %}

{% macro decimal_zero(precision=18, scale=2) -%}
    {{ decimal_literal('0', precision, scale) }}
{%- endmacro %}

{% macro bool_value(expression) -%}
    {{ return(adapter.dispatch('bool_value', 'olist_analytics')(expression)) }}
{%- endmacro %}

{% macro default__bool_value(expression) -%}
    {{ expression }}
{%- endmacro %}

{% macro clickhouse__bool_value(expression) -%}
    multiIf({{ expression }}, toUInt8(1), toUInt8(0))
{%- endmacro %}
