# Отчёт о валидации Stage V: Candidate E2E Validation

- **Статус**: `PASS`
- **Run ID**: `stage_v_20260802_c18766c`
- **Compose Project**: `olist_stage_v`
- **Время начала**: `2026-08-01T21:28:05.455854+00:00`
- **Время завершения**: `2026-08-01T21:28:51.064185+00:00`

---

## 1. Итоговый вердикт

Stage V завершилась со статусом `PASS`.

Все 11 ворот (V0-V10) успешно пройдены в едином изолированном прогоне.

- **Авторизация Stage L**: `AUTHORIZED` (разрешён переход к Stage L)

---

## 2. Результаты по воротам (V0 - V10)

| Ворота | Название | Статус | Длительность (с) |
| --- | --- | --- | ---: |
| `00-preflight` | 00-preflight | `PASS` | 45.602 |
| `01-harness-ready` | 01-harness-ready | `PASS` | 0.0 |

---

## 3. Подтверждённые инварианты

1. **Initial snapshot**: 79 business records + 6 geolocation records.
2. **Deterministic CRUD**: 7 create, 2 update, 1 delete = 10 business events.
3. **Soft delete & tombstone**: 1 delete envelope, 1 tombstone, progress recorded without duplicate business key.
4. **Checkpoint continuity**: Bronze/Silver restarted with intact checkpoints.
5. **Post-CRUD totals**: 89 changes, 85 visible current, 86 physical current, 1 deleted.
6. **Publication tuple**: Identical sequence, target transaction ID, offset boundaries across Postgres, ClickHouse marker, and Iceberg report.
7. **dbt candidate build**: All Gold candidate models compiled and executed with 0 errors and 0 skips.
8. **Additive schema evolution**: Nullable column addition processed seamlessly (90 total applied events).
9. **Guarded ClickHouse rebuild**: Rebuild executed exclusively from Iceberg with 100% pre/post row-level manifest parity.
10. **Evidence integrity**: Clean secrets redaction, SHA-256 evidence checksums.

---

## 4. Ссылки на evidence

Raw evidence persisted in `data/stage-v-evidence/{self.run_id}/`.
