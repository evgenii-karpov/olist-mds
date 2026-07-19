# CI Quality Gates

The GitHub Actions workflow is split into focused jobs so a failing check points
to a useful layer instead of one opaque pipeline failure.

CI intentionally runs only the local PostgreSQL execution path. The AWS/S3/
Redshift path is available for manual validation, but pull-request checks stay
local so they remain reproducible, self-contained, and independent of cloud
credentials or infrastructure availability.

## Workflow

```text
lint
  -> Ruff, SQLFluff, and pre-commit checks.

python-unit
  -> Python syntax, source-contract fixture validation, unit tests,
     and targeted negative data-quality tests.

dbt-static
  -> dbt parse without a warehouse connection.

airflow-imports
  -> Docker Compose validation, Airflow image build, metadata database startup,
     and isolated DAG imports.

cdc-stage1-oltp-simulator
  -> CDC implementation Stage 1: starts the isolated OLTP PostgreSQL source and
     validates deterministic seed, lifecycle, replay, and stop behavior.

cdc-stage2-kafka-debezium
  -> Manual-only CDC implementation Stage 2: validates Kafka topics, Apicurio
     compatibility, Debezium snapshot/CRUD semantics, and connector restart
     recovery.

batch-fixture-idempotency
  -> Small fixture end-to-end path through the local Airflow DAG, PostgreSQL,
     reconciliation, dbt snapshots/build/tests, batch-control checks, raw file
     comparison, and incremental replay idempotency.

cdc-stage4-warehouse-ingest
  -> Builds isolated MinIO/PostgreSQL state and verifies normalized loading,
     tombstone coverage, gap closure, transient retry, reconciliation, and
     duplicate-only replay in a disposable database and bucket.

cdc-stage5-realtime-dbt
  -> Builds three exact-manifest dbt micro-batches in a disposable PostgreSQL
     database and verifies source ordering, complete update history, late event
     handling, impacted-key rebuilds, hard-delete propagation to facts/marts,
     and reversible realtime-to-batch publication.

dbt-selector-boundaries
  -> Resolves all named selectors with `dbt ls`, restricts batch to project
     batch resources plus the required Elementary observability package,
     rejects realtime resources in batch, restricts cross-group refs to
     `models/parity`, and rejects unbounded `dbt build` commands in DAGs and CI
     workflows.

python-unit / CDC Stage 6 observability contract
  -> Validates real Loki/Alloy services, six dashboard domains, the complete
     alert inventory, runbook links, retention, and low-cardinality log labels.
     Destructive or long-running fault/benchmark execution remains manual or
     nightly through `failure_injection.py` and `benchmark_local.py`.
```

The regular `CI` workflow runs on pull requests and pushes to `main`/`master`.

## Small Fixture Dataset

The committed fixture lives in `tests/fixtures/olist_small`.

It contains:

- `olist_small.zip`, with the original Olist file names and headers.
- `source_profile_small.json`, the matching source contract.
- `source/`, reviewable uncompressed CSVs.

The fixture is synthetic, small, and referentially consistent. It exercises real
joins, correction feed generation, reconciliation, dbt snapshots, core models,
marts, and tests without requiring the full Kaggle archive in CI.

CI uses `DEFAULT_FIXTURE_BATCH_DATE` (`2018-09-01`) as the default fixture
batch date. This date is intentionally after all generated customer/product
correction `effective_at` values, so one fixture run sees the complete
synthetic SCD2 scenario instead of needing a multi-batch backfill sequence.

## What CI Tests

Happy path:

- source contract validation against the small fixture archive;
- raw file preparation with row-level validation;
- generated correction feeds;
- PostgreSQL raw load;
- batch control state transitions;
- source-to-raw reconciliation;
- dbt staging and intermediate build;
- dbt snapshots;
- dbt core and mart build;
- dbt tests.
- incremental replay of the same fixture batch through Airflow with stable raw
  file and analytical output fingerprints.

Failure modes:

- source contract failure when a required column is missing;
- corrupt source row being routed to the dead-letter path;
- dead-letter threshold failure;
- reconciliation gate failure.

The full `olist.zip` run remains a local/manual validation path. Use the
[Windows runbook](runbook_windows.md) or [macOS runbook](runbook_macos.md) for
the concrete local commands.
