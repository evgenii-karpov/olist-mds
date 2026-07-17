# CDC Kafka replay

Kafka replay is a consumer recovery operation, not a source resnapshot.

1. Record the target topic, partitions, current group offsets, and immutable
   object/warehouse watermarks.
2. Stop NiFi and export the current `olist-nifi-cdc-v1` group offsets.
3. Reset only the selected topic partitions to an explicitly recorded offset;
   never reset Connect internal topics or the Debezium connector group.
4. Start NiFi and observe lag drain, deterministic object names, verified
   coverage, warehouse `_event_id` deduplication, and offset continuity.
5. Compare object rows, inserted rows, duplicates, and rejected rows. A replay
   may increase duplicate counters but must not increase unique event or mart
   grain counts.

Keep the before/after offsets in the incident record. Do not combine replay with
topic deletion, retention changes, or resnapshot.
