# WP7 — BigQuery Migrations and Bridge

## Dependencies

WP6

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Implement migration runner and ledger.
- Create control tables and boundary/result schemas.
- Create bridge views for required Iceberg sources with explicit type normalization.
- Create Gold history/current tables and stable serving views.
- Create publication procedure skeleton and permissions.
- Add migration/static tests.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Migrations apply idempotently.
- Bridge views survive source refreshes covered by the accepted schema contract.
- All application schemas are SQL-owned, not Terraform-owned.
- dbt runner has only required dataset permissions.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
