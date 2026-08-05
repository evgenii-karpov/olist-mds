SET time_zone = '+00:00';

START TRANSACTION;
INSERT INTO olist_oltp.customers VALUES
  ('acceptance_customer_001', 'acceptance_unique_001', '09999', 'sao paulo', 'SP');
INSERT INTO olist_oltp.orders VALUES
  ('acceptance_order_001', 'acceptance_customer_001', 'created',
   '2018-09-01 10:00:00.123456', NULL, NULL, NULL,
   '2018-09-10 00:00:00.000000');
INSERT INTO olist_oltp.order_items VALUES
  ('acceptance_order_001', 1, 'product_001', 'seller_001',
   '2018-09-03 12:00:00.000001', 10.00, 2.50),
  ('acceptance_order_001', 2, 'product_002', 'seller_002',
   '2018-09-03 12:00:00.000002', 20.00, 3.50);
INSERT INTO olist_oltp.order_payments VALUES
  ('acceptance_order_001', 1, 'credit_card', 1, 12.50),
  ('acceptance_order_001', 2, 'voucher', 1, 23.50);
INSERT INTO olist_oltp.order_reviews VALUES
  ('acceptance_review_001', 'acceptance_order_001', 5, 'acceptance', 'acceptance review',
   '2018-09-02 08:00:00.000001', '2018-09-02 09:00:00.000001');
COMMIT;
