# Spark platform

This directory defines Spark runtime configuration and Iceberg table
migrations. Entity decoding and table writes use the contracts under
`streaming/schemas/`.

`render_spark_properties.py` reads credentials only through `*_FILE`
variables and writes a mode `0600` properties file. Required inputs are:

- `POLARIS_SPARK_CLIENT_ID_FILE`
- `POLARIS_SPARK_CLIENT_SECRET_FILE`
- `OBJECT_STORE_ACCESS_KEY_FILE`
- `OBJECT_STORE_SECRET_KEY_FILE`

The catalog alias is `lakehouse` and the Polaris warehouse is
`olist_lakehouse`. Checkpoints use the `olist-checkpoints` bucket
and are separate from table locations.

Run the table migration inside the Spark image:

```text
/usr/local/bin/run-with-platform-config.sh /opt/olist/streaming/spark/platform/migrate.py
```

The wrapper passes the properties-file path to `spark-submit` and keeps
credentials out of command arguments.
