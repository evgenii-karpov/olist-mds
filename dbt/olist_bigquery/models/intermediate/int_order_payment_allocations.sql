WITH item_amounts AS
(
    SELECT
        order_id,
        order_item_id,
        price,
        freight_value,
        CAST(price + freight_value AS NUMERIC) AS item_gross_amount,
        SUM(price + freight_value) OVER (PARTITION BY order_id)
            AS order_gross_amount
    FROM {{ ref('stg_order_items_current') }}
    WHERE NOT is_deleted
),
order_payments AS
(
    SELECT
        order_id,
        SUM(payment_value) AS order_payment_value
    FROM {{ ref('stg_order_payments_current') }}
    WHERE NOT is_deleted
    GROUP BY order_id
)
SELECT
    item_amounts.order_id,
    item_amounts.order_item_id,
    item_amounts.item_gross_amount,
    item_amounts.order_gross_amount,
    order_payments.order_payment_value,
    CASE
        WHEN item_amounts.order_gross_amount = 0 THEN CAST(NULL AS NUMERIC)
        ELSE ROUND(
            SAFE_DIVIDE(
                order_payments.order_payment_value
                    * item_amounts.item_gross_amount,
                item_amounts.order_gross_amount
            ),
            2
        )
    END AS allocated_payment_value
FROM item_amounts
LEFT JOIN order_payments USING (order_id)
