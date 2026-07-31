# NiFi assets

Phase 3 owns the version-controlled process group, parameter-context templates,
and flow validation fixtures here. Environment-specific parameter values must
not change the shared logical event contract.

The landing writer publishes data first, its ordinary manifest second, and an
immutable coverage manifest last. Coverage contains exact consumed,
business-event, and tombstone ranges and references the durable landing
identities. A retry reuses identical keys and fails closed on conflicting bytes.

Each branch uses a short 8 MiB micro-batch `MergeRecord` before the existing
32–64 MiB final merge. Single-event Avro containers are intentionally written
with the `null` codec; only the shared final Avro writer applies DEFLATE. The
two branch connections rely on NiFi's relationship fan-out, so business events
are cloned directly to landing and normalized without `copy.index` routing.
