# Wave 1 J1 validation report

Status: J1 complete. This report records the disposable Docker integration
run and contains no secret values, Kafka payloads, schema payload fragments, or
raw Docker inspect/log dumps.

## Scope

This report covers only the Wave 1 J1 join: shared dependency/Compose
integration, the `local_lab.py` lifecycle contract, runtime writer-schema
evidence, the Iceberg platform migration, the ClickHouse lakehouse seam, and
the common Spark normalization API. Bronze/Silver entity transforms, serving
publication, maintenance, and final parity remain deferred.

## Runtime evidence

| Item | Result |
| --- | --- |
| Validation timestamp (UTC) | 2026-08-01T01:15:20Z |
| Git base before integration commit | `685cd6f26c24412634b01e70acbf828d87bdff23` |
| Implementation commits | `6088ebe3dcaee0345bedfb0524caa4aa96842e50` (platform/integration), `b1cd1ab1b6f59166aa6dfad60bc02419bd0bfcf8` (dbt skeleton) |
| Docker / Compose | Docker Server 29.6.2 / Compose 5.3.1 |
| Compose project | `olist_wave1_j1` |
| Fixed `container_name` entries | 0 |
| Secret files checked | 9 dev source files; report contains no values |
| Final readiness | `local_lab up` ready; final `local_lab status` ready |

### Runtime image IDs

The following are the exact local image IDs observed with
`docker compose ... images --format json`; repeated service images are listed
once.

| Repository:tag | Image ID |
| --- | --- |
| `apache/kafka:4.3.1` | `sha256:47dccc76b32761bc57462b8753144cdbb73a16b123b1d13d3eedb92bb7952b11` |
| `mysql:8.4.10` | `sha256:9cffaceb9b62d4280247acdb2324b380d2b36208ae34dfe9f0afb62eeaf70f08` |
| `postgres:17.10` | `sha256:01b6c71f16212610e782b9f0e7c97bbe78b2df814a25c367890f3f884931eda2` |
| `quay.io/apicurio/apicurio-registry:3.3.0` | `sha256:4433c29ed9280d760eae2345874671f1a1512a2c32dc75f06a720aa09a9043e6` |
| `olist-kafka-connect:3.6.0.Final` | `sha256:e8f7d05da1f1e2afefc384cf144682cc101a787cf05adc93ea27a166f886b2a7` |
| `olist-spark:4.1.3-iceberg1.11.0` | `sha256:d1b757eebbe949267d7c4fd2bd9157f0285680a8bfb10f514fbdaa18879f47f9` |
| `olist-polaris:1.6.0` | `sha256:27758721527abb8b47311ee3f774c14ff27bfdcbae0d0051e6b1e04cc765be7c` |
| `olist-polaris-admin:1.6.0` | `sha256:b9871859cc30612c2a6383712120cb25785358cb3f3517061680d25607bb19ba` |
| `olist-polaris-bootstrap:1.6.0` | `sha256:f722c3a2432b74f6918560af210235da70a9e68d4d2821524b06d442f274f307` |
| `olist-polaris-credentials:1.0` | `sha256:43081fd5859bf426179413bb5f7dfddb6e7bc4e261da3a9fa0cc260511a19fce` |
| `olist-polaris-projector:1.0` | `sha256:f53b7d021f9e8a03df074c97f4714e1334415904780ccc12fc28609270cbe183` |
| `clickhouse/clickhouse-server:26.3.17.4` | `sha256:6dd193894fe56808d7c40e7d2c3d9c7348aa456548ea6502d51714312c997362` |
| `olist-airflow:local` | `sha256:652994621874051e44f64be6b89272b036d044bab7b2198bfc84a9317e4692ab` |
| `olist-minio:RELEASE.2025-10-15T17-29-55Z` | `sha256:be8c9c07801bc65848e4c9102416be2ffff5d18ca4d8e20a7a17615471bc4a7a` |
| `olist-minio-init:RELEASE.2025-08-13T08-35-41Z` | `sha256:097b5b4f7905830714279bf5beab6e077b2729bdb795bd2b062e6e9adf37c5c6` |

### MySQL, Kafka, Connect, and Apicurio

