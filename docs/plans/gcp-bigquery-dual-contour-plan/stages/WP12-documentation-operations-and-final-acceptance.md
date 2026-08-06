# WP12 — Documentation, Operations, and Final Acceptance

## Dependencies

WP11

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Document bootstrap, daily operation, reset, destroy, troubleshooting, and recovery.
- Document no-go redesign process without prescribing a fallback.
- Document Preview constraints and exact tested versions.
- Run final local acceptance, GCP acceptance, parity, retry/conflict/recovery tests.
- Run `gcp destroy --force` and verify residual resources.
- Record final architecture decision and completion evidence.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Both contours are independently operable.
- All acceptance-matrix rows have evidence.
- Main GCP resources are removed when required and the state-bucket exception is explicit.
- The implementation matches the decision register.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
