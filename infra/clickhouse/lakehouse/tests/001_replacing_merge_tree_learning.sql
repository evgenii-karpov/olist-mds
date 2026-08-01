DROP TABLE IF EXISTS serving_cdc._learning_current_versions;

CREATE TABLE serving_cdc._learning_current_versions
(
    business_key String,
    value String,
    is_deleted Bool,
    kafka_offset Int64
)
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY tuple()
ORDER BY business_key;

SYSTEM STOP MERGES serving_cdc._learning_current_versions;

-- Keep every logical version in a separate part.  ClickHouse 26.3 can
-- collapse duplicate ORDER BY keys inside one multi-row INSERT before a
-- plain read, which would make the physical-version assertion meaningless.
INSERT INTO serving_cdc._learning_current_versions VALUES ('visible', 'old', false, 1);
INSERT INTO serving_cdc._learning_current_versions VALUES ('visible', 'new', false, 2);
INSERT INTO serving_cdc._learning_current_versions VALUES ('deleted', 'before-delete', false, 1);
INSERT INTO serving_cdc._learning_current_versions VALUES ('deleted', 'before-delete', true, 2);

SELECT throwIf(
    (SELECT count() FROM serving_cdc._learning_current_versions) != 4,
    'plain SELECT must be allowed to observe multiple physical versions'
);

SELECT throwIf(
    (
        SELECT count()
        FROM serving_cdc._learning_current_versions FINAL
    ) != 2,
    'SELECT FINAL must return one latest version per business key'
);

SELECT throwIf(
    (
        SELECT argMax(value, kafka_offset)
        FROM serving_cdc._learning_current_versions
        WHERE business_key = 'visible'
    ) != 'new',
    'argMax must agree with the latest FINAL value'
);

SELECT throwIf(
    (
        SELECT count()
        FROM
        (
            SELECT
                business_key,
                argMax(is_deleted, kafka_offset) AS latest_is_deleted
            FROM serving_cdc._learning_current_versions
            GROUP BY business_key
        )
        WHERE NOT latest_is_deleted
    ) != 1,
    'a delete flag must be applied after version deduplication'
);

SYSTEM START MERGES serving_cdc._learning_current_versions;
DROP TABLE serving_cdc._learning_current_versions;
