{% test unique_combination_of_columns(model, combination_of_columns) %}
SELECT
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}
FROM {{ model }}
GROUP BY
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}
HAVING count() > 1
{% endtest %}

{% test non_negative(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE {{ column_name }} < 0
{% endtest %}
