# Controlled Debezium resnapshot

Resnapshot is a last-resort migration and always uses a new isolation boundary.

1. Pause simulator writes and record source LSNs, Kafka offsets, object
   watermarks, and warehouse counts.
2. Stop the connector without deleting its old slot, publication, offsets, or
   topics.
3. Create a new explicitly named slot and topic prefix. Update a copy of the
   connector template; never reuse `olist_cdc_slot` for the trial snapshot.
4. Snapshot into new topics and a new NiFi/object load boundary.
5. Reconcile the snapshot with OLTP, build in isolated warehouse schemas, and
   run full parity.
6. Switch consumers only after approval. Retain the old boundary until rollback
   is no longer required, then remove it through a separately reviewed change.
