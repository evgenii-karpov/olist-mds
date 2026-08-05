# Polaris and MinIO bootstrap

Polaris provides the Iceberg catalog and uses the `polaris` database in
`platform-postgres`. MinIO stores the catalog warehouse and Spark
checkpoints.

Compose runs the bootstrap in this order:

1. Prepare the local credential volume.
2. Create the Polaris database and initialize its JDBC catalog.
3. Create the MinIO buckets and service identities.
4. Create the `olist_lakehouse` catalog and its namespaces.
5. Project separate credentials for Spark, ClickHouse and Airflow.

Runtime services receive only their own read-only credential projection. The
Polaris server receives the warehouse identity; Spark receives a separate
checkpoint identity. Credentials are read from Docker secret files and are
written with mode `0600`.

The source credential volume must never be mounted into Polaris, Spark,
ClickHouse or Airflow runtime containers.
Bootstrap creates a different target volume for every entry. Runtime services
must not use a Compose `user: root` override.

The supported local recovery for catalog or credential drift is:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
```

The reset recreates the local catalog, object store buckets, checkpoints and
runtime identities.
