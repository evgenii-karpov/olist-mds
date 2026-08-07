WITH bounded AS
(
    {{ bounded_changes('silver_product_category_translation_changes') }}
)
SELECT {{ candidate_columns() }}, bounded.*
FROM bounded
