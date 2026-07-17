# Handoff: Stage 2 — Local Kafka, Registry, Connect, and Debezium

## Mission

Implement Phase 2 from
`docs/plans/near-realtime-cdc-implementation-plan.md`. Deliver durable,
schema-aware Avro CDC from the isolated PostgreSQL OLTP source into explicitly
managed local Kafka topics. Do not introduce NiFi, MinIO, realtime warehouse
schemas, CDC Airflow DAGs, Grafana, Prometheus, or AWS resources in this stage.

Stage 1 is complete. The repository now contains a dedicated PostgreSQL 18.4
OLTP service, FK-safe Olist schema, deterministic seed/replay/workload
simulator, synthetic-record ownership controls, and a bounded integration test.
All Stage 1 and existing batch gates passed. Read the completion record in
`docs/cdc/handoffs/stage-1-oltp-simulator.md` before editing.

## Read first

Read these files completely before implementation:

1. `docs/plans/near-realtime-cdc-implementation-plan.md`, especially ADR-001,
   ADR-004, ADR-006, sections 6, 7, 11, 12, 14 Phase 2, 15, 16, 18, and 19.
2. `docs/cdc/phases/phase-0-baseline.md` and
   `docs/cdc/phases/phase-1-oltp-simulator.md`.
3. `docs/cdc/handoffs/stage-1-oltp-simulator.md`.
4. `infra/oltp/initdb/010_create_roles.sh`,
   `infra/oltp/initdb/020_create_oltp_schema.sql`, `compose.yaml`,
   `.env.example`, `.gitignore`, and `streaming/runtime-versions.json`.
5. `scripts/simulation/README.md`, the simulator package, and
   `scripts/ci/check_oltp_simulator_integration.py`.
6. `streaming/schemas/compatibility-policy.json`, its checker, and the existing
   CI workflow.
7. The pinned Debezium 3.6 PostgreSQL and Avro documentation and Apicurio 3.3
   compatibility/rule documentation. Do not copy configuration keys from older
   Debezium or Apicurio examples without checking the pinned versions.

Authoritative references:

- <https://debezium.io/documentation/reference/3.6/connectors/postgresql.html>
- <https://debezium.io/documentation/reference/3.6/configuration/avro.html>
- <https://www.apicur.io/registry/docs/apicurio-registry/3.3.x/index.html>
- <https://kafka.apache.org/43/documentation.html>

## Starting state

The local OLTP source is the Compose service `oltp-postgres` in the
`realtime-core` profile:

| Setting | Stage 1 value |
| --- | --- |
| Container DNS name | `oltp-postgres` |
| Container port | `5432` |
| Default host port | `5433` |
| Database | `olist_oltp` |
| Bootstrap/admin role | `olist_admin` |
| Simulator role | `olist_simulator` |
| Future CDC role | `olist_cdc_reader` |
| Business schema | `public` |
| Non-captured control schema | `simulator_control` |

`olist_cdc_reader` currently has login and read access to business tables but
does not yet have logical-replication privileges. There is no publication,
replication slot, Kafka service, registry service, Connect worker, or CDC topic.

The OLTP service currently initializes through a reproducible local volume.
Stage 2 may reset that volume during integration tests. Existing batch
PostgreSQL and Airflow metadata state are also disposable in this workspace.
This permission does not extend to future immutable object storage, AWS state,
or an environment later designated non-disposable.

## Owned paths

- `streaming/kafka/`: KRaft broker configuration, topic manifest, and topic
  bootstrap/validation scripts.
- `streaming/connect/`: reproducible Connect image, pinned plug-in inventory,
  connector template, registration/status tooling, and configuration checks.
- `streaming/schemas/`: reviewed logical Avro contracts or registry test
  fixtures needed for Stage 2 compatibility evidence.
- `infra/oltp/`: logical-replication PostgreSQL configuration, grants,
  publication, replica identity, and heartbeat SQL.
