SET time_zone = '+00:00';

START TRANSACTION;
UPDATE olist_oltp.customers
SET customer_city = 'sao paulo acceptance',
    acceptance_optional_note = NULL
WHERE customer_id = 'acceptance_customer_001';
COMMIT;
