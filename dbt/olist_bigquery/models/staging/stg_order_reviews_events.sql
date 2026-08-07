WITH bounded AS
(
    {{ bounded_changes('silver_order_reviews_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
