WITH allocation_balance AS
(
    SELECT
        order_id,
        count() AS item_count,
        sum(allocated_payment_value) AS allocated_total,
        max(order_payment_value) AS payment_total
    FROM {{ ref('int_order_payment_allocations') }}
    WHERE order_payment_value IS NOT NULL
    GROUP BY order_id
)

SELECT *
FROM allocation_balance
WHERE
    abs(allocated_total - payment_total)
        > greatest(toDecimal64(item_count, 2) / 100, toDecimal64(0.01, 2))
