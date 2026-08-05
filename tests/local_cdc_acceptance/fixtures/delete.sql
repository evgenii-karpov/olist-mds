SET time_zone = '+00:00';

START TRANSACTION;
DELETE FROM olist_oltp.order_reviews
WHERE review_id = 'acceptance_review_001'
  AND order_id = 'acceptance_order_001';
COMMIT;