- Clean `bootstrap --archive tests/fixtures/olist_small/olist_small.zip`
  completed with `status=ready`, `capture_state=captured`, and contract
  version 2.
- MySQL `olist_oltp` counts are: `customers=8`, `geolocation=6`,
  `order_items=16`, `order_payments=14`, `order_reviews=12`, `orders=12`,
  `product_category_translation=5`, `products=8`, `sellers=4`.
- The live Kafka validator passed the fixed 15-topic manifest, including
  partition/config checks. Broker-managed service topics and
  `__consumer_offsets` are outside the managed manifest.
- Connector `olist-mysql-cdc` is registered, connector state is `RUNNING`, and
  task 0 is `RUNNING` after bootstrap, restart, and final up.
- Apicurio Registry is healthy and the live compatibility rule is
  `BACKWARD_TRANSITIVE`; the connector uses the SQL/PostgreSQL-backed
  Apicurio deployment.
- The runtime capture observed all 16 key/value slots and 79 schema-only
  records. Capture stores schema bytes and provenance only; no Kafka payload is
  persisted in the evidence bundle.

### Captured writer-schema evidence

All entries are captured from the live Kafka/Registry path. The IDs and
fingerprints below are schema identity evidence, not schema payloads.

| Entity / side | Registry ID | SHA-256 |
| --- | ---: | --- |
| `customers` / key | 7 | `9f5700fa7eb8f9b4c50f039c643512e955f42bf102dd37ad588157d507aa82dc` |
| `customers` / value | 10 | `d622022d67322c944129b84a7e2e3dd2d485fd581ea37e5d5b3114af12efb7fd` |
| `orders` / key | 11 | `5ea6fb639b50c1f8435462dc48e83867e81ae9c9fe3e21b2635ee559f0cba3bf` |
| `orders` / value | 13 | `27ab76afddf19535a5359cfd286fbb5ecf57f0065ad556a428f795dac456b836` |
| `order_items` / key | 14 | `58a3342219bc4279a0b1e21b93f0ce028825a0c47684d3c79000f4f3347aa516` |
| `order_items` / value | 16 | `4aa4857dfbae2506234b3d18818ca4db5344454805ab4bfb5b72b4c99f9562d7` |
| `order_payments` / key | 17 | `46772035e5530523b9a6c87aebd8b5b4d7038cf24c09f6f5c0ddcae1917b4a0a` |
| `order_payments` / value | 19 | `c444ba8de505fbfbe812fa5bab11d9e0c1976576eb7afdc338e292dcb7b94f54` |
| `order_reviews` / key | 20 | `007e02f1df31717b45176fc4bf3c70d82559ce1d8511763076a4ad1544a865b8` |
| `order_reviews` / value | 22 | `97d410a2eaad845907e1137ac4e65c6bcd1cb45388f69ef3e6219010fcd07390` |
| `products` / key | 23 | `909264b1b362855066fc14e5804ae1f0f3ca2e6c897a1426e3ffadfeba2c5576` |
| `products` / value | 25 | `c526d8632f372065580dd881260df9cefc3468fb51ae56207a0212962bf0d2fa` |
| `sellers` / key | 26 | `3076f14faa4e431303a7644c3812792df86f9d890b43ce10c164f0dad5199c03` |
| `sellers` / value | 28 | `53bf2a40e7c259647b7042c0c452d30afb09f977ae42d9c61bc9e72272734d27` |
| `product_category_translation` / key | 29 | `29e926b11bf32beb60f0fcfdec72da362a03e7254b9c4775f25aadd23a7382f5` |
| `product_category_translation` / value | 31 | `d0d04df645b86090a5691bc61b06bd2635a0496765913726b7637de0fe4f989a` |

`writer_schemas validate --require-captured` and the contract validator both
pass. The checked-in `v1` contract files were not rewritten; `v2` is the
captured contract surface.

### Polaris, MinIO, Spark, and Iceberg

- `polaris-bootstrap` completed exact principal-role, catalog-role, and
  privilege verification from `expected-rbac.json`, then performed catalog and
  `bronze` namespace authorization probes for each runtime principal.
