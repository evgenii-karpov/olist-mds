# Детальный план Stage F1: финальный candidate-only parity

- **Статус**: `PENDING`, выполняется после Stage L.
- **Назначение**: доказать бизнес-паритет очищенного candidate с frozen oracle F0 без запуска legacy runtime.

---

## 1. Preconditions

1. F0 oracle и metadata приняты и находятся в `tests/fixtures/final_parity`.
2. Stage L завершён, общий CI и component workflows зелёные.
3. Candidate указывается полным commit SHA; рабочее дерево не используется как неявный источник версии.
4. Fixture SHA совпадает со значением в metadata.
5. Доступен изолированный Docker runner с достаточным диском и уникальным Compose project.

---

## 2. Целевой CLI

```text
python scripts/cdc/local_lab.py final-parity \
  --run-id <unique-run-id> \
  --oracle tests/fixtures/final_parity/main-1400d08.json \
  --confirm-destructive \
  --timeout 5400
```

Команда должна запускать только candidate. Любая попытка создать legacy worktree или обратиться к symbolic `main` в F1 считается нарушением контракта.

---

## 3. Порядок выполнения

1. Проверить candidate SHA, oracle/metadata schema и все checksums.
2. Создать чистый Compose domain; выполнить scoped reset только для его ресурсов.
3. Поднять platform и streaming, загрузить тот же fixture.
4. Дождаться initial snapshot, committed Bronze/Silver progress и отсутствия rejects.
5. Выполнить finite serving sync по реальной boundary и `dbt build`.
6. Экспортировать candidate current state, fact и marts по тому же manifest, что использовался F0.
7. Канонизировать значения одинаковой версией правил.
8. Для каждого relation сравнить grain, набор ключей и каждую бизнес-колонку.
9. Записать machine-readable diff и Markdown summary.
10. Повторно проверить, что report status вычислен из diff, затем очистить Compose domain в любом исходе.

---

## 4. Обязательные артефакты

Каталог `data/reports/final-parity/<run-id>/` содержит:

- `preflight.json`;
- `candidate-manifest.json`;
- `comparison.json`;
- `report.md`;
- `junit.xml`;
- ограниченные логи только нужных сервисов при ошибке.

`comparison.json` для каждого relation содержит row counts, missing keys, extra keys, column mismatch count, bounded samples различий и SHA-256 канонических строк. Секреты, connection strings и полные environment dumps запрещены.

---

## 5. Решение PASS/FAIL

`PASS` возможен только при одновременном выполнении условий:

- process exit code `0`;
- все relations из manifest присутствуют;
- нет duplicate grain;
- `missing_keys = 0` и `extra_keys = 0`;
- `column_mismatches = 0`;
- fixture, baseline и canonicalization checksums совпадают с metadata;
- cleanup завершён либо отдельно отмечена инфраструктурная ошибка после уже вычисленного результата.

Checksum-only сравнение не является достаточным. При расхождении исправляется candidate и F1 повторяется с тем же oracle. Изменять F0 oracle для устранения расхождения запрещено.

---

## 6. Ручной GitHub workflow

F1 запускается job `final-parity` из `.github/workflows/lakehouse-acceptance.yml` с `suite=final-parity`. Workflow запускается только через `workflow_dispatch`, привязывает evidence к `candidate_sha`, сериализуется через concurrency и публикует артефакты даже при `FAIL`.

F1 не входит в обычный PR CI: его длительность, destructive reset и полный стек несоразмерны каждой правке. Обязательными PR-барьерами остаются общий CI и релевантные bounded components.

---

## 7. Критерии завершения программы

- F1 report имеет `PASS` и ссылается на точные candidate/baseline SHA;
- опубликованные machine-readable артефакты согласованы с Markdown report;
- повторный validator подтверждает решение;
- cleanup выполнен;
- итоговый отчёт добавлен в `docs/reports/`, а roadmap отмечает миграцию как завершённую.

---

## 8. Связанные документы

- [План F0](stage-f0-baseline-freeze.md)
- [Контракт финального паритета](../contracts/final-parity.md)
- [План CI cutover](stage-l-legacy-removal-ci-cutover.md)
