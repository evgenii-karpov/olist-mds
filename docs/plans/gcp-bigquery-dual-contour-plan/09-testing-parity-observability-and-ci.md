# Testing, Parity, Observability, CI, and Cost Evidence

## 1. Test layers

### Unit and contract tests

- binlog parsing and ordering-category requirements;
- canonical tuple generation in Scala/Python/SQL;
- boundary planner and transaction completeness;
- same-run retry and stale-run conflict state transitions;
- impacted-key/grain propagation;
- model delete/SCD2/aggregate mutation planning;
- configuration alias compatibility.

### Local integration

Preserve the existing local runtime and acceptance jobs. They remain mandatory after every structural refactor.

### Manual GCP integration

Run locally with real GCP credentials for:

- Terraform apply/destroy;
- vertical slice;
- full lakehouse load;
- restart from checkpoints;
- dbt build/test;
- publication failure/idempotency/conflict tests;
- parity and cleanup.

## 2. Cross-contour parity

A single CLI workflow:

1. establishes one deterministic source fixture and frozen source boundary;
2. runs the local contour to publication;
3. resets/replays the same source fixture and runs the GCP contour to publication;
4. extracts normalized model results;
5. compares row counts, keys, nulls, all business fields, aggregates, and checksums;
6. allows only explicitly documented representation differences;
7. emits JSON and Markdown reports.

Parity runs sequentially because contours do not operate concurrently.

## 3. Parity scope

- Bronze transport identity and offsets;
- Silver append-only changes and derived current state;
- reference data;
- transaction boundary and applied interval;
- Gold dimensions, facts, marts, SCD2 boundaries, deletes, and aggregates;
- ordering under multiple events for the same key;
- timestamps normalized to UTC;
- `NUMERIC`/`BIGNUMERIC` tolerance rules where representation differs.

Parity is an acceptance command, not a gate on every ordinary GCP serving run.

## 4. CI

Credential-free CI performs:

- existing local tests and runtime/static checks;
- Compose config rendering for `core + lakehouse-local` and `core + lakehouse-gcp`;
- verification that profile inventories do not leak forbidden services/secrets;
- Scala/Spark build and tests using the common image/dependency lock;
- Terraform `fmt`, `init -backend=false`, `validate`, and optional lint/security checks;
- `.terraform.lock.hcl` consistency;
- DAG import tests;
- SQL migration ordering/checksum/static validation;
- `dbt-bigquery parse` only.

Do not run `dbt compile` if it requires BigQuery catalog access. Do not provision cloud resources from CI in this phase.

## 5. Observability

Reuse the existing Prometheus/Grafana stack. Do not add Cloud Monitoring dashboards as a separate system.

Required metrics/events:

- per-query Kafka current/target offsets and lag;
- last completed source transaction/boundary;
- `audit.silver_progress` catch-up state;
- Spark batch duration, input rows, commit/restart failures;
- serving-run status and active `sync_run_seq`;
- per-model dbt duration/row counts/test result;
- publication duration, idempotent success, and conflict count;
- BigQuery processed/billed bytes and `maximum_bytes_billed` rejection;
- BigLake/GCS auth, catalog, checkpoint, and commit errors.

Every structured event carries contour, query/run/model identifiers, source boundary, and relevant GCP job IDs.

## 6. Cost evidence

For every vertical-slice, serving, and parity run record:

- BigQuery job labels;
- bytes processed and billed;
- GCS object counts/bytes;
- catalog/dataset inventory;
- remaining Free Trial credit/time as manually observed where API exposure is insufficient;
- cleanup verification.

Budget alerts are warning signals only and cannot guarantee zero spend. The zero-spend guarantee depends on remaining on Free Trial, query caps, small fixtures, and timely deletion.
