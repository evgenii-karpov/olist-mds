# GCP/BigQuery dual-contour runbook

This runbook describes the intended operator workflow for the `dev` GCP
contour. It does not authorize cloud mutation. Until a real project,
credentials, and an operator-approved run are available, `scripts/lab.py`
fails closed and only produces static plans/reports.

## Ownership and invariants

- The local and GCP contours are mutually exclusive lakehouse targets.
- `lab.py gcp up` starts `core + lakehouse-gcp` but does not start streaming.
- Long-lived Spark streaming remains owned by the explicit
  `gcp streaming start|stop` commands, never by Airflow.
- Spark owns Bronze/Silver/Reference/Audit Iceberg schemas and writes.
- BigQuery bridge views are read-only; SQL migrations own BigQuery application
  schemas.
- One GCP serving run owns one frozen transaction-complete boundary and one
  BigQuery publication transaction.
- The Terraform state bucket is a separate bootstrap resource and is not part
  of the main destroy scope.

## Prerequisites

The cloud operator must have, outside Git:

1. a dedicated project and billing account that remains on Free Trial; never
   activate paid billing;
2. a separately bootstrapped GCS Terraform state bucket;
3. `gcloud` ADC or role-specific impersonated ADC files for Spark, dbt, and
   Airflow;
4. Terraform with the repository Google provider lock (`7.43.0`), Docker, and
   the pinned project dependencies.

Relevant environment values are `GCP_PROJECT_ID`, `GCP_REGION`,
`GCP_LAKEHOUSE_CATALOG_ID`, `GCP_SPARK_ADC_SOURCE_FILE`,
`GCP_DBT_ADC_SOURCE_FILE`, `GCP_AIRFLOW_ADC_SOURCE_FILE`,
`GCP_DBT_PROJECT_HOST_PATH`, and `GCP_BIGQUERY_MAX_BYTES_BILLED`.

ADC files, billing identifiers, Terraform variable files, and service-account
keys must not be committed. Long-lived service-account keys are not part of
the design.

## Preview constraints and tested versions

The Lakehouse runtime catalog/Iceberg REST catalog path must be treated as a
version-sensitive Google Cloud surface. Before a cloud run, record the
operator's checked documentation revision and confirm the target region and
project are supported. The implementation intentionally keeps Spark as the
owner of the catalog-managed Iceberg tables; BigQuery bridge views and the
application SQL migrations remain separate.

The following documented constraints affect this design:

- Iceberg V1 tables are not supported by the Lakehouse catalog path. This
  repository targets the current Iceberg V2-compatible runtime and does not
  claim V3/Preview compatibility.
- BigQuery DDL/DML is not the mutation path for tables exposed through the
  Iceberg REST catalog. Do not use it to bypass Spark ownership or the
  catalog's external-engine compatibility rules.
- Fine-grained row-level and column-level access controls are not available
  for tables managed through the REST catalog endpoint. Treat this as an
  architectural limitation, not an IAM misconfiguration.
- BigQuery reads can have different performance and dry-run byte estimates
  from native BigQuery tables. Use completed job statistics and the configured
  `maximum_bytes_billed` cap as the cost evidence.
- Catalog, automatic table-management, and related federation capabilities
  can be Preview/Pre-GA. A successful static parse or Terraform validation is
  not evidence that the selected Preview feature is enabled or available in
  the target project.

The exact versions checked for this repository on 2026-08-07 are:

| Component | Version | Evidence |
| --- | --- | --- |
| Python | 3.12.13 | local interpreter |
| Apache Airflow | 3.2.1 | `pyproject.toml`/local import |
| dbt Core | 1.11.8 | local import |
| dbt BigQuery adapter | 1.11.3 | `pyproject.toml`/dbt parse |
| BigQuery Python client | 3.43.0 | `pyproject.toml` |
| Spark | 4.1.3 | Spark image/Dockerfile |
| Iceberg runtime label | 1.11.0 | Spark image label |
| Hadoop | 3.4.2 | Spark Dockerfile |
| GCS connector | 2.2.31 | Spark Dockerfile |
| Terraform | 1.15.8 | local binary |
| Google Terraform provider | 7.43.0 | `.terraform.lock.hcl` and provider docs |

