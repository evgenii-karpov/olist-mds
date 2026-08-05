-- Learning & regression test: candidate isolation by sync_run_seq
-- Verifies that unpublished candidate rows in current_versions do not replace published versions in stable views

-- 1. Insert published version for sync_run_seq 1
INSERT INTO serving_cdc.customers_current_versions (
    sync_run_seq, sync_run_id, customer_id, customer_unique_id, customer_zip_code_prefix,
    customer_city, customer_state, is_deleted, last_event_id, last_source_ts,
    kafka_partition, kafka_offset, last_row_hash, contract_version, updated_at
) VALUES (
    1, 'sync-00000000000000000001', 'cust_test_iso_1', 'unique_iso_1', '01000',
    'Sao Paulo', 'SP', 0, 'ev_1', now64(6, 'UTC'),
    0, 10, 'hash1', 2, now64(6, 'UTC')
);

-- 2. Insert published marker for sync_run_seq 1
INSERT INTO serving_control.published_runs (
    sync_run_seq, sync_run_id, publication_status, source_snapshot_completed, published_at, report_json
) VALUES (
    1, 'sync-00000000000000000001', 'PUBLISHED', 1, now64(6, 'UTC'), '{"sync_run_seq":1}'
);

-- 3. Insert UNPUBLISHED candidate for sync_run_seq 2 for the same PK with higher offset
INSERT INTO serving_cdc.customers_current_versions (
    sync_run_seq, sync_run_id, customer_id, customer_unique_id, customer_zip_code_prefix,
    customer_city, customer_state, is_deleted, last_event_id, last_source_ts,
    kafka_partition, kafka_offset, last_row_hash, contract_version, updated_at
) VALUES (
    2, 'sync-00000000000000000002', 'cust_test_iso_1', 'unique_iso_1_UPDATED', '01000',
    'Sao Paulo', 'SP', 0, 'ev_2', now64(6, 'UTC'),
    0, 20, 'hash2', 2, now64(6, 'UTC')
);

-- 4. Execute OPTIMIZE TABLE to trigger physical merge
OPTIMIZE TABLE serving_cdc.customers_current_versions FINAL;

-- 5. Query stable view customers_current - must still return published version from sync_run_seq 1
SELECT customer_unique_id FROM serving_cdc.customers_current WHERE customer_id = 'cust_test_iso_1';

-- Clean up test rows
ALTER TABLE serving_cdc.customers_current_versions DROP PARTITION 1;
ALTER TABLE serving_cdc.customers_current_versions DROP PARTITION 2;
ALTER TABLE serving_control.published_runs DROP PARTITION 1;
