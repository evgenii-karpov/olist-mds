WITH invalid_windows AS
(
    SELECT *
    FROM {{ ref('dim_product_scd2') }}
    WHERE valid_to IS NOT NULL AND valid_to <= valid_from
),

overlaps AS
(
    SELECT
        left_side.sync_run_seq,
        left_side.product_id,
        left_side.product_key AS left_product_key,
        right_side.product_key AS right_product_key
    FROM {{ ref('dim_product_scd2') }} AS left_side
    INNER JOIN {{ ref('dim_product_scd2') }} AS right_side
        ON
            left_side.sync_run_seq = right_side.sync_run_seq
            AND left_side.product_id = right_side.product_id
            AND left_side.product_key < right_side.product_key
            AND left_side.valid_from
                < coalesce(
                    right_side.valid_to,
                    toDateTime64('2299-12-31 00:00:00', 6, 'UTC')
                )
            AND right_side.valid_from
                < coalesce(
                    left_side.valid_to,
                    toDateTime64('2299-12-31 00:00:00', 6, 'UTC')
                )
)

SELECT sync_run_seq, product_id, product_key AS failure_key
FROM invalid_windows
UNION ALL
SELECT sync_run_seq, product_id, left_product_key AS failure_key
FROM overlaps
