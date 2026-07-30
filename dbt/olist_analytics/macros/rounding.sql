{% macro round_two_decimals(expression) -%}
    {{ cast_nullable_decimal('round(' ~ expression ~ ', 2)', 18, 2) }}
{%- endmacro %}
