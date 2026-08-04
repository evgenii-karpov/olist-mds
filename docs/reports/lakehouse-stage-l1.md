# Stage L1 implementation report

Status: **L1 complete; Stage L remains ACTIVE**.

This report records the target-runtime repairs completed after the L0 reset. It
does not declare the whole Stage L complete: observability, CI cutover and
legacy removal remain separate substages.

## Candidate and acceptance evidence

- Candidate baseline commit: `9c0036c84b758ebe72b31388d009982e16dd2a75`
  (the worktree contains the L1
  candidate changes; no commit was created for this L1 implementation).
- E2E run: `stage_l1_20260804_v6`.
- Evidence root: `data/stage-l-evidence/L1/stage_l1_20260804_v6/`.
- Result: `PASS` for every Stage V gate `V0` through `V10`.
- Root summary: `data/stage-l-evidence/L1/stage_l1_20260804_v6/summary.json`.
- Compose project: `olist_stage_v`.

The runtime was cleaned after the run with:

```text
docker compose --project-name olist_stage_v down --volumes --remove-orphans
```

There are no remaining Compose projects, containers or project volumes for
this E2E stack.

## What L1 changed

The implementation is intentionally narrow and target-owned:

- added dedicated local development secret files and file-only target secret
  loading for MySQL, MinIO, Polaris and Apicurio;
- routed the CDC bootstrap through the dedicated MySQL CDC reader rather than
  the simulator seed credential;
- removed active Redshift-specific raw-type metadata in favor of target-neutral
  profile metadata; the obsolete Redshift DDL generator remains a documented
  `DELETE` candidate for L4;
- implemented effective transaction-state reduction for append-only audit
  observations, including split `BEGIN`/`END`, unresolved `OPEN`, duplicate
  `END`, `REJECTED -> COMPLETE`, and ordering behavior in Scala, serving and
  Stage V validation;
- made serving/control readiness checks target-owned while retaining legacy
  control migrations during the compatibility window;
- moved runtime writer-schema capture to temporary/evidence storage so a Stage
  V run does not mutate the frozen tracked capture bundle;
- separated simulator DML credentials from the admin credential required by
  the additive-schema fixture;
- aligned observability image versions with the existing Compose contract.

No tests were deleted. Existing root tests and legacy compatibility migrations
remain available for the explicitly planned L2-L4 transfer/removal work. This
is deliberate: an implementation-name assertion may be removed only together
with its implementation, while business, data-quality, transaction and
secret-safety assertions must first be rewritten or replaced.

AWS/Redshift artifacts are not deferred to a later AWS stage: their disposition
is `DELETE`. GCP/BigQuery is a separate future program. Local MinIO and its
S3-compatible `s3a://` interface remain part of the current local target.

## Validation history and diagnostics

| Run | Result | Diagnosis and resolution |
| --- | --- | --- |
| `stage_l1_20260804_v3` | Failed at `03-initial-snapshot` | The probe defaulted to MySQL `root` while the target simulator contract uses `olist_simulator`. The probe identity and secret path were corrected. |
| `stage_l1_20260804_v4` | Failed at `07-dbt-and-stable-views` | Two new untracked tests were not formatted; `ruff format` was run and serving static validation was repeated successfully. This exposed that pre-commit `--all-files` alone is insufficient for an untracked candidate tree. |
| `stage_l1_20260804_v5` | Failed at `08-additive-schema` | The simulator user correctly lacked `ALTER`; the additive-schema fixture was changed to use the dedicated `olist_admin` credential. |
| `stage_l1_20260804_v6` | **PASS** | All V0-V10 gates passed, including additive schema, rebuild, serving sync, dbt/stable views and final effective-state validation. |

The target Python suites, Scala formatting/tests/package checks, pre-commit
checks and serving static validation were also green in the final candidate.

## Next substages

- **L2:** implement and validate the target observability chain described in
  `docs/plans/lakehouse/contracts/observability.md`; the current legacy
  observability test is retained until its assertions are transferred.
- **L3:** cut CI over to the target suites and the validation contract in
  `docs/plans/lakehouse/contracts/validation-and-ci.md`.
- **L4:** perform orphan scans, then remove artifacts whose L0 disposition is
  `DELETE`, including all AWS/Redshift artifacts, with a clean V0-V10 run after
  the removals.

The detailed stage plan and disposition register remain authoritative:

- [Stage L completed plan](../plans/lakehouse/completed/stage-l-legacy-removal-ci-cutover.md)
- [Legacy disposition register](../plans/lakehouse/contracts/legacy-disposition-register.md)
