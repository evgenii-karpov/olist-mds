WITH invalid_windows AS
(
    SELECT *
    FROM {{ ref('dim_customer_scd2') }}
    WHERE
        sync_run_seq = {{ sync_run_seq_sql() }}
        AND valid_to IS NOT NULL
        AND valid_to <= valid_from
),

overlaps AS
(
    SELECT
        left_side.sync_run_seq,
        left_side.customer_unique_id,
        left_side.customer_key AS left_customer_key,
        right_side.customer_key AS right_customer_key
    FROM {{ ref('dim_customer_scd2') }} AS left_side
    INNER JOIN {{ ref('dim_customer_scd2') }} AS right_side
        ON
            left_side.sync_run_seq = {{ sync_run_seq_sql() }}
            AND left_side.sync_run_seq = right_side.sync_run_seq
            AND left_side.customer_unique_id = right_side.customer_unique_id
            AND left_side.customer_key < right_side.customer_key
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

SELECT sync_run_seq, customer_unique_id, customer_key AS failure_key
FROM invalid_windows
UNION ALL
SELECT sync_run_seq, customer_unique_id, left_customer_key AS failure_key
FROM overlaps
