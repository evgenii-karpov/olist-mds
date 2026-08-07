# WP11 — Parity, Observability, CI, and Cost Evidence

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free implementation is complete; WP11 is not fully closed.**

The repository now has a strict evidence comparator, JSON/Markdown parity
reports, a bounded cost-evidence schema, GCP Prometheus metric contracts, and
credential-free CI checks. No GCP credential, BigQuery job, billing API,
Spark run, or cloud resource was used. A real sequential local/GCP fixture is
still required for the stage's semantic parity and zero-spend evidence.

## Implemented

- Added `scripts/serving/parity.py` with:
  - explicit `local`/`gcp` evidence contours and frozen-boundary comparison;
  - strict model, primary-key, row-count, field, null, and checksum checks;
  - UTC timestamp, decimal numeric, and `base64:` binary normalization rules;
  - bounded hash-only differences so business row values are not copied into
    failure reports;
  - fail-closed `BLOCKED/PENDING_GCP_ACCESS` reports when GCP evidence is
    absent.
- Replaced the `lab.py parity` placeholder with `parity run` and
  `parity report`. `run` writes `parity.json` and `parity.md`; it never
  presents a static plan as a passing parity result.
- Added `scripts/gcp/cost_evidence.py` for BigQuery labels, processed/billed
  bytes, maximum-byte caps, GCS object/byte summaries, residual resources,
  cleanup status, and manually observed Free Trial state.
- Extended the BigQuery runtime to retain bounded `job_id`, labels, location,
  processed bytes, billed bytes, and cap evidence after a successful query.
- Added `scripts/observability/gcp_metrics.py` with bounded low-cardinality
  Prometheus rendering for Kafka/Silver boundary, Spark, dbt, publication,
  BigQuery cost, and BigLake error signals.
- Added GCP recording rules and six GCP serving panels to the existing
  Prometheus/Grafana stack. The renderer is transport-agnostic so local CI
  can validate it without adding a cloud dependency to the local contour.
- Added a `gcp-static-contract` GitHub Actions job. It runs dbt BigQuery
  parse, GCP migration/static tests, parity blocked-plan validation, GCP
  Compose rendering, Terraform `fmt`/`init -backend=false`/`validate`, and
  observability validation. It does not run Terraform plan/apply or use
  GCP credentials.

## Static evidence

```text
uv run pytest tests/gcp tests/infrastructure \
  tests/airflow/test_gcp_dag_contract.py \
  tests/orchestration/test_compose_render.py \
  tests/observability/test_gcp_metrics.py \
  tests/observability/test_ci_contract.py -q
60 passed, 2 warnings

uv run dbt parse --project-dir dbt/olist_bigquery \
  --profiles-dir dbt/olist_bigquery --no-partial-parse
dbt=1.11.8; adapter bigquery=1.11.3; parse passed

uv run python scripts/ci/validate_observability_contract.py
18 scrape jobs, 23 alerts, 6 dashboards; valid

uv run python scripts/lab.py gcp migrate status
5 ordered migrations; status=ready; cloud_execution=NOT_RUN

uv run python scripts/lab.py parity run --output <temporary-output>
status=blocked; parity_status=BLOCKED; cloud_execution=PENDING_GCP_ACCESS

docker compose --profile core --profile lakehouse-gcp config --format json
GCP_COMPOSE_CONFIG_OK

terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
Success; no backend or cloud credentials used
```

The only test warnings are the existing Windows Airflow POSIX-runtime warning
and pytest cache-directory permission warning.

## Documentation basis

The BigQuery runtime settings were checked against the Google Developer
Knowledge MCP documentation for [running query jobs](https://docs.cloud.google.com/bigquery/docs/running-jobs),
[job labels](https://docs.cloud.google.com/bigquery/docs/adding-labels), and
[cost controls](https://docs.cloud.google.com/bigquery/docs/best-practices-costs).
The Terraform static workflow keeps the existing locked Google provider
version and uses backend-disabled validation only.

## Required cloud closeout

Before WP11 can be marked fully complete, execute and record:

1. one deterministic local run and one sequential GCP run from the same
   frozen source boundary;
2. normalized evidence for all published Gold models, including keys, nulls,
   business fields, deletes, SCD2 intervals, aggregates, and checksums;
3. a strict parity `PASS` report, or explicit documented representation
   differences accepted by the decision register;
4. real Spark/dbt/Airflow/BigQuery metric emission, including job IDs in
   structured events and low-cardinality Prometheus labels;
5. BigQuery processed/billed bytes, cap rejection behavior, GCS object
   inventory, residual-resource inventory, cleanup result, and manual
   Free Trial/billing observation;
6. evidence that the GCP run and parity workflow use no concurrent local/GCP
   lakehouse profiles and that actual observed monetary spend is zero.

No cloud execution ID or billing observation exists yet because GCP access was
intentionally unavailable.
