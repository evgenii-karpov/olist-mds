SET time_zone = '+00:00';

START TRANSACTION;
UPDATE olist_oltp.orders
SET order_status = 'approved',
    order_approved_at = '2018-09-01 10:05:00.123456'
WHERE order_id = 'wave2_order_001';
UPDATE olist_oltp.order_items
SET price = 19.99
WHERE order_id = 'wave2_order_001' AND order_item_id = 2;
COMMIT;
