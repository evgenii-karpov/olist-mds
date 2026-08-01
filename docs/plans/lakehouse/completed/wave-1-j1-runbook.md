# J1 runbook: финализация MySQL → Kafka → Spark/Iceberg Wave 1

- **Status**: Completed / Frozen
- **Purpose**: Historical execution and acceptance runbook for Wave 1/J1
- **Active instruction**: No
- **Evidence**: [docs/reports/mysql-spark-iceberg-wave1-j1-validation.md](../../../reports/mysql-spark-iceberg-wave1-j1-validation.md)
- **Implementation commits**: `6088ebe3dcaee0345bedfb0524caa4aa96842e50`, `b1cd1ab1b6f59166aa6dfad60bc02419bd0bfcf8`

---

Основной архитектурный источник:
[`mysql-spark-iceberg-lakehouse-migration.md`](../../mysql-spark-iceberg-lakehouse-migration.md).
Этот документ описывает исторический порядок выполнения J1-сведений и является архивным материалом.

## 1. Миссия J1

Завершить **только J1**:

1. Зафиксировать уже написанные component changes потоков A-D.
2. Один раз объединить shared dependencies и обновить `uv.lock`.
3. Собрать новый platform runtime в `compose.yaml`.
4. Перевести `scripts/cdc/local_lab.py` на Wave 1 lifecycle.
5. Поднять чистый disposable Docker consistency domain.
6. Проверить MySQL, Kafka, Connect, Apicurio, MinIO, Polaris, Spark/Iceberg и ClickHouse реальными component smoke tests.
7. Получить из работающего Debezium/Apicurio все реальные writer schemas, сохранить evidence bundle и выпустить contract version `v2`.
8. Зафиксировать общий Spark normalization API для будущих Wave 2 agents.
9. Сохранить validation report без секретов и создать тематические commits.

## 2. Исходное состояние

P0 зафиксирован коммитом: `685cd6f docs: add mysql spark iceberg migration plans`.

Component code A-D (владение путями):
- A: `infra/mysql/**`, `scripts/simulation/**`, `tests/mysql/**`
- B: `streaming/kafka/**`, `streaming/connect/**`, `streaming/schemas/**`, `tests/cdc_contracts/**`
- C: `docker/spark/**`, `infra/polaris/**`, `streaming/spark/platform/**`, `tests/lakehouse_platform/**`
- D: `infra/clickhouse/lakehouse/**`, `dbt/olist_clickhouse/**`, `tests/dbt_clickhouse/**`

## 3. Непереговорные правила

1. Все persisted services входят в один disposable consistency domain.
2. Потеря/рассогласование authoritative volume требует полного `reset --yes`.
3. Пароли, tokens и secrets передаются строго через `*_FILE`.
4. Складские данные (warehouse) доступны строго через vended credentials от Polaris.

## 4. Обязательные deliverables

1. Обновлённые `pyproject.toml` и `uv.lock`.
2. Валидный `compose.yaml` с профилями `platform`, `streaming`, `serving`, `observability`.
3. Реализация Wave 1 lifecycle в `scripts/cdc/local_lab.py`.
4. Изолированные Polaris credential projections.
5. Реально применённая Iceberg migration `0001_initial_lakehouse`.
6. Созданный ClickHouse DataLakeCatalog `lakehouse`.
7. Writer-schema evidence repository и контракт `v2`.
8. Validation report `docs/reports/mysql-spark-iceberg-wave1-j1-validation.md`.

## 5. Итог выполнения J1

Wave 1 и J1 успешно выполнены и зафиксированы отчетом [docs/reports/mysql-spark-iceberg-wave1-j1-validation.md](../../../reports/mysql-spark-iceberg-wave1-j1-validation.md).
