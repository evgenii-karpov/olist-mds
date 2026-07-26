{% macro round_two_decimals(expression) -%}
    {{ cast_decimal('round(' ~ expression ~ ', 2)', 18, 2) }}
{%- endmacro %}
