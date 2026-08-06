# Spark, Iceberg, and the Blocking Vertical Slice

## 1. Shared Spark implementation

The Spark codebase remains common. Introduce a backend configuration abstraction containing:

- catalog implementation and REST URI;
- warehouse identifier;
- FileIO implementation;
- REST authentication and credential-vending headers;
- checkpoint base URI;
- contour/query ID;
- credentials location;
- backend-specific Spark/Hadoop options.

Do not duplicate entity transformations or table specifications.

## 2. Runtime dependencies

The common Spark image includes:

- existing Spark/Scala/Iceberg dependencies for the local path;
- Iceberg GCP bundle for `GCSFileIO` and Google auth integration;
- a Hadoop GCS connector compatible with the exact Spark/Hadoop base image for `gs://` checkpoints.

Rules:

- pin versions and SHA-256 checksums;
- fetch/build dependencies during image build;
- reject runtime package resolution;
- add classpath tests for duplicate/incompatible Guava, protobuf, Google auth, HTTP, Jackson, and Hadoop classes;
- prove local MinIO/Polaris behavior remains intact with the combined image.

## 3. Iceberg ownership

Terraform creates catalog/namespaces; Spark creates/evolves tables from repository table specs. Tables use Iceberg V2 and Parquet. Do not set custom data or metadata paths. Monitor metadata JSON size. BigQuery reads are read-only and do not use `.snapshots`, `.files`, or other Iceberg metadata tables.

## 4. Fresh initial load

The first cloud execution is deliberately clean:

1. destroy/recreate local persistent volumes;
2. reload Olist source data into MySQL;
3. start Debezium/Kafka with clean history;
4. start GCP Spark queries from beginning offsets;
5. build complete Bronze/Silver/Reference/Audit state in GCS.

No migration of old MinIO files or Kafka checkpoints is required.

## 5. Vertical-slice scope

The mandatory slice includes:

```text
bronze.mysql_cdc_records
silver.order_items_changes
reference.geolocation
audit.silver_progress
```

This matrix tests raw CDC, complex Silver schema, reference batch load, audit/progress semantics, timestamps, ordinary/high-precision decimals, binary/nested fields, streaming commits, batch writes, and BigQuery reads.

## 6. Slice procedure

1. Apply Terraform and SQL migrations needed for the slice.
2. Start only the GCP contour.
3. Create/write the four Iceberg tables through the final Spark image and final service account.
4. Restart the streaming query from GCS checkpoints.
5. Query tables directly from BigQuery using P.C.N.T names.
6. Create/query stable bridge views.
7. Perform additional Spark commits while BigQuery queries are executed.
8. Validate UTC timestamp meaning and decimal mapping.
9. Validate duplicate/retry behavior and `audit.silver_progress` proof.
10. Record BigQuery bytes, errors, latency, table metadata size, and exact versions.

## 7. Go/no-go criteria

### Go

All mandatory behaviors work without an unresolved correctness issue.

### Go with constraints

The path is workable with explicit casts, unsupported-type exclusions, or documented operational constraints that do not change required business semantics.

### No-go

A fundamental catalog/query/type/visibility/recovery limitation prevents the target architecture. Stop after evidence collection. Do not automatically execute a prewritten native-staging fallback; diagnose and redesign based on the actual failure.