- `scripts/cdc/` or `scripts/ci/`: bounded CDC integration and readiness checks.
- `tests/`: configuration, topic, connector, key, and event-contract tests.
- `compose.yaml`: add Stage 2 services to `realtime-core` only.
- `.env.example`, `.gitignore`, CI, and documentation only as required by this
  stage.

Do not place generated Kafka logs, Connect offsets, registry state, connector
responses containing resolved secrets, or runtime Avro payload dumps under
version control.

## Scope boundary

Stage 2 ends when validated Avro CDC is durable in Kafka. It must not consume
CDC with NiFi or any custom long-running consumer, land objects, create Parquet,
load the analytical warehouse, create realtime dbt models, or add CDC Airflow
DAGs. A small bounded test decoder is allowed only for contract verification.

The existing batch services must remain unprofiled, and plain
`docker compose up` must retain its current batch-development behavior. Kafka,
Apicurio, Connect, and their bootstrap helpers belong only to
`realtime-core`.

## Fixed local names

Use these stable names unless implementation evidence proves one invalid. A
change requires a short ADR amendment because names participate in offsets,
topic identity, recovery, and later NiFi configuration.

| Resource | Required local name |
| --- | --- |
| Connect worker service | `kafka-connect` |
| Connector name | `olist-postgres-cdc` |
| Connect group | `olist-connect-cluster` |
| Debezium topic prefix | `olist_cdc` |
| PostgreSQL publication | `olist_cdc_publication` |
| PostgreSQL replication slot | `olist_cdc_slot` |
| Connect config topic | `olist_connect_configs` |
| Connect offset topic | `olist_connect_offsets` |
| Connect status topic | `olist_connect_status` |
| Debezium schema-history topic | `olist_cdc.schema_history` |
| Transaction metadata topic | `olist_cdc.transaction` |
| Heartbeat topic | `olist_cdc.heartbeat` |

Set the explicit Debezium heartbeat topic name rather than relying on a
version-dependent derived default. Never change `topic.prefix`, publication,
slot, internal-topic, or connector names during an ordinary restart.

## Exact image baseline

Use the machine-readable pins in `streaming/runtime-versions.json`:

| Component | Required baseline |
| --- | --- |
| Kafka | `apache/kafka:4.3.1` |
| Debezium Connect | `quay.io/debezium/connect:3.6.0.Final` |
| Apicurio Registry | `quay.io/apicurio/apicurio-registry:3.3.0` |
| PostgreSQL source | `postgres:18.4` |

Build a reproducible Connect image or plug-in layer from the pinned Debezium
image. Inventory the PostgreSQL connector, Apicurio Avro converter, and all
additional converter dependencies with exact versions and checksums where
artifacts are downloaded. Do not download `latest`, floating Maven versions, or
unverified plug-ins at container startup. Verify the installed plug-in surface
through the Connect REST API before connector registration.

## PostgreSQL logical-replication contract

Configure the OLTP service for `pgoutput` logical decoding with explicit,
documented values for `wal_level`, replication slots, WAL senders, and any WAL
retention setting required by the bounded tests. Do not weaken OLTP table
constraints or reuse the analytical PostgreSQL service.

Apply these database rules idempotently:

1. Grant `olist_cdc_reader` only the connection, schema usage, table `SELECT`,
   and replication privileges required by Debezium.
2. Create `olist_cdc_publication` explicitly for the eight captured tables.
   Configure the connector with publication auto-creation disabled.
3. Set `REPLICA IDENTITY FULL` on all eight captured tables so update/delete
   events have dependable before images for this educational workload.
4. Use the explicitly named persistent slot `olist_cdc_slot` with
   `slot.drop.on.stop=false`. The first-start workflow may let Debezium create
   the named slot, but deployment tooling must verify and manage its lifecycle;
   an ordinary restart must reuse it.
5. Add a narrowly scoped heartbeat action that advances WAL while idle. If it
   writes `simulator_control.heartbeats`, grant only the required statement
   privileges and keep that schema outside the publication.
