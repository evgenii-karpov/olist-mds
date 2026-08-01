SELECT
    sync_run_seq,
    order_id,
    order_item_id,
    count() AS duplicate_count
FROM {{ ref('fact_order_items') }}
GROUP BY sync_run_seq, order_id, order_item_id
HAVING duplicate_count > 1
