# Технический контракт: финальный паритет (F0/F1)

- **Статус**: Действующий нормативный контракт.
- **Назначение**: определить создание frozen legacy baseline на F0 и итоговое candidate-only сравнение на F1.
- **Главный инвариант**: после принятия F0 финальный прогон не зависит от наличия legacy runtime в текущем дереве.

---

## 1. Разделение стадий

### F0 — одноразовый экспорт baseline до cleanup

Legacy запускается из временного worktree на полном commit `1400d08345ad81a0121f0ee85ee9ae81cd575a73`. Из результата строятся версионированные oracle и metadata. Symbolic branch `main` не используется после проверки SHA.

### F1 — итоговый тест после cleanup

Очищенный candidate запускается с тем же fixture, экспортирует ту же поверхность данных и сравнивается построчно с frozen oracle. F1 не создаёт worktree, не запускает legacy и не обновляет oracle.

---

## 2. Артефакты baseline

Нормативные пути:

- `tests/fixtures/final_parity/main-1400d08.json`;
- `tests/fixtures/final_parity/main-1400d08.metadata.json`.

Metadata фиксирует полный baseline SHA, fixture SHA-256, версию canonicalization, versions images/tools, relation manifest, grains, business columns, row counts и SHA-256 канонических строк.

Oracle считается неизменяемым входом F1. Его обновление требует повторного контролируемого F0 и review; автоматическая регенерация в CI запрещена.

---

## 3. Поверхность сравнения

### 3.1 Current state

| Сущность | Grain |
| --- | --- |
| `customers` | `customer_id` |
| `orders` | `order_id` |
| `order_items` | `order_id, order_item_id` |
| `order_payments` | `order_id, payment_sequential` |
| `order_reviews` | `review_id, order_id` |
| `products` | `product_id` |
| `sellers` | `seller_id` |
| `product_category_translation` | `product_category_name` |

Baseline берётся из бизнес-таблиц legacy PostgreSQL; candidate — из `silver.<entity>_current` с `is_deleted = false`. Сравниваются все явно описанные бизнес-колонки, но не transport/load metadata.

### 3.2 Fact

`fact_order_items`, grain `order_id, order_item_id`.

Бизнес-колонки: `customer_id`, `customer_unique_id`, `product_id`, `seller_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`, `shipping_limit_date`, `price`, `freight_value`, `gross_item_amount`, `allocated_payment_value`, `delivery_days`, `delivery_delay_days`, `is_delivered_late`.

Surrogate keys, date keys, batch IDs и load timestamps исключаются.

### 3.3 Marts

1. `mart_daily_revenue`, grain `order_purchase_date`:
   `order_purchase_date`, `gross_revenue`, `allocated_payment_revenue`, `product_revenue`, `freight_revenue`, `orders_count`, `customers_count`, `items_count`, `average_order_value`, `average_paid_order_value`, `average_delivery_days`, `late_deliveries_count`.
2. `mart_monthly_arpu`, grain `order_month`:
   `order_month`, `active_customers`, `total_revenue`, `arpu`, `orders_count`, `orders_per_customer`, `average_order_value`, `repeat_customer_rate`.

---

## 4. Canonicalization

Разрешены только:

- timestamp → UTC ISO-8601 с шестью знаками микросекунд;
- decimal → фиксированная точность контракта без дополнительного округления;
- boolean → `true`/`false`;
- строки и `null` сохраняются без trim/case/default substitutions;
- JSON object keys сортируются;
- строки relation сортируются по grain.

Версия правил и manifest должны совпадать у F0 exporter и F1 candidate exporter. Нельзя исключать расходящиеся строки или принимать результат только по checksum.

---

## 5. Контракт runner F1

Целевой интерфейс:

```text
python scripts/cdc/local_lab.py final-parity \
  --run-id <run-id> \
  --oracle tests/fixtures/final_parity/main-1400d08.json \
  --confirm-destructive \
  --timeout 5400
```

Runner обязан:

1. проверить candidate SHA, fixture/oracle/metadata checksums и schema;
2. создать уникальный candidate Compose project;
3. выполнить clean seed → stream catch-up → serving sync → dbt build;
4. экспортировать candidate по baseline manifest;
5. сравнить grain, ключи и значения каждой бизнес-колонки;
6. сохранить raw machine-readable diff до генерации summary;
7. вычислить exit code и `PASS/FAIL` только из diff;
8. очистить только собственные ресурсы при любом исходе.

---

## 6. Acceptance

`PASS` требует одновременно:

1. exit code `0`;
2. все relations присутствуют и grain уникален;
3. отсутствующих ключей `0`;
4. лишних ключей `0`;
5. расхождений по бизнес-колонкам `0`;
6. checksums provenance совпадают;
7. report согласован с raw diff.

При `FAIL` исправляется candidate и повторяется F1 с тем же oracle. Перегенерация oracle для получения `PASS` запрещена.

---

## 7. CI policy

F1 запускается только вручную job `final-parity` workflow `.github/workflows/lakehouse-acceptance.yml`. Он не входит в обычный PR CI. F0 не является регулярным GitHub workflow.

---

## 8. Связанные документы

- [План F0](../active/stage-f0-baseline-freeze.md)
- [План F1](../active/stage-f1-final-parity.md)
- [Контракт Validation & CI](validation-and-ci.md)
- [Координационный план](../active/serving-cutover.md)
