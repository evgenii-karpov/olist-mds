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

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Local DAG behavior remains valid.
- GCP control schema is migration-ready.
- Tests prove one target cannot advance or mutate the other.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
