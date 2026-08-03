# Детальный план: повторная приёмка Stage E и Stage V

- **Статус**: `COMPLETE — CLEAN V0–V10 ACCEPTED`
- **Назначение**: устранить пробелы в реализации и доказательствах Stage E/V и получить воспроизводимый полный прогон V0–V10 до фиксации baseline и удаления legacy.
- **Граница стадии**: документ сохранён как frozen plan и содержит фактическое clean acceptance evidence ниже.

---

## 1. Почему стадия открыта повторно

Существующие отчёты Stage E и Stage V сохраняются как исторические evidence, однако пока не могут быть единственным основанием для destructive cleanup:

- отчёт Stage V содержит только evidence для подготовительных ворот V0/V1, но декларирует успех V0–V10;
- генератор отчёта допускает отсутствие ворот и формирует итоговый `PASS` без доказательства каждого обязательного шага;
- после ранних ворот сценарий не завершает выполнение немедленно при ошибке;
- control-plane bootstrap не доказывает применение миграции `005_create_serving_control_tables.sql`;
- граница serving-публикации строится без доказанных Kafka offsets и Iceberg snapshot IDs;
- Airflow/dbt runtime всё ещё должен быть окончательно переключён с `dbt/olist_analytics` на `dbt/olist_clickhouse`.

Поэтому статусы E/V переводятся в `REVALIDATION REQUIRED`. Это не отменяет выполненную разработку, а вводит недостающий барьер перед F0 и L.

---

## 2. Пакеты работ

### EV1 — сделать control plane исполнимым

1. Включить миграцию `infra/control-postgres/initdb/005_create_serving_control_tables.sql` в реальный bootstrap-порядок.
2. Ограничить grants целевыми схемами Airflow, Polaris, Apicurio и `olist_control.serving`.
3. Добавить автоматическую проверку версии схемы и обязательных таблиц/ограничений.
4. Проверить повторный запуск bootstrap без изменения уже применённой схемы.

**Выход**: машинно-читаемый evidence с перечнем применённых миграций и результатом schema assertions.

### EV2 — доказать конечную границу serving-транзакции

1. DAG `olist_lakehouse_serving_sync` получает реальные committed Kafka offsets и Iceberg snapshot IDs.
2. Пустые offsets/snapshots разрешены только для доказанного no-op, а не как обычный путь публикации.
3. `sync-serving` сверяет итоговый authoritative serving report, а не только статус Airflow run.
4. Поле `is_noop` вычисляется из фактической границы и опубликованной версии.
5. Повтор одного и того же boundary возвращает тот же результат без дублирования событий и Gold-версии.

**Выход**: accepted boundary, transaction ID, source offsets, snapshot IDs, candidate version и stable published version в одном JSON evidence.

### EV3 — завершить Airflow/dbt переключение

1. Airflow image и volumes содержат `dbt/olist_clickhouse`, а `DBT_PROFILES_DIR` указывает только на него.
2. В runtime отсутствуют обязательные зависимости от `dbt/olist_analytics`, Redshift и Elementary Redshift.
3. Импортируются ровно целевые DAGs:
   - `olist_lakehouse_serving_sync`;
   - `olist_lakehouse_quality`;
   - `olist_lakehouse_maintenance`;
   - `olist_lakehouse_serving_rebuild`.
4. Имена DAGs в коде, документации и CI совпадают.
5. `dbt deps`, `dbt parse` и candidate `dbt build` исполняются внутри того же образа, который использует DAG.

### EV4 — исправить Stage V harness

Harness обязан:

- иметь явный реестр обязательных ворот V0–V10;
- считать отсутствующее, пропущенное или дублированное ворото ошибкой;
- завершаться ненулевым кодом после первого обязательного `FAIL`;
- вычислять итоговый статус только из фактических результатов;
- не записывать hard-coded counts, IDs или формулировки успеха;
- сохранять команду, timestamps, duration, commit SHA, fixture SHA-256 и ссылки на артефакты;
- очищать только собственный Compose project в `finally`/`always()`;
- различать `PASS`, `FAIL`, `ERROR` и `SKIPPED`, причём `SKIPPED` обязательного ворота не допускает приёмку.

### EV5 — выполнить полный чистый прогон V0–V10

| Ворота | Обязательное доказательство |
| --- | --- |
| V0 — preflight | чистый/явно зафиксированный commit, fixture SHA, Docker resources, свободные project names |
| V1 — harness | полный реестр ворот, каталоги артефактов, таймауты и destructive confirmation |
| V2 — clean bootstrap | новый Compose domain и volumes, readiness всех platform-компонентов |
| V3 — initial load | seed, Debezium snapshot, 79 active entity rows, 6 reference rows, отсутствие rejects |
| V4 — CDC mutations | insert/update/delete/tombstone и точные ожидаемые изменения current/events |
| V5 — restart/catch-up | рестарт Bronze/Silver, отсутствие duplicate `event_id`, committed progress |
| V6 — serving sync | реальная frozen boundary, candidate publish, stable switch, корректный no-op повтор |
| V7 — dbt/quality | `dbt build`, schema/data tests и запросы к stable `gold`/`FINAL` |
| V8 — schema evolution | nullable additive column проходит Avro → Bronze → Silver → serving с `null` |
| V9 — rebuild | ClickHouse полностью очищен и восстановлен только из Iceberg |
| V10 — final assertions | все обязательные ворота присутствуют и `PASS`, отчёт согласован с raw evidence |

