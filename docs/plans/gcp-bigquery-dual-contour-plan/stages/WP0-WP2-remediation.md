# WP0–WP2 Post-Review Remediation and Consolidated Acceptance

## Status and role

This package is the mandatory closure gate for the current WP0–WP2 implementation. It does not introduce a new target architecture and does not authorize work from WP3 or later stages.

A clean reimplementation may deliver these corrections while executing WP0–WP2, but it must still run this package's consolidated acceptance before WP3 begins.

## Dependencies

WP0, WP1, WP2

## Objective

Correct the contract gaps found during independent review and replace happy-path-only evidence with production-path negative tests. Preserve unrelated and later-stage changes already present in the repository.

## Non-goals

- no redesign or acceptance analysis of WP3–WP12;
- no live GCP execution unless separately authorized and configured;
- no provider-neutral dbt refactor;
- no weakening of fail-closed ordering, profile isolation, target isolation, or optimistic concurrency;
- no unrelated cleanup or formatting churn.

## R1 — Production source-timezone semantics [High]

### Required changes

- Pass `SOURCE_TIME_ZONE` to local and GCP Spark driver services.
- Validate the zone during runtime configuration before streaming queries start.
- Normalize MySQL wall-clock business fields such as `DATETIME` through the configured zone and store UTC instants.
- Keep Debezium source timestamps, Kafka timestamps, ingestion timestamps, and other already-instant values on their existing instant semantics; do not apply a second timezone shift.
- Align schema/contract metadata with the implemented source-wall-clock semantics.

### Acceptance

- An end-to-end fixture proves the expected `America/Sao_Paulo` wall-clock-to-UTC conversion in Silver.
- The same fixture under `SOURCE_TIME_ZONE=UTC` produces the corresponding different instant, proving the production setting is effective.
- An invalid zone prevents the Spark streaming application from starting.
- Python-only normalization tests do not count as this acceptance.

## R2 — Batch-level ordering conflicts [High]

### Required changes

- Add Scala/Spark micro-batch conflict detection using the canonical source-coordinate identity.
- Treat an exact replay of the same event identity and payload as idempotent.
- Reject different event identities or payloads that share source coordinates.
- Reject a remaining ambiguity after every canonical tuple field.
- Perform conflict validation before writing Silver changes/current state or committed progress.

### Acceptance

- Scala tests cover snapshot, live non-transactional, and live transactional conflicts.
- An integration test proves a rejected batch does not change `silver.*_changes`, `silver.*_current`, or `audit.silver_progress`.
- Ordering remains based on source coordinates; timestamp, transport fields, and event ID are only documented tie-breakers after valid source coordinates.

## R3 — Ordering audit/quarantine evidence [Medium]

### Required changes

- Persist rejected ordering evidence in `audit.normalization_errors` or a more specific versioned audit table before the affected batch is reported as failed.
- Include a deterministic error ID, event ID when available, entity, error code/message, Kafka topic/partition/offset, schema identifiers, contract version, and occurrence timestamps.
- Make the evidence retry-safe so Structured Streaming retries do not create unbounded duplicates.
- Keep the raw event in Bronze and block serving progress for the affected interval.

### Acceptance

- Replaying the same rejected batch updates or reuses deterministic audit evidence rather than creating unrelated duplicates.
- Operators can identify the exact Bronze record and reason for the block from the audit row.

## R4 — Frozen optimistic predecessor [Medium]

### Required changes

- Before active-state advancement, require the requested predecessor to equal both the target's current active sequence and the predecessor frozen on the run at allocation.
- Encode allowed status transitions in one provider-independent transition contract.
- Apply shared conformance scenarios to the reference ledger, PostgreSQL adapter, and BigQuery adapter where capabilities overlap.
- Preserve same-run sequence, identity, boundary, and predecessor across retry.

### Acceptance

1. Allocate run A against active sequence 0.
2. Publish another valid run so active sequence becomes 1.
3. Attempt to advance run A while supplying 1.
4. The attempt fails as stale and leaves active state and run A unchanged.

Additional tests prove invalid transitions, non-retryable retries, target mismatch, and persistence rollback cannot partially mutate state.

## R5 — Normative CLI and preflight [Medium]

### Required changes

- Make every command in `appendices/A-command-surface.md` parse exactly as documented, including `lab.py local serving run`.
- Keep compatibility aliases where practical without creating a second behavioral contract.
- Remove public flags that permit mutating GCP start operations to bypass missing authentication or configuration.
- Exercise parser entry points rather than only private handler functions.

### Acceptance

- A parameterized parser test covers every WP1 command form.
- `gcp up` and `gcp streaming start` do not invoke Compose when preflight is incomplete.
- `gcp up` still excludes all streaming profiles and services.

## R6 — Durable and truthful evidence [Low]

### Required changes

- Commit a concise acceptance report with exact commands, versions, commit SHA, run ID, result summaries, and checksums, or link an immutable CI artifact containing them.
- Do not rely on an ignored `data/` path as the only evidence.
- Record whether containers, networks, volumes, and generated credentials were removed or preserved; the narrative and machine-readable cleanup result must agree.

## Execution order

1. Add failing regression tests for R1, R2/R3, R4, and R5.
2. Implement R1.
3. Implement R2 and R3 as one fail-closed behavior; neither closes without the other.
4. Implement R4.
5. Implement R5.
6. Produce R6 evidence and run consolidated acceptance.

## Consolidated verification

Run at minimum:

```text
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv lock --check
uv run pytest tests -q
dbt parse for olist_clickhouse with an explicit positive run context
docker compose --profile core --profile lakehouse-local config --quiet
docker compose --profile core --profile lakehouse-gcp config --quiet
Scala formatting, compile, unit tests, and Spark runtime-image verification
clean local CDC acceptance from a fresh project-scoped state
git diff --check
```

The local acceptance must include the new production timezone and rejected-ordering probes; an unchanged historical 11-gate run is insufficient.

## Required report

Create an operator-readable Markdown report containing:

- starting and ending commit SHAs;
- files changed, grouped by R1–R6;
- exact verification commands and summarized output;
- local acceptance run ID and durable evidence location/checksum;
- cleanup actions and actual retained resources;
- remaining limitations, including whether live GCP execution was performed;
- an explicit statement that WP3 remains blocked if any required scenario is unproved.

## Definition of done

- Every R1–R6 acceptance statement is proved or explicitly marked blocked with reproducible evidence.
- No High or Medium finding remains open.
- Existing local behavior and both supported Compose renders still pass.
- The durable report is internally consistent with machine-readable results.
- G2R is closed; only then may WP3 execution proceed.

## Rollback rule

Ordering or timestamp semantic changes require the documented destructive local reset/rebuild path. Revert code and configuration together; do not downgrade persistent schemas or checkpoint semantics in place. Target-specific control changes must not mutate or migrate the other target's physical state.
