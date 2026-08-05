# Detailed Stage F1 Plan: Final Candidate-Only Parity

- **Status**: `COMPLETE` (completed 2026-08-05; run `f1-400372a`; report: [docs/reports/mysql-spark-iceberg-f1-final-parity.md](../../../reports/mysql-spark-iceberg-f1-final-parity.md)).
- **Candidate commit**: `400372a31dcd6cf8f37490f4bb79c93f382f2248`.
- **Frozen baseline commit**: `1400d08345ad81a0121f0ee85ee9ae81cd575a73`.
- **Oracle SHA-256**: `629c36144e64fc9910b822e0907f8a1592b3ef6eb83e438d946267fa3d5b597b`.
- **Fixture SHA-256**: `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976`.
- **Purpose**: prove business parity between the cleaned candidate and the frozen F0 oracle without starting legacy runtime.

---

## 1. Preconditions

1. The F0 oracle and metadata are accepted and stored in `tests/fixtures/final_parity`.
2. Stage L is complete, and common CI and component workflows are green.
3. The candidate is specified by its full commit SHA; the working tree is not an implicit version source.
4. The fixture SHA matches the value in metadata.
5. An isolated Docker runner with sufficient disk and a unique Compose project is available.

---

## 2. Target CLI

```text
python scripts/cdc/local_lab.py final-parity \
  --run-id <unique-run-id> \
  --oracle tests/fixtures/final_parity/main-1400d08.json \
  --confirm-destructive \
  --timeout 5400
```

The command must run only the candidate. Any attempt to create a legacy worktree or access the symbolic `main` in F1 violates the contract.

The accepted execution used run ID `f1-400372a`. The runner and an independent
manifest comparator both returned `PASS` for all 11 relations with zero
missing keys, extra keys, duplicate grains, or business-column mismatches.
F0 validation was rerun successfully, and the scoped Compose cleanup returned
`PASS`. See the [F1 evidence report](../../../reports/mysql-spark-iceberg-f1-final-parity.md).

---

## 3. Execution order

1. Verify the candidate SHA, oracle/metadata schema and all checksums.
2. Create a clean Compose domain; perform a scoped reset only for its resources.
3. Start platform and streaming and load the same fixture.
4. Start the candidate ClickHouse serving observer before the catch-up barrier;
   the barrier uses ClickHouse audit/progress queries in addition to Spark status.
5. Wait for the initial snapshot, committed Bronze/Silver progress and no rejects.
6. Run finite serving sync at the real boundary and `dbt build`.
7. Export candidate current state, fact and marts with the same manifest used by F0.
8. Canonicalize values with the same rules version.
9. For each relation, compare the grain, key set and every business column.
10. Write the machine-readable diff and Markdown summary.
11. Recheck that report status is computed from the diff, then clean the Compose domain on every outcome.

---

## 4. Required artifacts

The `data/reports/final-parity/<run-id>/` directory contains:

- `preflight.json`;
- `candidate-manifest.json`;
- `comparison.json`;
- `report.md`;
- `junit.xml`;
- bounded logs for only the required services on failure.

For each relation, `comparison.json` contains row counts, missing keys, extra keys, column mismatch count, bounded mismatch samples and SHA-256 hashes of canonical rows. Secrets, connection strings and full environment dumps are forbidden.

---

## 5. PASS/FAIL decision

`PASS` is possible only when all conditions hold:

- process exit code `0`;
- all relations from the manifest are present;
- there is no duplicate grain;
- `missing_keys = 0` and `extra_keys = 0`;
- `column_mismatches = 0`;
- fixture, baseline and canonicalization checksums match metadata;
- cleanup completed, or an infrastructure error is separately recorded after the result was computed.

Checksum-only comparison is insufficient. On mismatch, fix the candidate and repeat F1 with the same oracle. Changing the F0 oracle to eliminate a mismatch is forbidden.

---

## 6. Manual GitHub workflow

F1 runs as the `final-parity` job in `.github/workflows/lakehouse-acceptance.yml` with `suite=final-parity`. The workflow runs only through `workflow_dispatch`, binds evidence to `candidate_sha`, serializes through concurrency and publishes artifacts even on `FAIL`.

F1 is not part of normal PR CI: its duration, destructive reset and full stack are disproportionate to every change. Common CI and relevant bounded components remain the required PR barriers.

---

## 7. Program completion criteria

- [x] the F1 report has `PASS` and references the exact candidate/baseline SHAs;
- [x] published machine-readable artifacts agree with the Markdown report;
- [x] a repeat validator confirms the decision;
- [x] cleanup is complete;
- [x] the final report is added to `docs/reports/` and the roadmap marks the migration complete.

---

## 8. Related documents

- [F0 plan](stage-f0-baseline-freeze.md)
- [Final parity contract](../contracts/final-parity.md)
- [CI cutover plan](stage-l-legacy-removal-ci-cutover.md)
