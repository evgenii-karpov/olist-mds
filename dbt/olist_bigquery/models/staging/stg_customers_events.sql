WITH bounded AS
(
    {{ bounded_changes('silver_customers_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
