# Spark platform

This directory defines Spark runtime configuration and Iceberg table
migrations. Entity decoding and table writes use the contracts under
`streaming/schemas/`.

`render_spark_properties.py` reads credentials only through `*_FILE`
variables and writes a mode `0600` properties file. The backend is selected by
`SPARK_BACKEND` (or the compatibility alias `SPARK_CONTOUR`) and is either
`local` or `gcp`.

The local backend requires:

- `POLARIS_SPARK_CLIENT_ID_FILE`
- `POLARIS_SPARK_CLIENT_SECRET_FILE`
- `OBJECT_STORE_ACCESS_KEY_FILE`
- `OBJECT_STORE_SECRET_KEY_FILE`

The GCP backend requires a mounted ADC file and the following non-secret
configuration:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `GCP_LAKEHOUSE_PROJECT_ID`
- `GCP_CHECKPOINT_BUCKET`
- `ICEBERG_WAREHOUSE` (`bl://...` or `gs://...`)

It uses the BigLake Iceberg REST catalog, `GoogleAuthManager`, `GCSFileIO`,
and the Hadoop GCS filesystem for checkpoints. GCP drivers must use a
dedicated Spark ADC file; they never inherit the local Polaris or S3A
credentials. The catalog alias defaults to `lakehouse`; the legacy
`ICEBERG_CATALOG_NAME` variable remains supported, while
`ICEBERG_SPARK_CATALOG_ALIAS` has precedence.

Local checkpoints use the isolated `olist-checkpoints` bucket. GCP
checkpoints must stay inside `GCP_CHECKPOINT_BUCKET` and are separate from
table locations.

The common image pins and checksums all runtime artifacts. It includes both
the local S3A/MinIO and GCP REST/GCS paths, so alias and contract behavior can
be exercised locally before cloud credentials are available.

Run the table migration inside the Spark image:

```text
/usr/local/bin/run-with-platform-config.sh /opt/olist/streaming/spark/platform/migrate.py
```

The wrapper passes the properties-file path to `spark-submit` and keeps
credentials out of command arguments.
