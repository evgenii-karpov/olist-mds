CREATE VIEW IF NOT EXISTS serving_cdc.customers_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY customer_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.customers_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.orders_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY order_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.orders_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.order_items_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY order_id, order_item_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.order_items_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.order_payments_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY order_id, payment_sequential
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.order_payments_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.order_reviews_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY review_id, order_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.order_reviews_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.products_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY product_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.products_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.sellers_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY seller_id
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.sellers_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;

CREATE VIEW IF NOT EXISTS serving_cdc.product_category_translation_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY product_category_name
            ORDER BY
                if(last_is_snapshot, 0, 1) DESC,
                coalesce(last_source_binlog_file_index, -1) DESC,
                coalesce(last_source_binlog_pos, -1) DESC,
                coalesce(last_source_row, -1) DESC,
                coalesce(toInt64(last_transaction_total_order), -1) DESC,
                coalesce(toInt64(last_transaction_data_collection_order), -1) DESC,
                last_source_ts DESC,
                kafka_partition DESC,
                kafka_offset DESC,
                last_event_id DESC,
                sync_run_seq DESC
        ) AS _version_rank
    FROM serving_cdc.product_category_translation_current_versions
    WHERE sync_run_seq IN
    (
        SELECT sync_run_seq
        FROM serving_control.published_runs_current
        WHERE publication_status = 'PUBLISHED'
    )
)
WHERE _version_rank = 1 AND NOT is_deleted;
