# Детальный план Stage F0: фиксация frozen baseline из `main`

- **Статус**: `PENDING`, выполняется после повторной приёмки E/V и до Stage L.
- **Baseline commit**: `1400d08345ad81a0121f0ee85ee9ae81cd575a73` (зафиксированный последний commit `main` на момент планирования).
- **Fixture**: `tests/fixtures/olist_small/olist_small.zip`.
- **Fixture SHA-256**: `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976`.

---

## 1. Решение

Legacy-контур запускается один раз из отдельного Git worktree на точном commit SHA. Его канонический результат сохраняется в репозитории как неизменяемый oracle. После этого Stage L может удалить legacy-файлы из рабочей ветки, а Stage F1 запускает только candidate и сравнивает его с oracle.

Это быстрее и проще, чем при каждом финальном тесте заново собирать две архитектуры. История Git остаётся источником воспроизводимости, но не входит в обычный путь F1.

Существующий `tests/fixtures/postgresql_oracle/postgres_batch_oracle.json` нельзя принять автоматически: он содержит legacy-specific surrogate/date keys, не покрывает единым контрактом восемь current-state сущностей и не имеет достаточных provenance metadata.

---

## 2. Артефакты F0

Должны быть добавлены:

- `tests/fixtures/final_parity/main-1400d08.json` — канонические строки и агрегаты;
- `tests/fixtures/final_parity/main-1400d08.metadata.json` — provenance и контрольные суммы;
- `docs/reports/mysql-spark-iceberg-f0-baseline.md` — человекочитаемый отчёт одноразового запуска.

Metadata обязана содержать:

- полный baseline commit SHA;
- fixture path и SHA-256;
- версии Docker images и инструментов;
- UTC timestamps начала/завершения;
- перечень таблиц, grains, колонок и row counts;
- SHA-256 каждого канонического набора строк;
- версию правил canonicalization;
- итоговый статус экспорта.

---

## 3. Порядок выполнения

1. Проверить, что E/V повторно приняты и candidate commit зафиксирован.
2. Проверить полный baseline SHA и fixture SHA-256; symbolic `main` после этого не используется.
3. Создать временный worktree вне дерева candidate на commit `1400d083...`.
4. Назначить уникальный `COMPOSE_PROJECT_NAME`, отдельные volumes и свободные порты.
5. Поднять legacy stack последовательно, загрузить неизменённый fixture и дождаться завершения batch/dbt пути.
6. Экспортировать восемь исходных сущностей, `fact_order_items`, `mart_daily_revenue` и `mart_monthly_arpu`.
7. Применить правила canonicalization из final-parity contract.
8. Проверить уникальность grain, отсутствие неразрешённых колонок и согласованность row counts/hash/rows.
9. Записать oracle, metadata и отчёт; повторно прочитать их независимым валидатором.
10. Выполнить `docker compose down -v` только для F0 project и удалить временный worktree.
11. Просмотреть diff oracle: секреты, абсолютные пути, нестабильные timestamps и runtime IDs запрещены.
12. Зафиксировать oracle отдельным reviewable commit до начала Stage L.

---

## 4. Поверхность сравнения

| Класс | Наборы | Grain |
| --- | --- | --- |
| Current state | `customers`, `orders`, `order_items`, `order_payments`, `order_reviews`, `products`, `sellers`, `product_category_translation` | естественные ключи из final-parity contract |
| Fact | `fact_order_items` | `order_id, order_item_id` |
| Marts | `mart_daily_revenue`, `mart_monthly_arpu` | `order_purchase_date`; `order_month` |

Сравниваются только явно перечисленные бизнес-колонки. Технические batch IDs, surrogate/date keys, load timestamps, binlog coordinates и engine-specific metadata в oracle не включаются.

---

## 5. Защита baseline

- Oracle никогда не регенерируется автоматически в PR или push CI.
- Изменение oracle требует ручного запуска F0 с тем же baseline commit либо отдельного архитектурного решения о смене baseline.
- Изменение только checksum без соответствующих канонических строк запрещено.
- При расхождении F1 исправляется candidate; oracle не подгоняется под результат.
- Git LFS не требуется, пока размер JSON позволяет обычный code review.

---

## 6. Критерии завершения

F0 завершена, если oracle и metadata проходят независимую валидацию, отчёт имеет `PASS`, cleanup выполнен, а review подтверждает отсутствие нестабильных/технических полей. После этого legacy runtime больше не является precondition для F1 и разрешён Stage L.

---

## 7. Связанные документы

- [Контракт финального паритета](../contracts/final-parity.md)
- [План Stage F1](stage-f1-final-parity.md)
- [Координационный план](serving-cutover.md)
