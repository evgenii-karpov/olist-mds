# Phase 3: NiFi to MinIO

Status: implemented and verified on 2026-07-16; coverage-contract amendment
implemented on 2026-07-16 for Phase 4 warehouse continuity.

Phase 3 adds persistent MinIO and NiFi services to `realtime-core`, a
version-controlled `olist-cdc-v1` process group, typed CDC schemas, immutable
Avro landing, normalized Parquet, manifests, quarantine/DLQ routing, and the
first Prometheus/Grafana component-health baseline.

## Runtime contract

- MinIO is built reproducibly from source tag
  `RELEASE.2025-10-15T17-29-55Z`; bucket `olist-cdc` is private and versioned.
- NiFi 2.10.0 uses persistent conf, state, database, FlowFile, content, and
  provenance repositories. The custom image verifies the Hadoop and Parquet
  NAR SHA-1 values before installation.
- `streaming/nifi/flow/olist-cdc-v1.json` and
  `streaming/nifi/parameters/local.template.json` are the deployment source of
  truth. `deploy_flow.py` is idempotent and resumes a complete stopped group.
- The stable consumer group is `olist-nifi-cdc-v1`. Bins target 32-64 MiB and
  close after 45 seconds, below the 60-second acceptance ceiling.
- Landing includes business events and tombstones and preserves the original
  framed key/value bytes. Normalized storage contains exactly `r/c/u/d`
  business events; deletes use `before`, and tombstones do not create a second
  delete.
- Object and manifest identity includes topic, partition, exact offset range,
  schema ID, and an event-set digest. Existing identical content is an
  idempotent success; conflicting content at the same key fails closed.
- After each landing object and landing manifest are durable, NiFi writes a
  separate immutable `kind=coverage` manifest. It classifies exact consumed
  offsets into business-event and tombstone ranges and references the committed
  landing identities. Normalized business files and coverage manifests remain
  independent commit markers.

Stock NiFi commits Kafka offsets after durable acceptance into its repositories,
not after all downstream S3 processors finish. A MinIO outage therefore leaves
accepted FlowFiles in the persistent repositories; queue backpressure stops
new consumption. Recovery can additionally reset only the stable consumer
group and replay immutable event IDs without ambiguous object identity.

## Verification evidence

- Compose configuration validated for `realtime-core,observability`.
- MinIO and NiFi images built successfully from pinned inputs.
- MinIO bootstrap created a healthy, versioned private bucket and the
  least-privilege `olist_nifi` policy.
- NiFi REST bootstrap deployed `olist-cdc-v1`; a repeat bootstrap reused the
  group and returned status `deployed`.
- A controlled reset of only `olist-nifi-cdc-v1` to earliest replayed all 16
  source topic partitions and drained Kafka lag to zero.
- Live objects include deterministic Avro landing, Parquet normalized files,
  and manifests for snapshot and later schemas across single- and
  multi-partition tables. Replay reused immutable keys.
- Static schema/flow/configuration tests, Ruff, Pyright, and nine Stage 3 unit
  tests pass.
- The amended coverage contract is versioned under
  `streaming/schemas/cdc-coverage/v1.schema.json`. Contract tests prove exact
  business/tombstone classification, and the Phase 4 isolated integration test
  proves that verified tombstones close normalized offset holes without adding
  raw rows.

## Operations

Build and start:

```text
docker compose --profile realtime-core build minio nifi
docker compose --profile realtime-core up -d --wait minio
docker compose --profile realtime-core run --rm --no-deps minio-init
docker compose --profile realtime-core up -d --wait nifi
docker compose --profile realtime-core run --rm --no-deps nifi-bootstrap
```

For a deliberate full Kafka replay, stop NiFi, reset only
`olist-nifi-cdc-v1`, and restart it. Never reset the Connect worker group or
delete the MinIO volume as part of a replay.

Phase 4 owns warehouse schemas, manifest claims, reconciliation, watermarks,
and the ingest DAG.
