# WP1 — Compose Profiles and `lab.py`

## Dependencies

WP0

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Rename/refactor `local-lab.py` to `scripts/lab.py`.
- Create `core`, `lakehouse-local`, and `lakehouse-gcp` ownership boundaries.
- Split common PostgreSQL bootstrap from Polaris bootstrap.
- Add profile exclusivity validation.
- Add explicit local/GCP streaming lifecycle commands.
- Preserve existing local command semantics through compatibility aliases where practical.
- Make the parser accept the exact normative command tree in `appendices/A-command-surface.md`.
- Keep credential and configuration preflight mandatory for every mutating GCP start operation; do not expose an operator flag that bypasses missing authentication.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Both supported Compose combinations render.
- GCP render contains no Polaris/MinIO/ClickHouse dependency or credential.
- Local render requires no ADC/GCP variables.
- `gcp up` does not start streaming.
- Parser tests cover every normative WP1 command, including `lab.py local serving run`.
- `gcp up` and `gcp streaming start` refuse incomplete preflight, and no public CLI option bypasses that refusal.
- Compatibility aliases exercise the same target/profile validation as the canonical commands.

## Post-review amendment

Successful Compose rendering is necessary but not sufficient. WP1 acceptance also covers the operator-visible CLI grammar and guards. Tests that call private Python handlers directly do not replace parser-level tests of the documented commands.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
