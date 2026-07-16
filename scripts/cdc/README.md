# Shared CDC application logic

Phase 4 and later own object discovery, immutable normalized and coverage
manifests, transactional loading, reconciliation, exact offset-coverage
watermarks, replay, and read-only pipeline metrics here.

Warehouse continuity is `NORMALIZED_LOADED union TOMBSTONE_AUDITED`. Never use
landing business ranges to advance a warehouse watermark before their normalized
events commit to `raw_cdc`.
`SOURCE_CONSUMED` records the expected horizon so missing business tail offsets
are visible. Replay files remain bound to their idempotent request ID until the
replay run claims them.