6. Add verification queries for publication membership, replica identity,
   slot state, retained WAL bytes, confirmed flush LSN, and heartbeat progress.

Captured tables, in publication order for deterministic validation:

1. `public.customers`
2. `public.orders`
3. `public.order_items`
4. `public.order_payments`
5. `public.order_reviews`
6. `public.products`
7. `public.sellers`
8. `public.product_category_translation`

Explicitly exclude:

- `public.geolocation` — seeded reference data outside initial CDC scope;
- every table in `simulator_control` — operational state, never business CDC;
- the analytical PostgreSQL and Airflow metadata databases.

Use the committed development-only Docker secret as the stable local default.
Connector templates must contain placeholders, not resolved values, and
non-local credentials must remain external.

## Kafka broker and topic contract

Run one local Kafka 4.3.1 broker in KRaft mode with persistent storage,
readiness checks, explicit listener separation where needed for container and
host clients, and replication factor 1. Do not add ZooKeeper.

Create all topics before connector registration. Disable implicit source-topic
creation for the production-like path and make the topic bootstrap idempotent.

Source topics use seven-day retention and `cleanup.policy=delete`:

| Topic | Partitions | Key |
| --- | ---: | --- |
| `olist_cdc.public.customers` | 1 | `customer_id` |
| `olist_cdc.public.orders` | 3 | `order_id` |
| `olist_cdc.public.order_items` | 3 | `order_id`, `order_item_id` |
| `olist_cdc.public.order_payments` | 3 | `order_id`, `payment_sequential` |
| `olist_cdc.public.order_reviews` | 3 | `review_id`, `order_id` |
| `olist_cdc.public.products` | 1 | `product_id` |
| `olist_cdc.public.sellers` | 1 | `seller_id` |
| `olist_cdc.public.product_category_translation` | 1 | `product_category_name` |

Also create before connector registration:

- compacted `olist_connect_configs`, `olist_connect_offsets`, and
  `olist_connect_status` topics with the partition counts required by Kafka
  Connect semantics and replication factor 1;
- compacted, single-partition `olist_cdc.schema_history`;
- single-partition `olist_cdc.transaction` and `olist_cdc.heartbeat`;
- one `olist_cdc.dlq.<table>` topic per captured table for the Stage 3 consumer
  contract, with documented retention and no producer wired in yet.

The topic validator must fail for a missing topic, wrong partition count,
wrong cleanup policy, wrong retention, or unexpected auto-created source topic.
Do not depend only on broker defaults.

Kafka keys must use Debezium's source primary-key schema. Verify scalar and all
three composite-key records. All changes for a source key must resolve to one
partition. The immutable downstream event identity remains
`<topic>:<partition>:<offset>`; do not introduce a different event ID in Stage 2.

## Apicurio and Avro contract

Deploy Apicurio Registry 3.3.0 with persistent local state suitable for restart
tests; an in-memory registry is not sufficient acceptance evidence. Expose
readiness and API checks without requiring a browser.

Use the Apicurio Avro Kafka Connect converter for both keys and values. Configure
Confluent-compatible wire framing because Stage 3 NiFi will use the
Confluent-compatible registry interface. Keep the converter JARs in the
reproducible Connect image, not a mutable runtime download.

Configure registry compatibility as `BACKWARD_TRANSITIVE` and verify it through
the registry API. The repository checker remains mandatory but is not a
substitute for registry-side enforcement. Preserve key schemas as well as value
schemas; composite keys must decode into all key fields.

The integration decoder must prove that Kafka records contain Avro bytes with a
resolvable numeric schema identifier and that the resolved schemas decode the
Debezium envelope. JSON converter output is not acceptable, even if its payload
looks equivalent.

Do not commit registry IDs as stable logical schema versions: registry IDs are
environment state. Retain the subject, schema identifier, and logical schema
version in test evidence for later adapters.

## Connector contract

Version a secret-free connector template and render secrets only at deployment
time. At minimum configure and verify:

