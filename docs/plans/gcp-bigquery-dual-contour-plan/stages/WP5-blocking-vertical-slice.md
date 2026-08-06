# WP5 — Blocking GCP Vertical Slice

## Dependencies

WP4

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Load the four representative tables.
- Test direct P.C.N.T reads and bridge views.
- Test timestamps, NUMERIC/BIGNUMERIC, binary, nested fields, and schema visibility.
- Restart from checkpoints and test duplicate/retry behavior.
- Query during additional Spark commits.
- Record cost, latency, metadata-size, and exact runtime versions.
- Produce a manual go/no-go decision record.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- All four tables pass the mandatory matrix.
- The decision is explicitly GO, GO-WITH-CONSTRAINTS, or NO-GO.
- No full table/model port starts before this record exists.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
