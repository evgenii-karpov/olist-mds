# WP12 — Documentation, Operations, and Final Acceptance

Date: 2026-08-07; Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free implementation is complete; WP12 is not fully closed.**

The operator-facing GCP/BigQuery runbook and the remaining normative GCP
command surface are now present. The CLI fails closed for serving execution,
inventory, reset, and destroy when no real GCP project and credentials are
available. Final cloud acceptance, parity, recovery, and residual-resource
verification remain explicitly pending rather than being represented by local
simulation.

## Implemented

- Added [`docs/runbooks/gcp-bigquery-dual-contour.md`](../../runbooks/gcp-bigquery-dual-contour.md)
  covering:
  - contour ownership and invariants;
  - prerequisites, credential handling, and bootstrap order;
  - daily serving operation and finite Airflow ownership;
  - same-sequence retry, stale-run conflict, atomic-publication failure, and
    compensating-run recovery guidance;
  - reset/destroy scope with the Terraform state-bucket exception;
  - troubleshooting and the no-go redesign process;
  - credential-free verification commands;
  - Preview/Pre-GA caveats and exact repository/tool versions checked on the
    report date.
- Added `gcp serving run [--sync-run-seq N]`, `gcp inventory`,
  `gcp reset-data --force`, and `gcp destroy --force` to `scripts/lab.py`.
  These commands validate local arguments and emit bounded JSON status, but
  do not perform cloud mutation or pretend that a blocked operation passed.
- Added parser and fail-closed command tests in
  `tests/orchestration/test_lab_cli.py`.

## Static evidence

The following checks are intended for the WP12 commit and contain no GCP
credentials or cloud calls:

```text
uv run ruff check scripts/lab.py tests/orchestration/test_lab_cli.py
All checks passed!

uv run pyright scripts/lab.py tests/orchestration/test_lab_cli.py
0 errors, 0 warnings, 0 informations

uv run pytest tests/orchestration/test_lab_cli.py -q
6 passed, 1 Windows pytest-cache warning

uv run pytest tests -q
352 passed, 3 skipped, 2 warnings, 86 subtests passed

uv run dbt parse --project-dir dbt/olist_bigquery \
  --profiles-dir dbt/olist_bigquery --no-partial-parse
dbt=1.11.8; adapter bigquery=1.11.3; parse passed

docker compose --profile core --profile lakehouse-gcp config --format json
GCP_COMPOSE_CONFIG_OK

terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
Success; Google provider 7.43.0 reused; no backend or cloud credentials used

uv run python scripts/ci/validate_observability_contract.py
18 scrape jobs, 23 alerts, 6 dashboards; valid

uv run python scripts/lab.py gcp migrate status
5 ordered migrations; status=ready; cloud_execution=NOT_RUN

uv run python scripts/lab.py parity run --output data/acceptance/gcp/wp12-parity-pending
status=blocked; parity_status=BLOCKED; cloud_execution=PENDING_GCP_ACCESS

uv run python scripts/lab.py gcp cost report --output data/acceptance/gcp/wp12-cost-pending
status=blocked; evidence_status=BLOCKED; cloud_execution=PENDING_GCP_ACCESS

uv run python scripts/lab.py gcp serving run --sync-run-seq 7
status=blocked; dag_id=olist_gcp_serving; cloud_execution=PENDING_GCP_ACCESS

uv run python scripts/lab.py gcp inventory
status=blocked; cloud_execution=PENDING_GCP_ACCESS

uv run python scripts/lab.py gcp reset-data [--force]
uv run python scripts/lab.py gcp destroy [--force]
status=blocked; --force is required, and real mutation remains PENDING_GCP_ACCESS

pre-commit run --all-files
All hooks passed via `uv run pre-commit run --all-files`.
```

The latest existing local Docker acceptance evidence is
`data/acceptance/local-cdc/wp4-local-acceptance-r1/report.md`: it passed all
11/11 mandatory gates on 2026-08-07. Subsequent changes in this plan were
GCP contour, reporting, documentation, or CLI changes; the full test suite
and current Compose configuration checks above were rerun after them.

The existing Windows Airflow POSIX-runtime warning and pytest cache-directory
permission warning are expected. Standard `DagBag` import is performed in a
Linux Airflow environment or through the repository's Windows-safe
direct-import contract checks. Pre-commit passed on the staged WP12 files.

## Cloud-gated evidence still required

These items cannot be closed without an operator-approved GCP project,
credentials, and a real run:

1. GCP vertical-slice acceptance, including P.C.N.T. reads, bridge reads,
   restart/checkpoint behavior, type assertions, and the explicit GO or
   GO-WITH-CONSTRAINTS decision.
2. Final local/GCP sequential parity over every Gold model, including deletes,
   SCD2 intervals, aggregates, nulls, and normalized checksums.
3. Same-run retry, stale-ready conflict, mid-publication failure injection,
   and compensating-run recovery against the real BigQuery control tables.
4. Actual Airflow/Spark/dbt/BigQuery metrics and bounded job/cost evidence,
   including processed/billed bytes and cap-rejection behavior.
5. `gcp inventory`, `gcp reset-data --force`, and `gcp destroy --force` in the
   target project, followed by proof that managed resources are absent while
   the separately bootstrapped Terraform state bucket remains.
6. Final Free Trial/billing observation and zero-spend evidence.

Until those checks are recorded, WP12 and the overall plan remain partially
complete even though the cloud-independent implementation and documentation
are complete.

## Documentation basis

The Preview/capability notes in the runbook were checked against Google
Developer Knowledge MCP documentation for the [Lakehouse runtime catalog](https://cloud.google.com/bigquery/docs/lakehouse-runtime-catalog),
the [Iceberg REST catalog endpoint](https://cloud.google.com/bigquery/docs/iceberg-rest-catalog-endpoint),
[Iceberg ingestion](https://cloud.google.com/bigquery/docs/iceberg-ingestion),
and [Lakehouse catalog concepts](https://cloud.google.com/lakehouse/docs/about-lakehouse-catalogs).
The locked Google Terraform provider version and dataset/resource semantics
were checked against the Terraform MCP provider documentation for Google
provider 7.43.0. No Terraform plan/apply/destroy operation was requested or
run.
