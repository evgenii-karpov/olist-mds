# Controlled Debezium resnapshot

Use a resnapshot only when the source-to-Kafka boundary itself must be rebuilt.
It always uses an explicitly recorded isolation boundary.

1. Record MySQL source state, connector/task state, topic offsets and the
   current Iceberg/serving boundary.
2. Stop the connector without deleting its internal topics or the existing
   target checkpoint.
3. Create a separately named connector/topic boundary and register it from the
   secret-free template; never overwrite the existing evidence.
4. Snapshot into the isolated target topics and run the bounded Spark contract
   checks.
5. Compare source counts, Bronze identity, Silver current state and serving
   output before approving a cutover.

Keep the old boundary until rollback is no longer required, then remove it in a
separate reviewed change.
