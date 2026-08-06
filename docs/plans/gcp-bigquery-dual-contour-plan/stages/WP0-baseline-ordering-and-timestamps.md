# WP0 — Baseline, Ordering, and Timestamp Contract

## Dependencies

None

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Pin repository baseline and archive current local acceptance evidence.
- Implement validated binlog filename/index parsing.
- Define event categories and required-field validation.
- Centralize the canonical ordering tuple for Scala, Python, ClickHouse SQL, and BigQuery SQL.
- Replace repository-owned `TIMESTAMP_NTZ` specs with UTC instant semantics.
- Add `SOURCE_TIME_ZONE` with default `America/Sao_Paulo`.
- Destructively rebuild local Iceberg/ClickHouse/Gold fixtures.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Ordering tests cover snapshot, non-transactional, transactional, malformed, missing, and tie cases.
- The local contour passes after rebuild.
- No latest-row implementation uses timestamp/event ID as an undocumented fallback.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
