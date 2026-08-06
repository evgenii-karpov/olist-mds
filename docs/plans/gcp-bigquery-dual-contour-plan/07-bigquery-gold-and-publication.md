# BigQuery Gold, Incremental Processing, and Publication

## 1. Project separation

`dbt/olist_bigquery` is an independent project. It shares semantic documentation and parity expectations with `dbt/olist_clickhouse`, but not a provider-neutral SQL layer.

The projects preserve:

- model names and grains;
- business/surrogate key inputs;
- SCD2 validity meaning;
- revenue, freight, payment, and ARPU definitions;
- null and deletion behavior;
- tests and documentation.

## 2. Physical datasets

```text
olist_lakehouse_bridge  read-only source views
olist_gold_store        model history/deltas + materialized current state
olist_gold              stable serving views
olist_serving_control   run/boundary/result/publication state
```

## 3. Naming convention

For each model `<model>`:

```text
olist_gold_store.<model>__history
olist_gold_store.<model>__current
olist_gold.<model>                  -- stable view
```

History rows include at minimum:

```text
sync_run_seq
sync_run_id
operation_type        -- INSERT / UPDATE / DELETE / CLOSE / REPLACE_GRAIN etc.
business key / model grain
payload columns
source interval metadata
built_at
```

One history table contains all runs for that model. There are no per-run physical tables.

## 4. Incremental derivation

### Initial run

Build a complete state-derived delta sufficient to populate every current table.

### Subsequent runs

1. Read each relevant `silver.*_changes` source only within `(previous_boundary, current_boundary]`.
2. Derive changed business keys.
3. Propagate exact impact to downstream grains.
4. Recompute only impacted rows/partitions.
5. Write candidate operations to the run's history rows.

No fixed time lookback is used.

## 5. Model-specific mutation semantics

- Current dimensions/facts: insert/update or delete the affected current row.
- SCD2 dimensions: close the active version and add a new version as required; corrections may rebuild the affected key's timeline.
- Daily/monthly aggregates: recompute exact affected dates/months and replace those grains transactionally.
- Static dimensions: update only when source/reference logic changes.

Late-arriving and corrected facts use the same impact-propagation mechanism rather than a separate periodic lookback.

## 6. Partitioning and clustering

General rules:

- large fact/mart current tables: partition by business/event/grain date and cluster by high-value business keys;
- dimension current tables: usually unpartitioned, clustered by business key;
- history tables: partition by run/build date where useful and cluster by `sync_run_seq` plus model key;
- do not force partitioning on very small tables solely for symmetry.

## 7. SQL ownership

Versioned SQL migrations create/evolve:

- control tables;
- history/current tables and required constraints/contracts;
- bridge views;
- stable serving views;
- publication procedures.

`dbt-bigquery` writes physical per-run model history/deltas and test evidence only.

## 8. Publication transaction

A versioned stored procedure accepts:

```text
sync_run_seq
expected_active_sync_run_seq
```

Inside one BigQuery multi-statement transaction it:

1. asserts the run exists and is ready;
2. asserts all expected entity/model tests passed;
3. asserts the current active sequence equals the expected predecessor;
4. treats an already-active same run as idempotent success;
5. rejects a stale run as `CONFLICTED` without changing current state;
6. applies every model's history operations to its current table;
7. performs SCD2 closes/inserts and aggregate-grain replacement;
8. updates run/model publication status;
9. advances `active_sync_run_seq`;
10. commits all changes together.

Any failure rolls back all current-state and control-state changes.

## 9. Retry, conflict, and recovery

### Same-run retry

Before rebuilding an unpublished run:

- delete all `<model>__history` rows with that `sync_run_seq`;
- reset model/entity results;
- preserve the frozen boundary and predecessor;
- rebuild with the same sequence.

### Stale conflict

A run whose expected predecessor is no longer active cannot overwrite the newer state. Mark it conflicted and require reconciliation.

### Published rollback

Create a new compensating run with a new sequence. It is built, validated, and published through the normal procedure. Pointer rollback is not used.

## 10. Retention and schema evolution

Retain successful, failed, and conflicted history because the project is small. Do not implement automatic cleanup initially.

- additive changes: versioned migrations and compatible dbt updates;
- breaking key/type/structure changes: reset/rebuild the GCP Gold/control state and related Iceberg data as documented.
