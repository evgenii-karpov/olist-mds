# Технический контракт: Финальный паритетный тест (Final Parity Contract)

- **Статус**: Действующий нормативный контракт (Active normative contract)
- **Назначение**: Фиксация требований к исполнителю финального теста паритета (`run_mysql_iceberg_final_parity.py`), правилам сравнения данных между исходным (legacy) и целевым (candidate) контурами.
- **Порядок авторитетности**: Определяет действующие нормативные требования к заключительной приемке системы на этапе F.

---

## 1. Алгоритм работы Parity Runner (`run_mysql_iceberg_final_parity.py`)

1. Проверка состояния рабочей директории кандидата и хэша SHA-256 файла тестовых фикстур.
2. Создание временного изолированного worktree для базового (legacy) коммита.
3. Запуск legacy-стека с `COMPOSE_PROJECT_NAME=olist_parity_legacy`.
4. Выполнение полного пакета пакетов batch-versus-CDC.
5. Экспорт канонического JSON отчета legacy-контура.
6. Выполнение `docker compose down -v` для legacy-контура.
7. Запуск очищенного целевого кандидата с `COMPOSE_PROJECT_NAME=olist_parity_candidate`.
8. Загрузка того же набора фикстур (`seed`).
9. Ожидание нормализации в Silver, выполнение синхронизации витрин и dbt.
10. Экспорт канонического JSON отчета кандидата.
11. Построчное сравнение данных и формирование итогового отчета.
12. Выполнение `docker compose down -v` для кандидата.
13. Удаление временного worktree.

### 1.1 Правила выполнения

- Исходный и целевой контуры запускаются **последовательно**, а не одновременно.
- Исполнитель паритетного теста требует явного флага `--confirm-destructive`.
- Скрипт очищает только собственное окружение Docker Compose.

---

## 2. Предмет сравнения (Comparison Surface)

### 2.1 Текущее состояние сущностей (Current State)

Сравниваются все бизнес-колонки следующих сущностей:

| Сущность | Первичный ключ (Grain) |
| --- | --- |
| `customers` | `customer_id` |
| `orders` | `order_id` |
| `order_items` | `order_id, order_item_id` |
| `order_payments` | `order_id, payment_sequential` |
| `order_reviews` | `review_id, order_id` |
| `products` | `product_id` |
| `sellers` | `seller_id` |
| `product_category_translation` | `product_category_name` |

Источники сравнения:
- **Baseline**: `connection=oltp-postgres, database=olist_oltp, schema=public, table=<entity>`
- **Candidate**: `silver.<entity>_current` где `is_deleted = false`

Служебные метаданные транспортировки, binlog и загрузки не сравниваются.

### 2.2 Таблицы фактов (Fact)

Сравниваются `baseline core.fact_order_items` и `candidate gold.fact_order_items` по ключу `order_id, order_item_id`.

Сравниваемые нетехнические бизнес-колонки:
`customer_id`, `customer_unique_id`, `product_id`, `seller_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`, `shipping_limit_date`, `price`, `freight_value`, `gross_item_amount`, `allocated_payment_value`, `delivery_days`, `delivery_delay_days`, `is_delivered_late`.

Суррогатные ключи, ключи дат, идентификаторы батчей и метки времени загрузки не сравниваются.

### 2.3 Витрины данных (Marts)

Сравниваются таблицы `baseline marts.<model>` и `candidate gold.<model>`:

1. `mart_daily_revenue`
   - Ключ: `order_purchase_date`
   - Колонки: `order_purchase_date`, `gross_revenue`, `allocated_payment_revenue`, `product_revenue`, `freight_revenue`, `orders_count`, `customers_count`, `items_count`, `average_order_value`, `average_paid_order_value`, `average_delivery_days`, `late_deliveries_count`
2. `mart_monthly_arpu`
   - Ключ: `order_month`
   - Колонки: `order_month`, `active_customers`, `total_revenue`, `arpu`, `orders_count`, `orders_per_customer`, `average_order_value`, `repeat_customer_rate`

---

## 3. Правила канонизации данных (Canonicalization Rules)

Разрешены строго следующие приведения типов:
- Метки времени (Timestamps) → UTC ISO-8601 с 6 знаками микросекунд;
- Дробные числа (Decimals) → фиксированная точность контракта;
- Булевы значения (Booleans) → `true` / `false`;
- Сортировка → по естественному первичному ключу таблицы;
- Свойства JSON → в алфавитном порядке ключей.

Запрещено:
- Обрезка пробелов или изменение регистра строк;
- Подмена значений `null` дефолтными значениями;
- Дополнительное округление чисел;
- Исключение расходящихся строк;
- Приемка только по совпадению контрольной суммы (checksum-only acceptance).

---

## 4. Критерий успешности теста (Acceptance Decision)

Результат теста равен **PASS** только если одновременно:
1. Код завершения скрипта равен `0`;
2. Количество отсутствующих или лишних ключей равно `0`;
3. Количество расхождений по колонкам равно `0`.

При любом расхождении отчет получает статус **FAIL**, а выявленные дефекты исправляются в целевом кандидате с последующим повторным прогоном теста.

---

## 5. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт архитектуры и runtime](architecture-and-runtime.md)
- [Контракт валидации и CI](validation-and-ci.md)
- [Активный план E/L/V/F (Serving Cutover)](../active/serving-cutover.md)
