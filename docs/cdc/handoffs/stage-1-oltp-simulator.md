# Handoff: Stage 1 — OLTP Database and Deterministic Simulator

Status: implemented and verified on 2026-07-16.

## Mission

Implement Phase 1 from `docs/plans/near-realtime-cdc-implementation-plan.md`.
Deliver an isolated PostgreSQL OLTP source plus a deterministic workload
simulator. Do not introduce Kafka, Debezium, NiFi, realtime warehouse schemas,
or AWS resources in this stage.

Phase 0 is complete: the shared runtime is Python 3.12/Airflow 3.2.1, exact
future service images are recorded in `streaming/runtime-versions.json`, Compose
profile names exist without changing default batch startup, repository ownership
is established, and CI includes configuration and Avro compatibility gates.

## Disposable local state

The user explicitly does not need any current local data preserved. The local
PostgreSQL 18.4 analytics volume and Airflow metadata volume are disposable;
Stage 1 may run `docker compose down -v` whenever a clean compatibility or
integration baseline is needed. Do not implement a migration from Airflow 3.3.0
metadata and do not spend effort retaining existing local warehouse rows.

The new OLTP source created by Stage 1 is also a reproducible local lab service:
its contents must be recreatable through `seed`, and its local volume may be
reset by tests. This permission does not apply to future immutable CDC object
storage, committed fixtures, AWS state, or any environment later marked
non-disposable.

## Read first

Read these files completely before editing:

1. `docs/plans/near-realtime-cdc-implementation-plan.md`, especially sections
   6, 12, 14 Phase 1, 15, 18, and 19.
2. `docs/cdc/phases/phase-0-baseline.md`.
3. `docs/source_contract.md`, `docs/architecture.md`, `docs/data_model.md`, and
   `docs/ci.md`.
4. `compose.yaml`, `.env.example`, `.gitignore`, and existing PostgreSQL fixture
   and loader tests for repository conventions.

## Owned paths

- `infra/oltp/`: source DDL, roles, initialization, seed/bootstrap assets.
- `scripts/simulation/`: simulator package and CLI.
- `tests/`: simulator and OLTP contract tests.
- `compose.yaml`: add the isolated OLTP service to `realtime-core` only.
- `.env.example`, `.gitignore`, CI, and docs only as required by this stage.

Do not put OLTP objects under `infra/postgres/realtime/`; that directory is the
Phase 4 analytical warehouse adapter.

## Required source design

Create a database/service distinct from analytical PostgreSQL and Airflow
metadata. Use the original source columns and OLTP-appropriate types. Preserve
zip prefixes as strings.

Required keys:

| Table | Primary key |
| --- | --- |
| `customers` | `customer_id` |
| `orders` | `order_id` |
| `order_items` | `(order_id, order_item_id)` |
| `order_payments` | `(order_id, payment_sequential)` |
| `order_reviews` | `(review_id, order_id)` |
| `products` | `product_id` |
| `sellers` | `seller_id` |
| `product_category_translation` | `product_category_name` |
| `geolocation` | generated `geolocation_id` |

Add declared foreign keys and indexes for every FK and generator lookup. Model
nullable source timestamps and attributes accurately. Use constraints for order
status, nonnegative amounts/dimensions, valid state codes, and transaction-safe
relationships where the source contract supports them. `geolocation` is seeded
reference data but is not in initial CDC scope.

Create a separate non-captured control schema for simulation runs, seed/config
identity, generated IDs, pending lifecycle transitions, heartbeat/current state,
graceful-stop requests, ownership of synthetic records, and replay timestamp
mapping. Do not add simulator-ownership columns to business tables. A stable
synthetic ID prefix is allowed.

Use dedicated roles for bootstrap/admin, simulator writes, and the later
read/replication integration. Stable committed development-only Docker secrets
are the local default. Phase 2 will add the final least-privilege
logical-replication grants and publication/slot.

## Simulator contract

Expose stable commands:

- `seed`: idempotently load fixture or full Olist archive in FK-safe order.
- `replay`: reconstruct inferred lifecycles with shifted timestamps and a speed
  multiplier.
- `run`: finite or continuous generation at a target lifecycle rate.
- `status`: return run id, random seed, rate, pending transitions, run state,
  and last committed source timestamp.
- `stop`: request a graceful stop after the active database transaction.

Every mutating command accepts a stable random seed. Finite run/replay accepts
duration or event limit. Persist the effective configuration so a run can be
reproduced. Use deterministic IDs and a deterministic logical clock; do not let
wall-clock scheduling change business decisions.

Lifecycle behavior:

1. Choose or create customer, product, and seller references.
2. Create order, item, and payment graph in one transaction.
3. Schedule approved/shipped/delivered or canceled/unavailable transitions.
4. Optionally add a post-delivery review.
5. Occasionally correct mutable customer/product attributes.
6. Rarely hard-delete only simulator-owned graphs in FK-safe order.

