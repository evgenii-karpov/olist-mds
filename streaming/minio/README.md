# Local CDC object storage

The local object store is built from the final open-source MinIO security
release `RELEASE.2025-10-15T17-29-55Z`. The upstream project stopped publishing
maintained community container images, so using the older prebuilt image would
reintroduce a fixed privilege-escalation vulnerability.

`minio-init` creates the private, versioned `olist-cdc` bucket and attaches a
prefix-limited policy to the `olist_nifi` service identity. Credentials are
read only from Docker secrets. Object versioning is a recovery guard; the NiFi
writer also refuses to replace an existing key with different content.

