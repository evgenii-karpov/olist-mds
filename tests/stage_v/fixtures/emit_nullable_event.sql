SET time_zone = '+00:00';

START TRANSACTION;
UPDATE olist_oltp.customers
SET customer_city = 'sao paulo stage v',
    stage_v_optional_note = NULL
WHERE customer_id = 'wave2_customer_001';
COMMIT;
