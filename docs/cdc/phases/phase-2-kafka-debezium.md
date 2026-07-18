# Phase 2: Local Kafka, Registry, Connect, and Debezium

Status: implemented and verified on 2026-07-16.

Phase 2 adds durable schema-aware CDC without introducing NiFi, object storage,
warehouse CDC schemas, or Airflow CDC DAGs. The `realtime-core` profile now
runs the Phase 1 OLTP source, Kafka 4.3.1 in KRaft mode, Apicurio Registry 3.3.0
with KafkaSQL persistence, and a Debezium 3.6.0.Final distributed Connect
worker.

## Runtime and data contracts

- Kafka is available at `kafka:29092` inside Compose and `localhost:9092` from
  the host. Its data volume is persistent and broker auto-creation is disabled.
- Apicurio native v3 API is at `/apis/registry/v3`; Confluent-compatible clients
  use `/apis/ccompat/v7`; the Debezium converter uses the Registry v2 API.
- Global registry compatibility is `BACKWARD_TRANSITIVE` and persists in the
  KafkaSQL journal across broker and registry restarts.
- Keys and values use Confluent-compatible Avro framing: magic byte `0`, a
  four-byte big-endian numeric Apicurio content ID, then Avro payload bytes.
- Main subjects use `<topic>-key` and `<topic>-value`. Apicurio also stores
  referenced Debezium record subjects such as the table `Value`, PostgreSQL
  `Source`, and transaction `event.block`. Registry IDs are environment state,
  not committed logical versions.
- Source events are ordered by source LSN, `source.txId` plus transaction order,
  and partition offset. In Debezium 3.6 the envelope transaction ID includes an
  event LSN; `source.txId` is the shared PostgreSQL transaction identity.
- Debezium derives heartbeats as `<heartbeat-prefix>.<topic-prefix>`. A
  heartbeat-only predicate and RegexRouter make the consumer-facing topic the
  fixed `olist_cdc.heartbeat`; business topics are not transformed.

The full topic contract is in `streaming/kafka/topics.json`. The eight DLQ
topics are reserved for Phase 3 with matching source partitions, seven-day
retention, and no Phase 2 producer.

## Operations

Start and configure a clean local stack:

```text
docker compose --profile realtime-core up -d --wait \
  oltp-postgres kafka
docker compose --profile realtime-core run --rm --no-deps kafka-topics
docker compose --profile realtime-core up -d --wait \
  apicurio-registry
python scripts/cdc/stage2_admin.py configure-registry
python -m scripts.simulation seed \
  --archive tests/fixtures/olist_small/olist_small.zip \
  --seed 20260716 \
  --password-file docker/secrets/dev/postgres_password.txt
docker compose --profile realtime-core up -d --wait kafka-connect
python scripts/cdc/stage2_admin.py register-connector \
  --password-file docker/secrets/dev/postgres_password.txt
```

Run bounded checks:

```text
python scripts/cdc/stage2_admin.py validate-topics
python scripts/ci/check_stage2_cdc_integration.py \
  --password-file docker/secrets/dev/postgres_password.txt
python scripts/ci/check_apicurio_compatibility.py
```

If a deliberate registry restart occurs while Connect is producing, strict
`errors.tolerance=none` can leave the task FAILED after converter retries are
exhausted. Restore registry health, inspect status, and run `restart-failed`.
This retains the slot and offsets and does not resnapshot.

For the disposable local lab only, stop the project and remove exactly the
Phase 1/2 data volumes (default Compose project name):

```text
docker compose --profile realtime-core down
docker volume rm olist-mds_olist_oltp_data olist-mds_olist_kafka_data
```

Do not use this reset for immutable landing objects introduced in Phase 3 or
for any non-disposable environment.

## Verified evidence

The clean fixture snapshot produced exactly 8 customers, 12 orders, 16 items,
14 payments, 12 reviews, 8 products, 4 sellers, and 5 category translations;
geolocation and simulator control state produced no source events. All three
composite keys decoded with every primary-key field.

The CRUD probe produced `c,u,u,d` for one order in one partition followed by
one tombstone. Two updates in one PostgreSQL transaction shared `source.txId`
and had increasing `data_collection_order` and Kafka offsets. The multi-table
create shared one source transaction identity.

Connect downtime increased retained WAL from 18,800 to 20,200 bytes. After
restart the customer end offset advanced from 11 to 12, the slot became active,
`confirmed_flush_lsn` advanced from `0/1CE4EE0` to `0/1CE9E60`, and snapshot
counts remained unchanged. Idle heartbeat offsets advanced and retained WAL
remained bounded in the tens of KiB during this short test; no 512 MB tuning
claim is made.

After Kafka and Apicurio restarts, the registry retained
`BACKWARD_TRANSITIVE`, existing subjects remained readable, and the decoder
again reconciled the original snapshot. A deliberate simultaneous dependency
outage produced an explicit FAILED task; `restart-failed` resumed from stored
offsets without a snapshot and subsequent CRUD passed.

Registry evolution accepted a nullable field with a default (HTTP 200) and
rejected an incompatible type (HTTP 409). The repository checker additionally
rejects removals and renames before any production subject is changed.

## Verification record

All checks below passed on 2026-07-16:

| Gate | Result |
| --- | --- |
| Ruff lint and format | Passed; 50 files formatted |
| Pyright | Passed; 0 errors and 0 warnings |
| Python unit suite | Passed; 37 tests, 1 Windows POSIX-shell skip |
| Realtime configuration and repository Avro compatibility | Passed |
| Default and `realtime-core` Compose config | Passed |
| Connect image build and checksum inventory | Passed |
| Topic/live OLTP/connector checks | Passed; 22 explicit topics, connector and task RUNNING |
| Clean Avro snapshot/CRUD/composite-key/delete assertions | Passed |
| Connect downtime and Kafka/Apicurio restart recovery | Passed without resnapshot |
| Stage 1 OLTP simulator integration | Passed |
| Airflow image and DAG imports | Passed; 2 DAGs imported |
| Existing batch fixture integration and replay | Passed in 265.8 seconds; fingerprints matched |
