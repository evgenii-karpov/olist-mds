# WP2 — Serving-Control Separation Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**WP2 is complete for the credential-free implementation and local acceptance
available without GCP access.**

The serving-control domain now has explicit target, boundary, run, result,
predecessor, and same-run retry contracts. Local state remains in PostgreSQL;
the GCP adapter and migration are isolated to BigQuery's
`olist_serving_control` dataset. No cloud API, BigQuery job, or Terraform
operation was executed.

## Implemented

- Added provider-independent contracts in `scripts/serving/domain.py`:
  `ServingBoundary`, `ServingRun`, `ServingResult`, `ServingTarget`, and a
  deterministic target-scoped reference ledger.
- Added `PostgresServingControlAdapter` as the local persistence adapter.
  PostgreSQL control rows are explicitly `target = 'local'`, and local status
  transitions/retries check the active predecessor.
- Added `BigQueryServingControlRepository` with an injected query-runner
  protocol. It allocates sequences from GCP-local control state, uses
  BigQuery multi-statement transactions, reports DML conflicts through
  `@@row_count`, and never consults PostgreSQL state.
- Added the parameterized
  `sql/bigquery/migrations/V001__control_tables.sql` migration for control
  state, runs, frozen offsets, entity/model results, publication state and the
  checksummed migration ledger. Terraform creates the dataset; SQL owns these
  application tables and seed rows.
- Added optimistic predecessor compare-and-set and same-run retry transitions.
  A retry preserves `sync_run_seq`, run identity, predecessor and frozen
  boundary while clearing only candidate/result rows.
- Added static/fake-runner tests proving per-target sequence isolation,
  cross-target rejection, stale predecessor conflicts, BigQuery SQL ownership,
  and same-run retry behavior.

The BigQuery transaction/query shape follows current Google Developer
Knowledge MCP documentation: BigQuery multi-statement transactions provide
atomic commit/rollback and snapshot isolation; conflicting mutating
transactions are cancelled; `@@row_count` exposes the preceding DML result.

- [BigQuery multi-statement transactions](https://docs.cloud.google.com/bigquery/docs/transactions)
- [BigQuery system variables](https://docs.cloud.google.com/bigquery/docs/reference/system-variables)

## Evidence

### Static checks

Passed after staging all new files:

```text
uv run pre-commit run --all-files
Ruff, Ruff format, Pyright and dbt-parse: Passed

uv run ruff check scripts/serving tests/serving
All checks passed

uv run ruff format --check scripts/serving tests/serving
23 files already formatted

uv run pytest -q \
  tests/serving/test_control_domain.py \
  tests/serving/test_bigquery_control.py \
  tests/serving/test_bigquery_control_contract.py \
  tests/serving/test_control.py
14 passed
```

`uv lock --check` and the repository pre-commit dbt parse hook also passed.

### Full local acceptance

Evidence:

- Run ID: `wp2-local-acceptance-r2`
- Report: `data/acceptance/local-cdc/wp2-local-acceptance-r2/report.md`
- Compose project: `olist_local_cdc_acceptance`
- Result: `11/11` mandatory gates passed
- Started: `2026-08-07T02:28:10.237107+00:00`
- Finished: `2026-08-07T02:44:42.717663+00:00`

The clean-domain run passed bootstrap, snapshot, CRUD/restart, catch-up,
serving sync, dbt/stable views, additive schema evolution, rebuild and final
consistency checks. The project-scoped containers and volumes were removed
after the run.

The first attempt, `wp2-local-acceptance-r1`, stopped at the serving static
validation gate because newly created untracked tests had not been included
in the first pre-commit invocation. Ruff fixed the imports/formatting; the
staged rerun above passed the same validation and all runtime gates.

## Remaining checks

1. Execute the migration and repository adapter against a real BigQuery
   project and validate named query parameter typing with the chosen client
   wrapper.
2. Validate BigQuery dataset/table IAM and migration-ledger permissions after
   WP3 Terraform creates the project resources.
3. Integrate the GCP adapter with the GCP serving DAG, boundary planner and
   atomic publication procedure in later work packages.
4. Run cloud acceptance and parity checks against real BigQuery/Lakehouse data.

No GCP credentials, resources, BigQuery job, or Terraform apply was used for
this package.
