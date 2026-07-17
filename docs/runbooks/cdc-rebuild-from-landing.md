# Rebuild normalized CDC from landing

Landing Avro and its immutable coverage manifest are the recovery source when a
normalized object is missing or invalid.

1. Identify the exact topic/partition/offset range and verify landing object
   ETag, SHA-256, schema IDs, and coverage reference.
2. Use a new rebuild prefix and flow/run ID. Never overwrite the original
   landing, normalized, or coverage object.
3. Decode through the same versioned Avro registry/schema contract and run the
   same NiFi normalization scripts against the selected landing object.
4. Publish a deterministic normalized object and manifest under the rebuild
   prefix, then compare row/operation/offset counts to landing coverage.
5. Load through the normal warehouse replay ledger. `_event_id` deduplication
   must make repeated recovery harmless.

Quarantine schema-incompatible records; do not coerce them to make coverage
appear contiguous.