- `connector.class=io.debezium.connector.postgresql.PostgresConnector`;
- `plugin.name=pgoutput`;
- `tasks.max=1`;
- the fixed database, topic prefix, publication, and slot names above;
- `publication.autocreate.mode=disabled`;
- `snapshot.mode=initial` for the normal bootstrap;
- the exact eight-table include list;
- transaction metadata enabled;
- tombstones enabled;
- periodic heartbeat records and the heartbeat action query;
- the explicit heartbeat topic and schema-history topic;
- Apicurio Avro key and value converters with Confluent-compatible framing;
- bounded retry/error settings and DLQ behavior only where it does not hide a
  connector-wide data-contract failure.

Connector registration must be idempotent: create when absent, update only when
the rendered non-secret configuration changed, and fail clearly for a connector
or task in `FAILED`. Never delete offsets, drop the slot, or force a resnapshot
as part of a normal update.

Provide finite commands or scripts for:

- service readiness;
- topic creation and validation;
- publication/role/replica-identity validation;
- connector registration/update;
- connector and task status;
- bounded Avro event inspection;
- safe local reset explicitly intended for disposable integration state.

Airflow must not register or supervise the connector.

## Required integration scenarios

Add a bounded Compose integration suite based on
`tests/fixtures/olist_small`. It must start only Stage 2 dependencies, seed the
OLTP source, register the connector, and collect machine-readable evidence.

### Initial snapshot

Wait for snapshot completion and assert exactly one `op=r` current record for
each fixture business row:

| Table | Expected snapshot records |
| --- | ---: |
| customers | 8 |
| orders | 12 |
| order_items | 16 |
| order_payments | 14 |
| order_reviews | 12 |
| products | 8 |
| sellers | 4 |
| product_category_translation | 5 |

Assert zero source records for `geolocation` and `simulator_control`. Decode
keys and values through Apicurio, not by treating payloads as JSON.

### CRUD, keys, deletes, and ordering

Use deterministic simulator configurations plus narrowly scoped SQL fixtures to
prove:

- `c`, `u`, and `d` events retain Debezium before/after envelopes, source
  timestamp, LSN, and transaction metadata;
- hard delete emits one business delete event followed by a separately counted
  tombstone, not two business deletes;
- scalar and composite Kafka keys contain all primary-key fields;
- multiple updates to one key in one PostgreSQL transaction retain transaction
  ordering and increasing Kafka offsets in one partition;
- multi-table order-graph creation retains the shared source transaction
  identity where Debezium exposes it;
- source LSN, transaction order, and Kafka offset form a usable total ordering
  contract without ingestion timestamps.

Do not compare a global order across different Kafka partitions.

### Restart and recovery

After successful streaming:

1. Record connector offsets, slot LSNs, topic end offsets, and snapshot `r`
   counts.
2. Stop and restart Kafka Connect without dropping the slot or internal topics.
3. Generate committed source changes while Connect is unavailable.
4. Verify the connector resumes from stored offsets, emits the downtime changes,
   and does not perform a second initial snapshot.
5. Restart Kafka and Apicurio with persistent volumes and verify existing Avro
   events and schemas remain readable.

### Schema evolution

- Prove a nullable field with a default passes the repository checker and
  registry-side `BACKWARD_TRANSITIVE` compatibility.
- Prove removal, rename, and an incompatible type change fail before production
  source topics receive incompatible data.
- Use isolated registry subjects or a fully disposable source reset for
  destructive compatibility tests. Do not leave the committed OLTP contract in
  a breaking state.

### Heartbeats and WAL

- Observe heartbeat records during an otherwise idle interval.
- Verify the heartbeat action advances PostgreSQL WAL and the slot's confirmed
  position.
- Stop Connect briefly, generate changes, and show retained WAL grows.
- Restart Connect and show the backlog drains without loss and retained WAL
  stops growing monotonically.
- Record byte counts and timings. Phase 2 must demonstrate bounded behavior but
  must not claim the later 512 MB alert threshold is tuned without benchmark
  evidence.

## Unit and static tests

Add tests that do not require live services for:

