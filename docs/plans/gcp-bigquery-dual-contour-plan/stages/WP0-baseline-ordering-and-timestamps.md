# WP0 — Baseline, Ordering, and Timestamp Contract

## Dependencies

None

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Pin repository baseline and archive current local acceptance evidence.
- Implement validated binlog filename/index parsing.
- Define event categories and required-field validation.
- Publish one language-neutral canonical-order specification and shared conformance fixtures.
- Implement the specification in the WP0 Scala, Python, and ClickHouse consumers. BigQuery consumers are implemented in their downstream work packages and must pass the same fixtures before their stage can close.
- Replace repository-owned `TIMESTAMP_NTZ` specs with UTC instant semantics.
- Add `SOURCE_TIME_ZONE` with default `America/Sao_Paulo` and wire it into the production Spark decoding path for source wall-clock business fields.
- Persist retry-safe audit/quarantine evidence for rejected ordering records before blocking the affected Silver batch.
- Destructively rebuild local Iceberg/ClickHouse/Gold fixtures.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Ordering tests cover snapshot, non-transactional, transactional, malformed, missing, and tie cases.
- Scala batch tests prove that conflicting source coordinates and a remaining full-tuple ambiguity fail closed, while an exact replay of the same event remains idempotent.
- A failed ordering batch writes deterministic `audit.normalization_errors` evidence and does not advance Silver changes, current state, or `audit.silver_progress`.
- An end-to-end MySQL `DATETIME` fixture proves `SOURCE_TIME_ZONE=America/Sao_Paulo` conversion to the expected UTC instant; a second non-default-zone case proves that the production setting is effective.
- Invalid `SOURCE_TIME_ZONE` configuration fails before streaming starts.
- The local contour passes after rebuild.
- No latest-row implementation uses timestamp/event ID as an undocumented fallback.

## Post-review amendment

The production Spark path, not only Python helpers, is the authority for the timestamp acceptance. Per-record validation alone is insufficient for ordering acceptance: conflict detection must run over the actual Silver micro-batch. BigQuery ordering SQL is a downstream conformance obligation and is not a prerequisite for starting WP1, but the shared specification and fixtures delivered here are normative for it.

Historical acceptance output referenced only from ignored `data/` paths is not durable evidence. Commit a concise report containing commands, versions, run IDs, result summaries, and checksums, or link an immutable CI artifact with the same information.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
