CREATE TABLE IF NOT EXISTS pipeline_runtime.cdc_transform_run_files
(
    transform_run_id String,
    object_uri String,
    manifest_sha256 FixedString(64),
    selected_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(selected_at)
PARTITION BY toYYYYMM(selected_at)
ORDER BY (transform_run_id, object_uri)
TTL selected_at + INTERVAL 7 DAY DELETE;