- exact image pins and absence of floating tags;
- connector template required fields and excluded schemas/tables;
- fixed publication, slot, connector, topic-prefix, heartbeat, and history
  names;
- topic manifest names, partition counts, retention, cleanup policy, and
  replication factor;
- source primary-key and partitioning contract, including all composite keys;
- no resolved non-local credentials in committed templates or rendered output;
- registry compatibility configuration;
- Connect plug-in inventory/checksums;
- Compose default behavior and `realtime-core` dependency wiring;
- readiness/status parser behavior for `RUNNING`, `FAILED`, and partial task
  states.

Keep the live Stage 2 integration in a focused CI job so failures are distinct
from the existing batch fixture pipeline. Dump bounded Kafka, Connect,
registry, and OLTP diagnostics on failure without printing secrets.

## Verification commands

Before handoff, run and record at least:

```text
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run python -m unittest discover -s tests -v
uv run python scripts/ci/validate_realtime_configuration.py
uv run python scripts/ci/check_avro_schema_compatibility.py
docker compose config --quiet
docker compose --profile realtime-core config --quiet
docker compose build airflow
docker compose run --rm --no-deps airflow python scripts/ci/check_airflow_dag_imports.py
```

Also run and record exact Stage 2 commands for:

1. a clean `realtime-core` build/start and readiness check;
2. topic manifest creation and validation;
3. OLTP seed and publication/slot validation;
4. connector registration and initial snapshot reconciliation;
5. Avro CRUD/composite-key/delete/transaction-order checks;
6. Connect restart without resnapshot;
7. compatible and incompatible registry checks;
8. heartbeat and retained-WAL recovery checks;
9. the Stage 1 OLTP integration test;
10. the existing batch fixture integration and replay pipeline.

Record command, result, runtime, topic counts/offset ranges, schema subjects and
versions, slot LSN evidence, restart evidence, and every skipped check with its
blocker. Keep raw generated payloads and runtime state out of Git.

## Exit criteria

Stage 2 is complete only when all of the following are demonstrated:

- the initial fixture snapshot reconciles exactly for all eight captured
  tables and excludes geolocation/control state;
- Kafka keys are correct for scalar and composite primary keys;
- Avro key/value records resolve through persistent Apicurio state under
  `BACKWARD_TRANSITIVE` compatibility;
- insert, multiple update, transaction metadata, hard delete, and tombstone
  semantics are verified with LSN/offset ordering evidence;
- source topics and internal topics are explicit and pass their configuration
  manifest;
- Connect restart reuses offsets and the persistent slot without a second
  snapshot or lost committed changes;
- heartbeat/WAL evidence shows bounded idle and recovery behavior;
- compatible evolution succeeds and incompatible evolution is rejected;
- all Stage 1 and existing batch gates still pass;
- no NiFi, object-storage, realtime warehouse, AWS, or CDC Airflow behavior is
  required for the result.

## Known risk requiring explicit evidence

Debezium 3.6.0.Final supports PostgreSQL 18 and Kafka Connect 3.1 or later, but
the Debezium 3.6 release baseline was built and tested with Kafka 4.2 while this
project pins the local broker to Kafka 4.3.1. Do not change either version merely
to avoid running the integration matrix. Exercise snapshot, streaming,
transaction ordering, schema history, Connect/internal-topic recovery, broker
restart, and WAL recovery against the pinned pair.

If the pinned combination fails, preserve logs and a minimal reproduction, then
add an ADR amendment describing context, tested alternatives, selected exact
replacement, consequences, and migration impact. Never resolve the failure by
using a floating image tag.

## Handoff to Stage 3

The next handoff must report the exact bootstrap servers, registry API mode,
subject naming behavior, topic manifest, key/value framing, heartbeat and
transaction topic behavior, schema ID/version fields, DLQ topic policy,
connector consumer-facing guarantees, and restart/replay evidence that NiFi can
rely on. Stage 3 must not have to infer wire framing or topic semantics from
running containers.
