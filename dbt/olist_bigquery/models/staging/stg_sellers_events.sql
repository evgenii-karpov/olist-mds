WITH bounded AS
(
    {{ bounded_changes('silver_sellers_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
