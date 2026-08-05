CREATE TABLE IF NOT EXISTS serving_control.published_runs
(
    sync_run_seq UInt64,
    sync_run_id String,
    previous_transaction_id Nullable(String),
    target_transaction_id Nullable(String),
    publication_status LowCardinality(String),
    source_snapshot_completed Bool,
    published_at DateTime64(6, 'UTC'),
    report_json String DEFAULT '{}'
)
ENGINE = ReplacingMergeTree(published_at)
PARTITION BY tuple()
ORDER BY sync_run_seq;

CREATE VIEW IF NOT EXISTS serving_control.published_runs_current AS
SELECT
    sync_run_seq,
    sync_run_id,
    previous_transaction_id,
    target_transaction_id,
    publication_status,
    source_snapshot_completed,
    published_at,
    report_json
FROM serving_control.published_runs FINAL;
