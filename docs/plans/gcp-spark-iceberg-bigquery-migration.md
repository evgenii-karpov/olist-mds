# Future GCP program: Spark, Iceberg and BigQuery

## Status

Future program, outside the local Stage L scope. This document deliberately
contains no implementation phases or GCP Definition of Done for the local
MySQL/Spark/Iceberg migration. The local candidate must first pass its own
clean-reset E2E and final parity gate.

## Fixed portability boundary

The future GCP program preserves business grains, metric definitions, the
versioned entity contracts, the small fixture, and the canonical parity
format. It does not reuse local infrastructure manifests or the ClickHouse dbt
project.

The target program must:

1. Select a Spark-writable Iceberg REST catalog supported on GCP.
2. Store Iceberg data and streaming checkpoints in physically separate GCS
   locations.
3. Replace MinIO-specific S3 settings with GCS-native credentials and I/O.
4. Create a separate `dbt-bigquery` project with no adapter branches shared
   with `dbt/olist_clickhouse`.
5. Define an explicit finite serving/publication boundary for BigQuery.
6. Run a separate local-versus-GCP row-level parity program.

Spark must not write into BigQuery-managed Iceberg tables. Catalog ownership,
table ownership, credential vending, maintenance, disaster recovery, cost
controls, and regional placement require fresh GCP architecture decisions and
are intentionally not inferred from the local Polaris/MinIO topology.

## Inputs required before planning

- a passing local MySQL-to-Iceberg candidate report;
- a passing legacy-versus-local final parity report;
- measured Bronze/Silver volume, file-size, snapshot, and checkpoint profiles;
- selected GCP region and organization/IAM constraints;
- selected Spark runtime and catalog compatibility matrix;
- BigQuery freshness, cost, and recovery objectives.

## References

- <https://docs.cloud.google.com/lakehouse/docs/use-lakehouse-metastore-iceberg-rest-catalog>
- <https://docs.cloud.google.com/bigquery/docs/biglake-iceberg-tables-in-bigquery>