Documentation basis: [Lakehouse runtime catalog](https://cloud.google.com/bigquery/docs/lakehouse-runtime-catalog), [Iceberg REST catalog endpoint](https://cloud.google.com/bigquery/docs/iceberg-rest-catalog-endpoint), [BigQuery Iceberg ingestion](https://cloud.google.com/bigquery/docs/iceberg-ingestion), and [BigLake catalog concepts](https://cloud.google.com/lakehouse/docs/about-lakehouse-catalogs).

## Bootstrap and first run

Run the following sequence only after the operator has approved the project,
Free Trial billing, and resource budget:

```text
uv run python scripts/lab.py doctor
uv run python scripts/lab.py gcp preflight
uv run python scripts/lab.py gcp terraform init --backend-config=...
uv run python scripts/lab.py gcp terraform validate
uv run python scripts/lab.py gcp terraform plan --var-file=...
uv run python scripts/lab.py gcp terraform apply --yes --var-file=...
uv run python scripts/lab.py gcp migrate render --project-id ... --catalog-id ...
uv run python scripts/lab.py gcp migrate apply --project-id ... --catalog-id ...
uv run python scripts/lab.py gcp up --build
uv run python scripts/lab.py gcp streaming start --build
uv run python scripts/lab.py gcp vertical-slice run --project-id ... --catalog-id ...
uv run python scripts/lab.py parity run --local-evidence ... --gcp-evidence ...
```

The vertical-slice report must produce `GO` or `GO-WITH-CONSTRAINTS` before
the full GCP lakehouse load is considered eligible. A static
`PENDING_GCP_ACCESS` report is not a cloud decision.

## Daily serving run

1. Run `gcp preflight` and inspect the recorded billing/cost evidence scope.
2. Verify that only one lakehouse profile is active.
3. Verify Spark Silver progress reaches the frozen transaction boundary.
4. Run `gcp serving run [--sync-run-seq N]` through the target Linux Airflow
   environment, or trigger the `olist_gcp_serving` DAG manually there.
5. Inspect the lease, boundary, candidate model/entity results, publication
   pointer, and BigQuery job labels/bytes.
6. Store the bounded parity/cost/metrics evidence and emit a Markdown report.

The DAG is finite. It acquires a lease, freezes a boundary, waits for
progress, builds the dbt candidate, records results, calls the atomic
publication procedure, emits evidence, and releases the lease on all task
outcomes.

## Retry, conflict, and recovery

- A failed unpublished sequence may be retried with the same
  `sync_run_seq`; candidate history for that sequence must be cleaned before
  rebuilding.
- A stale predecessor or compare-and-set mismatch is a conflict. Do not
  overwrite the active sequence; inspect the control ledger and create a new
  compensating run when a published correction is required.
- A mid-publication failure must leave current tables, publication pointers,
  and active state unchanged except for the explicitly recorded conflict row.
- Container, dbt, BigQuery, and publication failures require checking the
  Airflow task log and the GCP metric/event evidence before retrying.

## Reset and destroy

Both operations are destructive and require `--force`:

```text
uv run python scripts/lab.py gcp inventory
uv run python scripts/lab.py gcp reset-data --force
uv run python scripts/lab.py gcp destroy --force
```

Before a real mutation, the operator must record project ID, active serving
run/lease, streaming state, buckets, datasets, catalog resources, and exact
scope. `reset-data` clears application data and checkpoints through
catalog-aware operations. `destroy` stops streaming, verifies no active
serving transaction, destroys Terraform-managed resources, and verifies that
the main-contour resources are gone. The separately bootstrapped state bucket
remains until a separate manual cleanup decision.

The current credential-free implementation intentionally reports these
commands as blocked; it does not simulate deletion locally.

## Troubleshooting

| Symptom | First checks | Safe response |
| --- | --- | --- |
| Preflight blocked | project, region, ADC path, `gcloud`, Terraform | fix local prerequisites; do not bypass preflight for cloud mutation |
| Vertical slice has no decision | direct P.C.N.T. reads, bridge reads, types, restart evidence | stop before WP6/full port and diagnose the actual cloud failure |
| Silver boundary is waiting | `audit.silver_progress`, Kafka offsets, transaction metadata | keep serving blocked until the complete prefix is visible |
| dbt candidate failed | bounded container logs, run artifacts, model result rows | retry same sequence only after candidate cleanup |
| publication conflict | active sequence, predecessor, CAS result, conflict row | do not force pointer updates; create a compensating run if needed |
| bytes cap rejected a query | job labels, processed/billed bytes, configured cap | reduce fixture/query scope or explicitly revise the approved cap |
| BigLake/GCS error | ADC role, catalog endpoint, checkpoint bucket, commit error metrics | stop streaming and preserve evidence before changing IAM/config |

## No-go process

If the vertical slice returns `NO-GO`, stop the dependent full lakehouse work.
Record the exact failing table, query, schema/type result, restart behavior,
cost evidence, and environment versions. Revisit the decision register and
redesign the failed boundary only after the failure is understood; this
runbook does not prescribe a fallback technology.

## Credential-free verification available now

```text
uv run dbt parse --project-dir dbt/olist_bigquery --profiles-dir dbt/olist_bigquery --no-partial-parse
uv run python scripts/lab.py gcp migrate status
uv run python scripts/lab.py parity run
uv run python scripts/lab.py gcp cost report
uv run python scripts/lab.py gcp serving run
uv run python scripts/lab.py gcp inventory
uv run python scripts/lab.py gcp reset-data
uv run python scripts/lab.py gcp destroy
docker compose --profile core --profile lakehouse-gcp config --quiet
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
uv run python scripts/ci/validate_observability_contract.py
```

The expected result for parity/cost commands without cloud evidence is
`BLOCKED/PENDING_GCP_ACCESS`. Existing stage reports are under
`docs/reports/gcp-bigquery-dual-contour/`; they distinguish static evidence
from cloud closeout requirements.
