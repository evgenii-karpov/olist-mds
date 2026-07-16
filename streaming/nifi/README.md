# NiFi assets

Phase 3 owns the version-controlled process group, parameter-context templates,
and flow validation fixtures here. Environment-specific parameter values must
not change the shared logical event contract.

The landing writer publishes data first, its ordinary manifest second, and an
immutable coverage manifest last. Coverage contains exact consumed,
business-event, and tombstone ranges and references the durable landing
identities. A retry reuses identical keys and fails closed on conflicting bytes.
