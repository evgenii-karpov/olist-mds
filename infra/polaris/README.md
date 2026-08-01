# Polaris and object-store bootstrap resources

The platform uses Polaris `1.6.0` with its relational JDBC backend in the
`polaris` database on `platform-postgres`. The admin tool bootstraps realm
`POLARIS`; the server and admin images load database and root credentials only
from secret files.

The bootstrap sequence is intentionally split into bounded one-shot steps:

1. `credentials/prepare.sh` creates the bootstrap administrator credential
   pair in the ephemeral credentials volume with mode `0600`.
2. `postgres/010_create_polaris_database.sh` creates the database/user.
3. `admin/bootstrap-jdbc.sh` idempotently initializes the JDBC schema/realm.
4. `minio/init.sh` creates `olist-lakehouse` and `olist-checkpoints`, with
   disjoint warehouse and checkpoint identities/policies.
5. `bootstrap/bootstrap.sh` creates catalog `olist_lakehouse`, namespaces,
   three runtime principals, their roles and grants, verifies the exact live
   RBAC graph, authenticates every saved runtime credential pair, and writes
   the pairs with mode `0600`.

The catalog storage contract keeps both the S3 data endpoint and the STS
endpoint on the internal MinIO address `http://minio:9000`. Iceberg clients
must request `X-Iceberg-Access-Delegation: vended-credentials`; only the
Polaris server receives the static warehouse identity. Spark receives a
separate static identity solely for `olist-checkpoints`.

The runtime credential artifact prefixes are:

- `polaris-spark-*`
- `polaris-clickhouse-*`
- `polaris-airflow-*`
- `bootstrap-admin-*`
- `minio-polaris-*`
- `minio-checkpoints-*`

If an identity exists in Polaris/MinIO but its credential pair is absent (or
vice versa), bootstrap fails closed. The supported recovery is a full local
reset; credentials are never silently rotated around persisted catalog state.

## Runtime credential projections

The consistency-domain volume is a root-owned producer volume. It must never
be mounted into Polaris, Spark, ClickHouse, or Airflow runtime containers.
`credentials/projector.Dockerfile` supplies a bounded root one-shot whose only
job is to copy the allowlisted files from that source into one dedicated named
volume, change ownership to the actual runtime UID/GID, and leave the directory
at `0700` and each file at `0600`. Runtime services keep their image user; they
must not use a Compose `user: root` override.

`credentials/projection-contract.json` is the machine-readable J1 interface.
It defines five isolated projections because the Polaris admin tool and server
have different needs:

- `polaris-admin`: bootstrap administrator pair only;
- `polaris-server`: bootstrap administrator plus the MinIO warehouse pair;
- `spark`: Spark Polaris pair plus the checkpoint-only MinIO pair;
- `clickhouse`: ClickHouse Polaris pair only;
- `airflow`: Airflow maintenance Polaris pair only.

J1 must create a different target volume for every entry above. For each
projector service, mount the consistency-domain source read-only at
`/run/polaris-credentials`, mount exactly one target volume read-write at
`/run/projected-credentials`, set `CREDENTIAL_CONSUMER`, and set numeric
`CREDENTIAL_TARGET_UID` and `CREDENTIAL_TARGET_GID` to the named user from the
corresponding pinned consumer image. The consumer mounts only its own target
volume read-only and points the environment variables listed in the contract
at `/run/projected-credentials/<source>`.

The required ordering is:

1. prepare the root credential volume;
2. project `polaris-admin`, then run JDBC admin bootstrap;
3. initialize MinIO, then project `polaris-server` and start Polaris;
4. run catalog bootstrap, then project `spark`, `clickhouse`, and `airflow`;
5. start those consumers only after their projector completed successfully.

The PostgreSQL username/password files remain independent platform secrets and
are not part of this projection contract. The MinIO client gets a unique
private `MC_CONFIG_DIR`, removed by a trap. Its user-management commands still
require access key and secret as positional arguments in the supported `mc`
CLI, so their short-lived argv exposure is an explicit J1 process-isolation
gap rather than an invented stdin/file interface.

## RBAC verification and J1 smoke

`bootstrap/expected-rbac.json` is compared exactly with the assignments and
catalog grants returned by Polaris CLI 1.6 after `setup apply`. Spark receives
the supported `TABLE_CREATE`, read/write property, and read/write data grants,
but no DROP or access-management privilege. ClickHouse is strictly read-only.
Airflow receives read/write property and data grants for maintenance, but
cannot create or drop tables or manage access. Unexpected persisted grants
cause bootstrap to fail with a full-reset requirement; `setup apply` is not
treated as proof that every grant succeeded.

The bootstrap also logs in with each saved runtime client ID/secret and reads
the catalog plus `bronze` namespace. Docker is deliberately outside Parallel
Wave 1 code-first validation, so J1 must still prove the Polaris 1.6 JSON-line
CLI output contract, resolve each pinned image's numeric UID/GID, and perform
an end-to-end Spark Iceberg operation that receives usable temporary MinIO STS
credentials. Failure of any of those checks blocks platform readiness.
