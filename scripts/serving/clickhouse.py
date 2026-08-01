"""ClickHouse candidate materialization, marker publication and rebuild helpers."""

from __future__ import annotations

import contextlib
import json
import logging
import urllib.request

from scripts.serving.entities import ServingEntitySpec
from scripts.serving.models import ServingSyncReport

logger = logging.getLogger(__name__)


def get_clickhouse_url() -> str:
    host = "127.0.0.1"
    port = 8123
    return f"http://{host}:{port}"


def clickhouse_query(
    sql: str, params: dict[str, str | int | float] | None = None
) -> list[dict[str, object]]:
    url = f"{get_clickhouse_url()}/?default_format=JSON"
    data = sql.encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return []
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                data_val = parsed.get("data")
                if isinstance(data_val, list):
                    return [item for item in data_val if isinstance(item, dict)]
            return []
    except Exception as exc:
        logger.error("ClickHouse query error: %s", exc)
        raise


class ClickHouseServingMaterializer:
    @staticmethod
    def materialize_entity_events(
        spec: ServingEntitySpec,
        sync_run_seq: int,
        sync_run_id: str,
        target_transaction_id: str | None = None,
    ) -> int:
        # Drop candidate partition if exists
        drop_sql = f"ALTER TABLE {spec.ch_events_table} DROP PARTITION {sync_run_seq}"
        with contextlib.suppress(Exception):
            clickhouse_query(drop_sql)

        cols = ", ".join(spec.business_columns)

        insert_sql = f"""
        INSERT INTO {spec.ch_events_table} (
            event_id, op_type, source_ts_ms, kafka_timestamp, {cols}, sync_run_seq, sync_run_id
        )
        SELECT
            event_id, op_type, source_ts_ms, kafka_timestamp, {cols}, {sync_run_seq}, '{sync_run_id}'
        FROM {spec.changes_relation}
        """
        clickhouse_query(insert_sql)

        count_sql = f"SELECT count() as cnt FROM {spec.ch_events_table} WHERE sync_run_seq = {sync_run_seq}"
        res = clickhouse_query(count_sql)
        cnt_val = res[0].get("cnt") if res else None
        return int(cnt_val) if isinstance(cnt_val, (int, str, float)) else 0

    @staticmethod
    def materialize_entity_current(
        spec: ServingEntitySpec,
        sync_run_seq: int,
        sync_run_id: str,
    ) -> int:
        drop_sql = f"ALTER TABLE {spec.ch_current_versions_table} DROP PARTITION {sync_run_seq}"
        with contextlib.suppress(Exception):
            clickhouse_query(drop_sql)

        cols = ", ".join(spec.business_columns)
        pk_cols = ", ".join(spec.primary_key)

        insert_sql = f"""
        INSERT INTO {spec.ch_current_versions_table} (
            {pk_cols}, op_type, is_deleted, kafka_offset, {cols}, sync_run_seq, sync_run_id
        )
        SELECT
            {pk_cols}, op_type, if(op_type = 'delete', 1, 0) as is_deleted, 1 as kafka_offset, {cols}, {sync_run_seq}, '{sync_run_id}'
        FROM {spec.ch_events_table}
        WHERE sync_run_seq = {sync_run_seq}
        """
        clickhouse_query(insert_sql)

        count_sql = f"SELECT count() as cnt FROM {spec.ch_current_versions_table} WHERE sync_run_seq = {sync_run_seq}"
        res = clickhouse_query(count_sql)
        cnt_val = res[0].get("cnt") if res else None
        return int(cnt_val) if isinstance(cnt_val, (int, str, float)) else 0

    @staticmethod
    def publish_marker(report: ServingSyncReport) -> None:
        published_at_str = report.published_at
        canonical_json = json.dumps(report.to_canonical_dict())

        insert_sql = f"""
        INSERT INTO serving_control.published_runs (
            sync_run_seq, sync_run_id, previous_transaction_id, target_transaction_id,
            publication_status, source_snapshot_completed, published_at, report_json
        ) VALUES (
            {report.sync_run_seq},
            '{report.sync_run_id}',
            {f"'{report.previous_transaction_id}'" if report.previous_transaction_id else "NULL"},
            {f"'{report.target_transaction_id}'" if report.target_transaction_id else "NULL"},
            'PUBLISHED',
            1,
            parseDateTime64BestEffort('{published_at_str}'),
            '{canonical_json}'
        )
        """
        clickhouse_query(insert_sql)
