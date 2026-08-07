WITH bounded AS
(
    {{ bounded_changes('silver_products_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
