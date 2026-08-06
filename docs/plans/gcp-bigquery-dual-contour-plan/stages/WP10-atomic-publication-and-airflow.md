# WP10 — Atomic Publication and GCP DAG

## Dependencies

WP9

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Complete the versioned publication procedure.
- Apply all model operations and control-state changes in one transaction.
- Implement idempotent already-active behavior and stale conflict behavior.
- Create `olist_gcp_serving` DAG.
- Invoke dbt through restricted Docker API access.
- Add failure injection, compensation-run, and retry tests.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Partial current-state publication is impossible in tests.
- A stale run cannot overwrite a newer active sequence.
- A published correction/rollback uses a new compensating run.
- Airflow never starts or owns long-lived streaming.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
