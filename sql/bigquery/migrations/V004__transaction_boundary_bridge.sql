-- Read-only bridge for Debezium transaction metadata used by WP8.
--
-- The view exposes the append-only audit evidence needed to select a
-- transaction-complete serving prefix.  It deliberately does not infer a
-- boundary from Kafka end offsets or wall-clock idleness.

CREATE OR REPLACE VIEW `{{ project_id }}.olist_lakehouse_bridge.audit_mysql_transactions`
OPTIONS (
  description = 'Read-only normalized bridge over Debezium transaction metadata'
)
AS
SELECT
  CAST(`transaction_id` AS STRING) AS transaction_id,
  CAST(`status` AS STRING) AS status,
  CAST(`event_count` AS INT64) AS event_count,
  ARRAY(
    SELECT AS STRUCT
      CAST(collection.`data_collection` AS STRING) AS data_collection,
      CAST(collection.`event_count` AS INT64) AS event_count
    FROM UNNEST(`data_collections`) AS collection
  ) AS data_collections,
  CAST(`begin_event_id` AS STRING) AS begin_event_id,
  CAST(`end_event_id` AS STRING) AS end_event_id,
  CAST(`kafka_topic` AS STRING) AS kafka_topic,
  CAST(`kafka_partition` AS INT64) AS kafka_partition,
  CAST(`begin_kafka_offset` AS INT64) AS begin_kafka_offset,
  CAST(`end_kafka_offset` AS INT64) AS end_kafka_offset,
  CAST(`source_ts` AS TIMESTAMP) AS source_ts,
  CAST(`first_seen_at` AS TIMESTAMP) AS first_seen_at,
  CAST(`completed_at` AS TIMESTAMP) AS completed_at,
  ARRAY(
    SELECT CAST(event_id AS STRING)
    FROM UNNEST(`rejected_event_ids`) AS event_id
  ) AS rejected_event_ids,
  CAST(`recorded_at` AS TIMESTAMP) AS recorded_at
FROM `{{ project_id }}.{{ catalog_id }}.audit.mysql_transactions`;
