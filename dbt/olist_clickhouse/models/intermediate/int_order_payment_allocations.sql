WITH item_amounts AS
(
    SELECT
        order_id,
        order_item_id,
        price,
        freight_value,
        price + freight_value AS item_gross_amount,
        sum(price + freight_value) OVER (PARTITION BY order_id)
            AS order_gross_amount
    FROM {{ ref('stg_order_items_current') }}
),

order_payments AS
(
    SELECT
        order_id,
        sum(payment_value) AS order_payment_value
    FROM {{ ref('stg_order_payments_current') }}
    GROUP BY order_id
)

SELECT
    item_amounts.order_id AS order_id,
    item_amounts.order_item_id AS order_item_id,
    item_amounts.item_gross_amount,
    item_amounts.order_gross_amount,
    order_payments.order_payment_value,
    if(
        item_amounts.order_gross_amount = 0,
        CAST(NULL, 'Nullable(Decimal(18, 2))'),
        CAST(
            round(
                order_payments.order_payment_value
                * item_amounts.item_gross_amount
                / item_amounts.order_gross_amount,
                2
            ),
            'Nullable(Decimal(18, 2))'
        )
    ) AS allocated_payment_value
FROM item_amounts
LEFT JOIN order_payments USING (order_id)
