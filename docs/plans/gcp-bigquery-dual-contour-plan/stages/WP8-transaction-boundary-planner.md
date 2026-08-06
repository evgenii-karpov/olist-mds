# WP8 — Transaction-Complete Boundary Planner

## Dependencies

WP2, WP6, WP7

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Implement Debezium transaction-metadata reader.
- Freeze per-topic/partition offsets at the last complete source transaction.
- Fail closed on missing/incomplete metadata.
- Persist predecessor and exact change interval.
- Wait for `audit.silver_progress` and revalidate after build.
- Implement same-sequence retry state transitions.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- No test boundary splits a transaction.
- End-offset/idle-pause fallback does not exist.
- A boundary can be replayed deterministically.
- Stale predecessor state is detectable.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
