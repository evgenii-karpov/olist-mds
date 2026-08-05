CREATE VIEW IF NOT EXISTS serving_cdc.customers_current AS
SELECT * EXCEPT (_version_rank)
FROM
(
    SELECT
        *,
        row_number() OVER (
            PARTITION BY customer_id
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
            ORDER BY kafka_offset DESC, sync_run_seq DESC
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
