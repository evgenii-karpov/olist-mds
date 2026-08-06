# WP6 — Full GCP Iceberg Lakehouse

## Dependencies

WP5 = GO or GO-WITH-CONSTRAINTS

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Port all Bronze, Silver, Reference, and Audit table writers/configuration.
- Run the clean initial MySQL/Debezium/Kafka replay.
- Validate independent GCP checkpoints and restarts.
- Implement audit/quarantine failure handling for ordering/transaction issues.
- Validate `audit.silver_progress` across all entities.
- Add operational inventory and reset-data support.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- All repository Iceberg tables exist in the managed catalog.
- Spark reaches stable progress from a clean replay.
- GCP can reset/rebuild without touching the local contour.
- BigQuery source reads remain read-only.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
