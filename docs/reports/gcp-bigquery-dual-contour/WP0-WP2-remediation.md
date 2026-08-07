# WP0-WP2 remediation evidence report

Status: PASS. The implementation is complete in the worktree; no commit was created by this task.

## Revision and run identity

- Starting commit SHA: `22db8622fdc20db61ca328469a5219fb82f3af32`.
- Ending commit SHA: `22db8622fdc20db61ca328469a5219fb82f3af32` (same HEAD; implementation remains in the worktree).
- Final Run ID: `wp0-wp2-20260807T164500Z`.
- Final evidence root: `data/acceptance/local-cdc/wp0-wp2-20260807T164500Z/`.
- Final acceptance started at `2026-08-07T16:43:53.253752+00:00` and finished at `2026-08-07T17:05:34.752923+00:00`.
- Compose project: `olist_local_cdc_acceptance`.

Tool versions captured after the final run:

```text
uv 0.11.28
Python 3.12.13
dbt-core 1.11.8
dbt-bigquery 1.11.3
dbt-clickhouse 1.10.1
docker client/server 29.6.2
docker compose 5.3.1
```

## Negative-first evidence

The negative tests were added before implementation. The initial command was:

```text
uv run pytest tests/lakehouse_platform/test_spark_config.py tests/lakehouse_platform/test_spark_ordering_contract.py tests/serving/test_control_domain.py tests/orchestration/test_lab_cli.py tests/test_wp0_wp2_remediation_report.py -q
```

Result before implementation: `5 failed, 43 passed`.

The final mandatory evidence is present in the final preflight:

- production decoder `SOURCE_TIME_ZONE` path: PASS for `America/Sao_Paulo` and `UTC`;
- Scala micro-batch conflict matrix: PASS for snapshot, live non-transactional, and live transactional coordinates;
- exact replay idempotency, including different transport coordinates: PASS;
- deterministic `audit.normalization_errors` schema/error-ID evidence: PASS;
- rejected Silver ordering gate before state writes: PASS;
- stale predecessor scenario: PASS; stale run A remained unchanged after run B published active sequence 1.

## Remediation scope

- R1: `SOURCE_TIME_ZONE` is validated before Spark startup, propagated through local/GCP drivers, and used only for MySQL DATETIME wall-clock normalization. Debezium/Kafka instants remain instant-valued.
- R2/R3: canonical source-coordinate ordering is validated before Silver state/progress writes; ambiguous/colliding batches fail closed, raw Bronze is retained, and deterministic audit evidence is written to `audit.normalization_errors`.
- R4: the provider-independent serving state matrix and frozen predecessor compare-and-set checks are shared by local/PostgreSQL and GCP/BigQuery paths.
- R5: the normative CLI grammar is enforced and mutating GCP commands always run mandatory preflight; public auth/config bypass flags are removed.
- R6: the acceptance harness records mandatory production, Scala, audit, Silver-gate, stale-predecessor, gate, cleanup, and checksum evidence.

## Static gate before full e2e

The full e2e was launched only after these static checks were green:

| Command | Result |
| --- | --- |
| `uv run pre-commit run --all-files` | exit 0; all hooks passed, including Ruff, format, Pyright, dbt parse and BigQuery parse |
| `uv run pytest tests -q` | exit 0; `402 passed, 3 skipped, 86 subtests passed` |
| `uv run ruff check .` | exit 0; all checks passed |
| `uv run ruff format --check .` | exit 0; `144 files already formatted` |
| `uv run pyright` | exit 0; `0 errors, 0 warnings, 0 informations` |
| `uv lock --check` | exit 0; resolved 210 packages |
| `uv run python -m streaming.schemas.generate_contracts --check` | exit 0; eight contract chains current |
| `docker compose --profile core --profile lakehouse-local config --quiet` | exit 0 |
| `docker compose --profile core --profile lakehouse-gcp config --quiet` | exit 0 |
| `git diff --check` | exit 0; only Git LF/CRLF warnings |
| `uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse --vars '{"sync_run_seq": 1, "sync_run_id": "wp0-wp2-static"}'` | exit 0; dbt 1.11.8 parse completed |

## Full local acceptance

Exact command:

```text
uv run python scripts/validation/local_cdc_acceptance.py run --run-id wp0-wp2-20260807T164500Z --evidence-dir data/acceptance/local-cdc/wp0-wp2-20260807T164500Z --confirm-reset
```

Result: exit 0, `overall_status=PASS`, all 11 mandatory gates passed:

```text
00-preflight PASS
01-harness-ready PASS
02-clean-bootstrap PASS
03-initial-snapshot PASS
04-crud-and-restart PASS
05-caught-up PASS
06-serving-sync PASS
07-dbt-and-stable-views PASS
08-additive-schema PASS
09-rebuild PASS
10-final PASS
```

The production final gate recorded `publication_status=PUBLISHED`, `last_published_sync_run_seq=4`, no active runs, no open/rejected transactions, and stable Iceberg/Gold counts. The final status command recorded ClickHouse 200, connector RUNNING, Iceberg READY, registry 200, and writer schema capture `captured`.

## SHA-256 evidence

The acceptance-generated `checksums.json` contains the per-gate hashes. The following final evidence hashes were independently checked with `Get-FileHash -Algorithm SHA256`:

```text
summary.json                                      EE09104A69F81206C794E33B0518ECA5D0F08DA25CABB0EEE1094E8EE0D8F790
checksums.json                                    ECFF61FEC35A41166A9F93EEEFAFB3C2EC126A04C80871F1FBB6CCB0CA161ABA
00-preflight/summary.json                         89207C9DDA7EECB19827165880BECF0459605BD0FC4B8E333A0CCBE5D37C9B1E
06-serving-sync/summary.json                      781A2362C65B265AA24E71310B6675E47387C954CD7D71CF6C1B9D6F4DC08798
07-dbt-and-stable-views/summary.json              CDEA9EC70DCCFDDF550EAB2D36F5E11A9B7228CECC9F39D32C3307622ED9636B
08-additive-schema/summary.json                   432AF1EE8275C7CA05BA062C4A880D793E66135A437A5A0282C53F143B78115B
09-rebuild/summary.json                           F8459B071B61BB58F300275E126A638B4BE7F0D7D0FFB23BE22F64A9598EF04E
10-final/summary.json                             817E84B08420285EDF366DC89F60C245248A3B62E6C1F3E9383814EDF87CC2FA
runtime_cleanup.json                              F5A1E96BE877800A4B4BA6245DD9D186B3BD26EFCD291109BCE9864A5DA905CD
```

## Cleanup and promotion boundary

Exact cleanup command recorded by the harness:

```text
uv run python scripts/cdc/local_lab.py down
```

Cleanup result: exit 0, `status=ready`, `runtime_cleanup.status=PASS`, scoped to `olist_local_cdc_acceptance`, `volumes_preserved=true`. No live GCP resources or production GCP runs are claimed by this local report.

WP3 remains blocked whenever any required WP0-WP2 scenario is unproved. The required WP0-WP2 scenarios are proved by the final run, but this report does not authorize WP3; that requires its separate gate and go/no-go decision.