Rollback must leave no partial graph. Seeded historical rows must never be
eligible for destructive scenarios.

Prefer a small importable Python package with thin CLI entrypoint. Separate
random decision generation, deterministic clock/ID generation, database
transactions, and command presentation so lifecycle branches can be unit tested
without a live database. Emit structured JSON logs and low-cardinality metrics;
never log credentials or raw connection strings.

## Tests and acceptance evidence

Add unit tests covering:

- every lifecycle branch and transition;
- the three composite keys;
- identical decisions and identifiers for identical seed/configuration;
- different seeds producing a different deterministic sequence;
- graceful stop at a transaction boundary;
- destructive selection excluding seeded rows;
- rollback of an injected failure leaving no partial order graph;
- idempotent seed and FK-valid fixture load;
- status fields and replay timestamp mapping.

Add a bounded Compose integration test using `tests/fixtures/olist_small` that
starts only the OLTP dependency, seeds twice, runs a finite workload, exercises
correction and hard-delete scenarios, and verifies counts/constraints directly.
It must not require Kafka or AWS.

Before handoff, run and record:

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

Also run the new Stage 1 OLTP integration command and the existing fixture
integration pipeline. Record exact commands, results, runtime, and any skipped
check with its blocker.

## Exit criteria

Stage 1 is complete only when a finite fixture workload predictably produces
create, update, cancel, deliver, review, correction, and delete operations; seed
is idempotent and FK-valid; rollback is atomic; historical seeded data is safe;
all batch gates still pass; and no later-stage service is required.

## Known compatibility note for the next stage

Debezium 3.6.0.Final supports PostgreSQL 18 and Kafka Connect 3.1+, but its
release was built/tested with Kafka 4.2 while the approved local broker baseline
is 4.3.1. Stage 1 must not resolve this by changing versions. Preserve the OLTP
contract; Stage 2 owns explicit connector/broker integration evidence and any
ADR amendment if that combination fails.

## Completion record

Stage 1 adds the isolated `oltp-postgres` service to the `realtime-core`
profile on host port 5433 with its own volume. The initialization assets create
the nine Olist business tables, generated geolocation key, declared foreign
keys, FK/lookup indexes, business constraints, `olist_simulator` and
`olist_cdc_reader` roles, and the non-captured `simulator_control` schema. The
reader role intentionally has no replication privilege, publication, or slot;
those remain Phase 2 work.

`python -m scripts.simulation` implements the stable `seed`, `run`, `replay`,
`status`, and `stop` commands. Decisions, identifiers, logical timestamps, and
lifecycle branches depend only on the supplied configuration and seed. Runtime
pacing does not participate in business decisions. The control schema persists
effective configuration, generated IDs, synthetic ownership, pending
transitions, replay timestamp mappings, counters, heartbeats, and graceful-stop
state. Logs are structured JSON and do not contain connection strings or
credentials.

The bounded integration check seeds `tests/fixtures/olist_small` twice, verifies
stable table counts and immediate constraints, produces delivered, canceled,
and unavailable lifecycles, reviews, corrections, and hard deletes, verifies an
injected rollback leaves no partial graph, proves destructive selection cannot
remove historical orders, exercises replay mappings, and checks the status
contract.

## Verification record

All checks were run on 2026-07-16 from the Stage 1 workspace.

| Gate | Result |
| --- | --- |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | Passed; 44 files formatted |
| `uv run pyright` | Passed; 0 errors and 0 warnings |
| `uv run python -m unittest discover -s tests -v` | Passed; 27 tests, 1 POSIX-shell-only skip on Windows |
| `uv run python scripts/ci/validate_realtime_configuration.py` | Passed |
| `uv run python scripts/ci/check_avro_schema_compatibility.py` | Passed |
| `docker compose config --quiet` | Passed |
| `docker compose --profile realtime-core config --quiet` | Passed |
| `docker compose --profile realtime-core up -d --wait oltp-postgres` | Passed; service healthy |
| `uv run python scripts/ci/check_oltp_simulator_integration.py --password-file docker/secrets/dev/postgres_password.txt` | Passed in 1.5 seconds on the small fixture |
| Stage 1 integration evidence | Seed counts: customers 8, geolocation 6, order items 16, payments 14, reviews 12, orders 12, categories 5, products 8, sellers 4; synthetic terminal states: delivered 5, canceled 1, unavailable 1; replay mappings 5 |
| `docker compose build airflow` | Passed in 15.3 seconds |
| `docker compose run --rm --no-deps airflow python scripts/ci/check_airflow_dag_imports.py` | Passed; imported both existing DAGs |
| Existing fixture integration and replay | Passed in 247.3 seconds; initial and replay raw/analytical fingerprints matched |

The full `olist.zip` seeding path is implemented but was not loaded as part of
the bounded CI evidence; the committed small fixture is the Stage 1 integration
gate. No Kafka, Debezium, NiFi, realtime warehouse schema, or AWS resource was
introduced.
