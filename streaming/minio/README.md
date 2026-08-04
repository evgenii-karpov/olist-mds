# Target MinIO runtime

This image is the local S3-compatible object-store adapter for the target
Iceberg/Polaris runtime. It stores the isolated checkpoint and lakehouse data
used by Spark and Polaris; it runs as a local service rather than a cloud
deployment.

`start.sh` reads the root credentials from the Docker secret mounted at
`/run/secrets/minio_root_password` and starts MinIO without printing the
resolved value. Bucket creation, policy and service identities are owned by
`infra/polaris/minio/init.sh`, so this image contains no legacy pipeline
identities or loader policies.
