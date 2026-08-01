# Spark lakehouse platform

This directory is the Wave 1 platform contract. It contains no entity business
transformations.

`render_spark_properties.py` reads all credentials through `*_FILE` variables
and atomically writes a mode `0600` Spark properties file. Required secret
inputs are:

- `POLARIS_SPARK_CLIENT_ID_FILE`
- `POLARIS_SPARK_CLIENT_SECRET_FILE`
- `OBJECT_STORE_ACCESS_KEY_FILE` (the checkpoint-only MinIO identity)
- `OBJECT_STORE_SECRET_KEY_FILE`

The catalog alias is always `lakehouse`; its Polaris resource and REST
warehouse are both `olist_lakehouse`. Checkpoints are accepted only below
`s3a://olist-checkpoints/` and are never catalog table locations.

Run the initial migration inside the Spark image with:

```text
/usr/local/bin/run-with-platform-config.sh \
  /opt/olist/streaming/spark/platform/migrate.py
```

The wrapper passes only the properties-file path to `spark-submit`; it never
puts a catalog credential or object-store key on the command line.
