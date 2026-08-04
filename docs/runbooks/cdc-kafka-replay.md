# Target Kafka replay

Kafka replay is a bounded consumer recovery operation, not a source reset.

1. Record the topic, partition, current consumer group offsets and the latest
   Bronze/Silver status evidence.
2. Stop only the affected target Spark query through the documented lifecycle
   command; preserve Kafka Connect internal topics and the source database.
3. Reset only explicitly selected partitions and offsets, then restart the
   target query with its existing checkpoint contract.
4. Verify Bronze event identity/deduplication, Silver progress, transaction
   state and serving catch-up before publication.

Never combine replay with topic deletion, retention changes or credential
rotation. Keep before/after offsets in the evidence record.
