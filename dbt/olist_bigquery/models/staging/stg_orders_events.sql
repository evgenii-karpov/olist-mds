WITH bounded AS
(
    {{ bounded_changes('silver_orders_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
