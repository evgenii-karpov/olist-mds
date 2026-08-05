{% test candidate_not_null(model, column_name) %}
SELECT {{ column_name }}
FROM {{ model }}
WHERE
    sync_run_seq = {{ sync_run_seq_sql() }}
    AND {{ column_name }} IS NULL
{% endtest %}

{% test candidate_relationships(model, column_name, to, field) %}
WITH child AS
(
    SELECT {{ column_name }} AS from_field
    FROM {{ model }}
    WHERE
        sync_run_seq = {{ sync_run_seq_sql() }}
        AND {{ column_name }} IS NOT NULL
),

parent AS
(
    SELECT {{ field }} AS to_field
    FROM {{ to }}
    WHERE sync_run_seq = {{ sync_run_seq_sql() }}
)

SELECT child.from_field
FROM child
LEFT JOIN parent ON child.from_field = parent.to_field
WHERE parent.to_field IS NULL
{% endtest %}

{% test unique_combination_of_columns(model, combination_of_columns) %}
SELECT
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}
FROM {{ model }}
WHERE sync_run_seq = {{ sync_run_seq_sql() }}
GROUP BY
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}
HAVING count() > 1
{% endtest %}

{% test non_negative(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE
    sync_run_seq = {{ sync_run_seq_sql() }}
    AND {{ column_name }} < 0
{% endtest %}