### EV6 — обновить evidence

1. Сформировать новый отчёт Stage E с фактическими командами и артефактами.
2. Перегенерировать отчёт Stage V только после завершения V10.
3. Не перезаписывать raw evidence успешными декларациями при ошибке.
4. Указать commit SHA, на котором был получен результат.

---

## 3. Проверки, которые должны появиться в автоматическом CI

В общий CI входят unit/contract проверки реестра ворот, fail-fast, применения migration 005, DAG inventory и запрета placeholder boundary. Полный V0–V10 остаётся ручным из-за длительности и destructive reset; его точный workflow описан в [Stage L / CI cutover](../active/stage-l-legacy-removal-ci-cutover.md).

---

## 4. Критерии завершения

Stage E/V считается повторно принятой только если:

1. все EV1–EV4 реализованы и покрыты автоматическими тестами;
2. один чистый прогон содержит ровно V0–V10 и все они имеют `PASS`;
3. отчёты Stage E/V построены из raw evidence и соответствуют ему;
4. повторная проверка отчёта отдельной командой возвращает `PASS`;
5. после завершения стенд очищен, а evidence сохранён;
6. только после этого разрешён переход к F0.

---

## 5. Связанные документы

- [Координационный план финальных стадий](../active/serving-cutover.md)
- [План фиксации baseline F0](../active/stage-f0-baseline-freeze.md)
- [Контракт Validation & CI](../contracts/validation-and-ci.md)

## 6. Фактическое подтверждение

- **Результат**: clean `PASS` для всех 11 обязательных ворот V0–V10; все 42 machine-readable assertions прошли.
- **Run ID**: `stage_v_clean_e113c55`.
- **Compose project**: `olist_stage_v`.
- **Commit SHA из V0**: `e113c552cca990636f426b827456a77ddc9d594b`.
- **V0 source tree**: `dirty=false`.
- **Evidence**: `data/stage-v-evidence/stage_v_clean_e113c55/`.
- **Отчёт**: `docs/reports/mysql-spark-iceberg-stage-v-validation.md`.
- **Независимая проверка отчёта**: отчёт сгенерирован из raw evidence clean run и содержит `PASS` по всем обязательным gate.
- **Evidence checksums**: SHA-256 созданы для всех 11 вложенных gate summaries.
- **Следующая стадия**: F0 — фиксация frozen baseline из `main`; Stage L и F1 остаются заблокированными до F0.

### 6.1 Историческая ручная post-fix проверка V06–V10

3 августа 2026 года V06–V10 были проверены отдельно в уже существующем Compose project `olist_stage_v`. Этот прогон не является clean-domain acceptance V0–V10: V06 использовал одну контролируемую source UPDATE, потому что исходные CRUD fixtures уже были израсходованы предыдущими попытками.

- **V06**: publish `sync_run_seq=6` (`is_noop=false`, boundary `file=binlog.000002,pos=38910`, `expected=materialized=90`) и repeat `sync_run_seq=7` (`NOOP`, та же boundary).
- **V07**: `validate-serving` для seq 6 подтвердил фактический `dbt build --selector serving_candidate`: 75 результатов (`16 success`, `59 pass`), stable current parity и все 8 Gold interfaces.
- **V08**: allowlisted nullable-column fixtures дали customer event offset 10, schema id 37, `NULL` в новой source column, `schema_violations=0`, `normalization_errors=0`; publish `sync_run_seq=9` дал `expected=materialized=91`, а повторная serving validation прошла.
- **V09**: rebuild `sync_run_seq=10` завершился `SUCCEEDED`, `expected=materialized=91`, с восемью Iceberg snapshots.
- **V10**: `local_lab.py status --require serving` и post-rebuild current/Gold parity завершились `PASS`.
- Все четыре serving DAGs имеют `schedule=None`, `is_paused=false`; контейнеры не останавливались.

Эта ручная проверка была промежуточным подтверждением и на момент выполнения не снимала требование EV5; последующий clean run в разделе 6.2 снял этот барьер.

### 6.2 Clean V0–V10 acceptance

3 августа 2026 года выполнен clean-domain run на commit `e113c552cca990636f426b827456a77ddc9d594b`.

- `00-preflight` зафиксировал `dirty=false` и точный execution commit.
- Все обязательные gate `00-preflight`–`10-final` завершились `PASS`; всего `42/42` assertions.
- V06 выполнил реальный non-NOOP sync (`seq=1`, `SUCCEEDED`, dbt: `16 success + 59 pass`), затем повтор boundary дал `seq=2`, `NOOP`.
- V08 подтвердил nullable Avro propagation (`schema_id=37`, `optional_value=null`, `schema_violations=0`, `normalization_errors=0`).
- V09 восстановил serving из Iceberg (`seq=4`, `expected_event_count=90`, `materialized_event_count=90`).
- V10 подтвердил `PUBLISHED`, пустые active/open/rejected control-plane sets и parity Iceberg/Stable/Gold.
- После завершения runtime cleanup выполнен только для Compose project `olist_stage_v`, volumes сохранены для диагностики/повторного использования.