- The five credential projections are isolated: `polaris-admin`,
  `polaris-server`, `spark`, `clickhouse`, and `airflow`. Runtime consumers have
  only their own projection mounted read-only; projection producer mounts are
  separate and read/write only for the producer.
- Projection directories are mode `0700`, files are `0600`, with owners:
  Polaris `10000:10001`, Spark `185:185`, ClickHouse `101:101`, and Airflow
  `50000:0`. No runtime consumer uses `user: root`.
- Spark migration completed through the Polaris REST catalog with usable vended
  MinIO credentials. The migration created namespaces `bronze`, `silver`,
  `reference`, and `audit`, with 26 expected tables.
- The repeat migration returned `APPLIED` for
  `0001_initial_lakehouse`, version 1, with the same checksum:
  `d3bf55d90fbfe953cfbc74eef83e6d83f91ce1986cfb85c849da2c3e788b3d8d`.
- The fixed-snapshot DataLakeCatalog smoke passed in a disposable project:
  Spark appended one contract-valid synthetic row to
  `silver.customers_current`, snapshot `905098570482567440` was read by the
  ClickHouse catalog, and both current and fixed-snapshot reads returned one
  row. A full reset removed the synthetic row before the final clean domain.

### ClickHouse and dbt

- Native DDL `001` through `005` was applied twice successfully. Runtime
  inventory is exactly 8 event tables, 8 ReplacingMergeTree current-version
  tables, and 8 stable views.
- `001_replacing_merge_tree_learning.sql` passed all four assertions (`0 0 0
  0`). A disposable publication fixture proved unpublished and deleted
  current versions stay hidden from the stable view; the fixture was truncated
  afterward.
- The real ClickHouse adapter `dbt build` completed with
  `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=78`. Candidate materializations
  used `sync_run_seq=9001`; no publication was performed. The disposable dbt
  state was removed by the final consistency-domain reset.
- ClickHouse catalog and HTTP health checks returned 200. The catalog uses
  read-only Polaris client credentials; static warehouse credentials are not
  passed to ClickHouse.

### Credential leak and restart checks

- The sanitized credential scan checked Compose config, inspect metadata, and
  logs for all project containers. It found no secret value in a
  credential-bearing context and stored no raw output.
- Restarted the Wave 1 long-running services together, then ran
  `docker compose --profile platform --profile serving up -d --wait`; all
  long-running services became healthy and all one-shots exited 0.
- `local_lab down` returned `volumes_preserved=true`; a subsequent bounded
  `local_lab up` returned `status=ready`. Final status retained the MySQL
  counts, connector/task `RUNNING`, registry rule, Polaris 200, ClickHouse 200,
  and Iceberg 26-table surface.

## Static and unit checks

All listed checks exited 0 unless explicitly noted as an intentional skip:

- `uv lock --check` and `docker compose --profile platform --profile
  streaming --profile serving --profile observability config --quiet`;
- `uv run ruff check ...` and `uv run ruff format --check ...`;
- `uv run pyright`;
- `uv run python -m unittest discover -s tests/mysql -v`: 44 tests passed, one
  opt-in disposable reseed test skipped because final MySQL is already seeded;
- `uv run python -m unittest discover -s tests/cdc_contracts -v`: 51 passed;
- `uv run python -m pytest -p no:cacheprovider tests/lakehouse_platform -q`:
  31 passed;
- `uv run python -m unittest discover -s tests/dbt_clickhouse -v`: 15 passed;
- `uv run python -m pytest -p no:cacheprovider tests/test_simulation.py -q`:
  9 passed;
- live MySQL schema integration: passed against the disposable container;
- `local_lab doctor`, `status`, `validate`, `bootstrap`, `up`, and `down`:
  passed with bounded JSON output;
- `git diff --check`: passed; only normal LF-to-CRLF working-copy warnings were
  emitted.

## Deferred work and scope guard

The following commands intentionally return structured non-zero results:

- `start-streaming` and `wait-caught-up`: `not_available_until=J2`;
- `sync-serving`, `rebuild-serving`, `run-maintenance`, and `final-parity`:
  `not_available_until=E`.

Wave 2 Bronze/Silver streaming, entity normalizers, Silver MERGE correctness,
Airflow publication/sync-serving, maintenance, final parity, and legacy asset
deletion remain outside J1.
