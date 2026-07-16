# Phase 1: OLTP Database and Deterministic Simulator

Status: implemented on 2026-07-16.

Phase 1 establishes a source system that is independent of both the analytical
PostgreSQL database and Airflow metadata. The Compose `realtime-core` profile
starts `oltp-postgres` on host port 5433 with a dedicated volume and PostgreSQL
18.4 image.

## Source contract

The OLTP schema retains every original Olist column and adds only the required
generated `geolocation_id`. Primary keys match the approved plan, including the
three composite keys. Foreign keys are declared and indexed; state codes,
statuses, scores, timestamps, amounts, and physical dimensions have database
constraints. Zip-code prefixes remain strings.

The `simulator_control` schema is outside the business-table set and is reserved
for runs, deterministic ID allocation, synthetic ownership, scheduled
transitions, replay timestamp mappings, seed row identity, counters,
heartbeats, and graceful stop state. Stage 2 must exclude this schema and
`geolocation` from its initial Debezium publication.

## Simulator behavior

The simulator is an importable Python package with a thin CLI. A stable seed and
configuration reproduce identifiers, decisions, and logical source timestamps.
It creates each order/item/payment graph atomically, then applies lifecycle
updates as separate transactions so later CDC captures meaningful intermediate
states. Delivered orders may receive reviews; synthetic customer/product rows
may receive corrections; hard delete first verifies control-schema ownership
and deletes only the synthetic order graph in FK-safe order.

`seed` accepts either the Olist zip archive or an extracted directory and loads
entities in FK-safe order. Primary-key entities use upserts. Geolocation rows
use archive identity plus source row number in the control schema, preserving
duplicate reference rows while making repeated seeds idempotent.

See [the Stage 1 handoff](../handoffs/stage-1-oltp-simulator.md) for exact
verification evidence and [the simulator README](../../scripts/simulation/README.md)
for commands.
