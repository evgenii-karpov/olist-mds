# WP11 — Parity, Observability, CI, and Cost

## Dependencies

WP10

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Implement sequential parity CLI and normalization rules.
- Emit JSON and Markdown parity reports.
- Add required Prometheus metrics and Grafana panels.
- Add BigQuery labels, byte caps, and job-byte recording.
- Add credential-free cloud static checks to CI.
- Add budget/preflight/residual-resource reporting.
- Run full local/GCP parity fixture.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Strict parity passes or all accepted representation differences are documented.
- CI uses no GCP credentials/resources.
- `dbt-bigquery parse` passes; no online compile requirement is introduced.
- Observed real monetary spend remains zero.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
