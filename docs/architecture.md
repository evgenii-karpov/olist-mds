# Architecture

## Goal

Provide a production-like analytics pipeline that can be run and reviewed
locally, with a separate AWS batch path. The batch workflow uses Python, local
files, ClickHouse, Airflow, PostgreSQL control state, and dbt; the AWS workflow
stages raw files in S3 and loads Redshift. The candidate CDC architecture uses
MySQL, Kafka/Apicurio, Spark, Iceberg, MinIO, and Polaris. Wave 1 freezes the
platform contracts and integration seams; entity Silver transforms and serving
publication are later join points.

## Wave 1 CDC boundary

```text
MySQL OLTP
  -> Debezium MySQL / Kafka Connect
  -> Kafka (15 exact topics) + Apicurio (Confluent-framed Avro)
  -> Spark/Iceberg through Polaris REST Catalog
  -> Bronze/Silver/audit Iceberg tables on MinIO
```

MySQL is the authoritative business source. PostgreSQL is limited to the
Airflow, Polaris, Apicurio, and `olist_control` control-plane databases. The
single `scripts/cdc/local_lab.py` CLI owns the disposable Compose project and
returns bounded JSON results. `reset --yes` removes only that Compose project's
volumes; `down` preserves them.

The common normalization API in `streaming/spark/platform/normalization_api.py`
freezes event identity, captured writer fingerprints, schema resolution,
changes append, current MERGE, audit/error, ordering, deduplication, and
checkpoint boundaries. It contains no entity business transforms.

## Legacy near-realtime transformation boundary

The local CDC ingest Asset triggers `olist_cdc_transform_local`. Before dbt
runs, the DAG records the exact set of newly loaded immutable manifests in
`cdc_audit.cdc_transform_run_files`. The set is stable across retries. After
focused dbt build/tests succeed, the DAG records mart freshness and commits the
transform run; failed builds never consume manifests.

The hourly `olist_cdc_quality_local` DAG checks offset continuity,
reconciliation, freshness, and realtime model integrity. Its midnight logical
run additionally executes the full realtime test suite and Elementary. Batch
DAGs and schemas remain independent.

Batch and realtime transformations stay in one dbt project so they can share
portable business macros. dbt groups and named selectors enforce the runtime
boundary: batch DAGs use `batch`, CDC builds use `realtime_transform`, hourly
checks use `realtime_quality`, and comparisons use `realtime_parity`. The only
cross-group refs live in `models/parity`; unrestricted `dbt build` is not an
orchestration entrypoint.

The operational `batch` selector also includes the Elementary package models.
They provision the observability schema required by Elementary's dbt hooks and
the subsequent `edr report`, including on a clean warehouse. The selector
boundary check rejects every other third-party package from `batch`.

## Flow

```text
Source archive
  -> source-contract validation
  -> row-level validation
  -> raw and dead-letter files
  -> ClickHouse or Redshift raw tables
  -> reconciliation
  -> dbt transformations and tests
  -> analytical marts
```

Airflow coordinates both paths. Local batch and CDC control state is durable in
PostgreSQL `olist_control`, while local analytical data lives in ClickHouse.

The previous PostgreSQL/NiFi path remains available in the repository for later
parity work, but it is not selected by the Wave 1 `platform`, `streaming`, or
`serving` profiles and is not part of J1 readiness.

## Components

### Ingestion

The ingestion layer reads `olist.zip`, verifies the expected files and headers,
validates row-level warehouse compatibility, adds operational metadata, and
writes gzip CSV files into a deterministic raw-zone layout:

```text
data/raw/olist/raw/<entity>/batch_date=<YYYY-MM-DD>/run_id=<run_id>/<entity>.csv.gz
data/raw/olist/dead_letter/<entity>/batch_date=<YYYY-MM-DD>/run_id=<run_id>/<entity>.csv.gz
```

The same logical layout is used for both execution modes. The default local
workflow writes to the filesystem, and the AWS workflow uploads the prepared
artifacts to S3 under the same partitioning scheme.

### Warehouse

The project supports two analytical warehouse targets:

- ClickHouse for the default local workflow
- Redshift for the AWS workflow

Both targets use the same logical schemas:

```text
raw_data
staging
intermediate
snapshots
core
marts
```

Raw files are loaded into ClickHouse `raw_data` locally or Redshift `raw_data`
on AWS. Local `audit` and `cdc_audit` control schemas live in PostgreSQL
`olist_control`; ClickHouse stores analytical `cdc_audit` parity relations.

### Airflow

Airflow exposes batch DAGs for both execution modes:

- `olist_modern_data_stack_local` for filesystem raw files plus ClickHouse
- `olist_modern_data_stack_aws` for S3 raw files plus Redshift

Both DAGs follow the same high-level contracts:

```text
validate_source_contract
prepare_raw_files or upload_raw_files_to_s3
generate_correction_feeds
load_raw_files_to_clickhouse or load_raw_files_to_redshift
reconcile_raw_load
dbt_build
```

Airflow handles orchestration, retries, parameters, and failure callbacks. The
control database remains the durable source of batch status.

Local CDC is orchestrated by dedicated finite DAGs for ingest, replay,
transform, quality, and publication. Continuous services such as PostgreSQL
OLTP, Debezium/Kafka, Apicurio, MinIO, NiFi, and telemetry are managed by Docker
Compose rather than supervised by Airflow.

### dbt

dbt owns the analytical transformation layer:

```text
sources -> staging -> intermediate -> snapshots -> core -> marts
```

The modeling details, grain decisions, SCD2 strategy, and mart definitions live
in [data_model.md](data_model.md).

## Reliability Patterns

### Source Contract

Missing files, changed headers, and changed source row counts are structural
contract failures. They fail before raw loading starts.

The generated contract is documented in [source_contract.md](source_contract.md).

### Dead Letter Pattern

Record-level type and length failures are written to the dead-letter zone with
the source row number, failure stage, reason, and timestamp. A run continues
only while rejected rows remain within configured thresholds.

Corrected dead-letter files can be replayed into raw tables. Replays are
idempotent for a stable replay id and are recorded in
`audit.dead_letter_replays`.

### Batch Control

`audit.batch_runs` tracks each logical batch independently of Airflow task
history.

```text
STARTED
SOURCE_VALIDATED
RAW_PREPARED
RAW_LOADED
RAW_RECONCILED
DBT_BUILT
```

`FAILED` is allowed from any state. The helper script prevents accidental
backward transitions.

### Reconciliation

After raw loading, the pipeline compares source counts, prepared rows, valid raw
rows, dead-letter rows, replayed rows, and rows present in the active warehouse
for the batch.

Core checks:

```text
prepared_total_rows = expected_source_rows
prepared_valid_rows + dead_letter_rows = prepared_total_rows
raw_loaded_rows = prepared_valid_rows + replayed_rows
```

A mismatch fails the DAG before dbt builds snapshots, facts, or marts.

## Execution Modes

The local batch workflow is the default development entrypoint because it is
self-contained and easier to run in CI and on a laptop. The AWS batch workflow
is supported for manual runs with S3 and Redshift credentials. Both batch paths
share the same source contract, raw-zone partitioning, audit patterns, and dbt
models while varying only the storage and warehouse targets.

The local CDC workflow is a separate execution mode. It starts from the
PostgreSQL OLTP simulator, lands immutable CDC objects through Kafka and NiFi,
loads them into ClickHouse `raw_cdc`, and builds realtime dbt models that are
compared with batch outputs before publication.

CI intentionally stays local so checks remain reproducible, self-contained, and
independent of cloud credentials or infrastructure availability.
