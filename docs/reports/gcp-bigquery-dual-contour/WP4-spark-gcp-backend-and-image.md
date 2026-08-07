# WP4 — Spark GCP Backend and Common Image Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free implementation and local acceptance are complete. Cloud
completion remains pending a real GCP project, ADC and BigLake access.**

The local contour was verified with the same image that contains the GCP
catalog and GCS connector path. The following cloud-only acceptance items are
not claimed as complete until they are run in GCP:

- creating a GCP namespace and Iceberg test table through the REST catalog;
- writing and reading a real GCS checkpoint;
- validating credential vending and IAM with the provisioned service accounts.

## Implemented

- Added a validated Python backend abstraction selected by `SPARK_BACKEND`
  (`local` or `gcp`). The legacy `SPARK_CONTOUR` and
  `ICEBERG_CATALOG_NAME` variables remain compatible; the explicit
  `ICEBERG_SPARK_CATALOG_ALIAS` takes precedence.
- Added GCP REST catalog properties for the BigLake endpoint, `bl://`/`gs://`
  warehouse, `GoogleAuthManager`, vended credentials and
  `x-goog-user-project` billing attribution.
- Added GCP `GCSFileIO`, `GoogleHadoopFileSystem`,
  `GoogleHadoopFS`, `APPLICATION_DEFAULT` authentication and HTTP API client
  configuration for isolated `gs://` checkpoints. GCP configuration rejects
  local Polaris/S3A credentials and requires a mounted regular ADC file.
- Propagated the resolved catalog alias through migrations, writers and
  operational Spark applications instead of embedding `lakehouse` table paths
  in active GCP code.
- Added dedicated `lakehouse-gcp` and `streaming-gcp` Compose services. Their
  ADC source defaults to the ignored host path
  `.gcp/credentials/spark-adc.json`; no credential is generated locally.
- Added the GCP artifacts to the common image with checksummed Maven URLs:
  `iceberg-gcp-bundle` `1.11.0` and shaded GCS connector `2.2.31`. The image
  now performs runtime version checks and a single-owner classpath scan for
  Google auth, GCS, Protobuf, Guava, Jackson, HTTP, Hadoop and Iceberg GCP
  classes.

The implementation follows the Google Developer Knowledge MCP documentation:

- [Set up a Lakehouse Iceberg REST catalog](https://docs.cloud.google.com/lakehouse/docs/set-up-lakehouse-iceberg-rest-catalog)
- [Query Iceberg tables with Lakehouse](https://docs.cloud.google.com/lakehouse/docs/query-iceberg-tables-with-lakehouse)
- [Cloud Storage connector for Managed Service for Apache Spark](https://docs.cloud.google.com/managed-spark/docs/concepts/connectors/cloud-storage)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc)

## Evidence

All checks below were run without GCP credentials or cloud API calls.

```text
docker build --file docker/spark/Dockerfile --tag olist-spark:wp4-gcp --progress=plain .
PASS: Spark 4.1.3 / Scala 2.13 / Hadoop 3.4.2 image
PASS: scalafmtCheckAll, scalafmtSbtCheck, Scala compile, 10 Scala tests, package
PASS: runtime artifact and classpath verifier during image build
Image digest: sha256:db3e239a75cad8e7eaf14aeb6a604efa1289170565fd46af7a8b11d2635e8be7

docker run --rm --entrypoint /usr/local/bin/verify-olist-spark-runtime olist-spark:wp4-gcp
PASS

docker run --rm --entrypoint /usr/local/bin/verify-olist-spark-classpath olist-spark:wp4-gcp
PASS

uv run pre-commit run --all-files
Ruff, Ruff format, Pyright and dbt-parse: Passed

uv run pytest -q tests/lakehouse_platform tests/orchestration
66 passed, 1 skipped

docker compose --profile core --profile lakehouse-gcp config --format json
PASS

Full local acceptance with the same image tag:
Run ID: wp4-local-acceptance-r1
Mandatory gates: 11/11 PASS
Evidence: data/acceptance/local-cdc/wp4-local-acceptance-r1/
Project cleanup: PASS; acceptance volumes explicitly removed with
docker compose --project-name olist_local_cdc_acceptance ... down -v
```

The raw acceptance directory is local evidence and remains ignored by the
repository. This report is the committed operator-facing record; the cloud
namespace/checkpoint run must be appended after a real GCP execution.

## Reproduction identifiers

- Spark base: `apache/spark:4.1.3-scala2.13-java17-python3-ubuntu`
- Iceberg runtime/bundles: `1.11.0`
- Hadoop: `3.4.2`
- GCS connector: `hadoop3-2.2.31-shaded`
- New JAR SHA-256 values are committed in `docker/spark/jars.sha256`:
  - Iceberg GCP bundle:
    `d9248fc76d94d232e153bf760631229cd3b7c6bc3b20f47d4b2caffe011a8a2f`
  - GCS connector:
    `f640c555676cc8c15ba92775a9cfc6437b6a7fbbeab37fc763d170272ee7c921`

## Rollback

The GCP contour is isolated behind Compose profiles and `SPARK_BACKEND=gcp`.
The local contour continues to use Polaris/S3A properties. Removing the WP4
commit restores the previous local-only image and configuration without
changing persistent local schema or ordering contracts.
