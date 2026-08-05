# MinIO object store

This image provides the local object store used by Polaris and Spark. It holds
Iceberg data and Spark checkpoints for the Compose project.

`start.sh` reads the root credential from
`/run/secrets/minio_root_password` without printing it. Bucket creation,
policies and service identities are owned by
`infra/polaris/minio/init.sh`.

Use separate identities for the Iceberg warehouse, Spark checkpoints, Polaris,
ClickHouse and Airflow. Do not place resolved credentials in environment files,
commands or logs.
