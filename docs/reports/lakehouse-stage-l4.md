# Stage L4 legacy-removal report

Status: **PASS**

This report records the implementation and validation of Stage L4. The orphan
guard, target static checks and clean Stage V V0–V10 run all pass. Stage L as
a whole remains active until its separate L5 completion gate is satisfied.

## Scope implemented

- Removed the legacy PostgreSQL OLTP, AWS/Redshift, NiFi, old raw ClickHouse,
  old dbt and legacy control-migration families.
- Removed legacy DAGs, obsolete CI runners, old secret templates, old oracle
  fixtures and implementation-specific tests whose target ownership is
  recorded in the disposition register.
- Retained the one-shot source-database F0 exporter and its relation contract
  for controlled F1 parity regeneration and diagnostics; removed the retired
  Stage 5 relation manifest. The accepted frozen F0 oracle remains unchanged.
- Moved retained tests into explicit target owners, including the dedicated
  observability suite; the Stage V runner remains independent of observability.
- Added an independent orphan guard and updated the target-only control
  bootstrap, runtime dependency set, active runbooks and source-profile docs.

## Normative decisions

The complete per-artifact decisions are recorded in
[the legacy disposition register](../plans/lakehouse/contracts/legacy-disposition-register.md).
AWS/Redshift artifacts are `DELETE`, not deferred. GCP is a separate future
cloud program and is not introduced by L4.

## Text and ownership audit

- `check_legacy_orphans.py`: PASS; 46 removed-path rules and 590 active text
  files scanned with no forbidden active references.
- The whole-repository search still finds retired names in historical
  phase/handoff documents, disposition/contract records and validator
  deny-lists. These are explicit provenance or negative-check inputs, not
  runtime consumers; they must not be used as an excuse to retain a removed
  component.
- The remaining `AWS`/S3 strings in target runtime files are protocol/library
  identifiers required for the local MinIO S3-compatible object store:
  Iceberg S3FileIO, Hadoop S3A, Polaris S3 credentials and MinIO policy ARNs.
  No cloud-provider runtime, credential helper or Redshift consumer remains.
- PostgreSQL ownership is limited to the platform/control plane: Airflow
  metadata, the `olist_control` serving ledger, the Polaris catalog database
  and the Apicurio registry database. No regular source, analytical warehouse
  or business-data runtime path connects to PostgreSQL; the one-shot F0 parity
  exporter is an explicit pre-F1 exception and is not part of target runtime.

## Validation

The following local checks pass for the current candidate:

- `check_legacy_orphans.py`: PASS; 46 removed-path rules, 590 active files
  scanned.
- `check_repository_contracts.py`: PASS.
- `validate_observability_contract.py`: PASS; 18 scrape jobs, 23 alerts and 6
  dashboards.
- `check_dbt_clickhouse_contract.py`: PASS; 20 models and 17 sources.
- Explicit target Python suite: `253 passed, 3 skipped, 86 subtests passed`.
- Observability suite: `24 passed`.
- Scala target image: 9 tests passed; JAR dependency boundary passed.
- Target dbt parse/compile against standalone ClickHouse: PASS.
- Target Airflow DAG inventory inside the Linux Airflow image: PASS; 4 DAGs
  imported and 4 target DAG IDs found.
- `pre-commit run --all-files`: PASS.
- Clean Stage V V0–V10 E2E: PASS; run
  `stage_l4_20260805_f0_restored`, with all mandatory gates passing and normal
  scoped runtime cleanup succeeding.

Evidence is stored at
`data/stage-l-evidence/L4/stage_l4_20260805_f0_restored/`.
