# WP9 — Incremental `dbt-bigquery` Gold

## Dependencies

WP8

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Create the dedicated pinned dbt Compose service.
- Port all Gold business semantics to independent BigQuery SQL.
- Build full initial deltas, then exact interval-based incremental deltas.
- Implement impacted-key/grain propagation.
- Implement per-model delete/SCD2/aggregate operation generation.
- Write one history table per model keyed by run and operation.
- Add model/unit/data tests and artifacts.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- The first run can populate empty current tables through publication.
- A later run touches only impacted keys/grains.
- Same-run rebuild deletes/recreates only that run history.
- No model uses a fixed `updated_at` lookback.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
