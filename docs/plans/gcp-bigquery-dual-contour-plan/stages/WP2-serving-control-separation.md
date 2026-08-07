# WP2 — Serving-Control Separation

## Dependencies

WP0, WP1

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Extract provider-independent run/boundary/result domain models.
- Keep the local persistence adapter in PostgreSQL.
- Design BigQuery-native control tables and state transitions.
- Implement global sequence semantics per target without sharing physical state.
- Add optimistic-predecessor and same-run retry contracts.
- Define the allowed run-status transition matrix once and apply it to the reference ledger and both persistence adapters.
- Add adapter conformance scenarios for stale predecessors, retries, duplicate results, and transaction rollback.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Local DAG behavior remains valid.
- GCP control schema is migration-ready.
- Tests prove one target cannot advance or mutate the other.
- A run can advance active state only when the requested predecessor equals both the target's current active sequence and the predecessor frozen on the run at allocation time.
- Same-run retry preserves run identity, sequence, frozen boundary, and predecessor while clearing only retry-owned candidate/result state.
- Invalid status transitions, duplicate logical results, stale compare-and-set attempts, and failed transactions leave active state unchanged and no partial mutation behind.
- The provider-independent reference ledger and persistence adapters pass the same transition-contract scenarios where their capabilities overlap.

## Post-review amendment

Cross-target isolation alone does not close WP2. Optimistic concurrency must be tested after allocation: advancing another run between planning and publication must make the earlier run stale even if a caller supplies the new active sequence. Persistence-specific SQL tests must assert transaction shape and rollback behavior, not only the presence of expected SQL fragments.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
