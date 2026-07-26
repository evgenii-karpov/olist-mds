from __future__ import annotations

import re
import unittest
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml
from scripts.cdc.warehouse_ingest import (
    ClickHouseRawCdcSink,
    Manifest,
    cdc_insert_token,
)

ROOT = Path(__file__).resolve().parents[1]


def manifest() -> Manifest:
    return Manifest(
        manifest_uri=(
            "s3://olist-cdc/manifests/cdc/kind=normalized/table=customers/"
            "ingest_date=2026-07-16/hour=10/file.manifest.json"
        ),
        manifest_etag="manifest-etag",
        object_uri=(
            "s3://olist-cdc/stage/cdc/table=customers/"
            "event_date=2026-07-16/hour=10/file.parquet"
        ),
        object_etag="object-etag",
        object_sha256="a" * 64,
        object_size_bytes=100,
        table="customers",
        topic="olist_cdc.public.customers",
        partition=0,
        offset_ranges=((7, 8),),
        schema_id="42",
        row_count=2,
        operation_counts={"r": 2},
        ingest_date=date(2026, 7, 16),
        source_ts_min=datetime(2026, 7, 16, 10, 0, tzinfo=UTC),
        source_ts_max=datetime(2026, 7, 16, 10, 1, tzinfo=UTC),
        closed_at=datetime(2026, 7, 16, 10, 2, tzinfo=UTC),
    )


def customer_row(offset: int) -> dict[str, Any]:
    return {
        "customer_id": f"customer-{offset}",
        "customer_unique_id": f"unique-{offset}",
        "customer_zip_code_prefix": "01001",
        "customer_city": "sao paulo",
        "customer_state": "SP",
        "_event_id": f"olist_cdc.public.customers:0:{offset}",
        "_op": "r",
        "_source_ts": datetime(2026, 7, 16, 10, offset - 7, tzinfo=UTC),
        "_source_lsn": 100 + offset,
        "_tx_id": None,
        "_tx_order": None,
        "_topic": "olist_cdc.public.customers",
        "_partition": 0,
        "_offset": offset,
        "_kafka_ts": datetime(2026, 7, 16, 10, offset - 7, tzinfo=UTC),
        "_key_schema_id": 1,
        "_schema_id": 42,
        "_nifi_written_at": datetime(2026, 7, 16, 10, 3, tzinfo=UTC),
    }


class FakeQueryResult:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self.result_rows = rows
        self.first_row = rows[0] if rows else None


class FakeClickHouseClient:
    def __init__(self) -> None:
        self.logical_rows: dict[tuple[str, int, int], dict[str, Any]] = {}
        self.insert_calls: list[dict[str, Any]] = []

    def query(self, query: str, *args: Any, **kwargs: Any) -> FakeQueryResult:
        if "SELECT _source_lsn, _source_ts" in query:
            max_offset = int(re.search(r"_offset <= (\d+)", query).group(1))  # type: ignore[union-attr]
            eligible = [
                row
                for (_, _, offset), row in self.logical_rows.items()
                if offset <= max_offset
            ]
            eligible.sort(key=lambda row: int(row["_offset"]), reverse=True)
            if not eligible:
                return FakeQueryResult([])
            row = eligible[0]
            return FakeQueryResult([(row["_source_lsn"], row["_source_ts"])])

        columns = [
            item.strip().strip("`")
            for item in query.split("SELECT ", 1)[1].split(" FROM ", 1)[0].split(",")
        ]
        rows = [
            tuple(row[column] for column in columns)
            for row in sorted(
                self.logical_rows.values(), key=lambda item: int(item["_offset"])
            )
        ]
        return FakeQueryResult(rows)

    def insert(self, *args: Any, **kwargs: Any) -> None:
        self.insert_calls.append(kwargs)
        columns = list(kwargs["column_names"])
        for values in kwargs["data"]:
            row = dict(zip(columns, values, strict=True))
            self.logical_rows[
                (str(row["_topic"]), int(row["_partition"]), int(row["_offset"]))
            ] = row

    def close(self) -> None:
        return None


class ClickHousePhase5CdcIngestionTests(unittest.TestCase):
    def test_insert_token_is_stable_and_manifest_bound(self) -> None:
        item = manifest()
        self.assertEqual(cdc_insert_token(item), cdc_insert_token(item))
        changed = replace(item, object_sha256="b" * 64)
        self.assertNotEqual(cdc_insert_token(item), cdc_insert_token(changed))

    def test_clickhouse_sink_counts_logical_duplicates_with_final_readback(
        self,
    ) -> None:
        item = manifest()
        client = FakeClickHouseClient()
        sink = ClickHouseRawCdcSink(client)
        rows = [customer_row(7), customer_row(8)]

        self.assertEqual((2, 0), sink.insert_file(item, rows))
        self.assertEqual((0, 2), sink.insert_file(item, rows))
        self.assertEqual(2, len(client.logical_rows))
        self.assertEqual(
            cdc_insert_token(item),
            client.insert_calls[0]["settings"]["insert_deduplication_token"],
        )

    def test_clickhouse_sink_rejects_existing_payload_mismatch(self) -> None:
        item = manifest()
        client = FakeClickHouseClient()
        sink = ClickHouseRawCdcSink(client)
        rows = [customer_row(7), customer_row(8)]
        sink.insert_file(item, rows)
        changed_rows = [dict(row) for row in rows]
        changed_rows[0]["customer_city"] = "rio de janeiro"

        with self.assertRaisesRegex(ValueError, "payload differs"):
            sink.insert_file(item, changed_rows)

    def test_cdc_dag_uses_clickhouse_sink_explicitly(self) -> None:
        dag = (ROOT / "airflow/dags/olist_cdc_local.py").read_text(encoding="utf-8")
        self.assertIn('"--warehouse-type"', dag)
        self.assertIn('"clickhouse"', dag)
        self.assertIn('"control-postgres"', dag)
        self.assertNotIn('"--bootstrap-sql-dir"', dag)

    def test_realtime_selection_projects_to_clickhouse_runtime_table(self) -> None:
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        macro = (ROOT / "dbt/olist_analytics/macros/realtime_cdc.sql").read_text(
            encoding="utf-8"
        )
        sources = (
            ROOT / "dbt/olist_analytics/models/realtime/staging/_realtime__sources.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("project_transform_selection", runtime)
        self.assertIn("pipeline_runtime", runtime)
        self.assertIn("manifest_selection_digest", runtime)
        self.assertIn("clickhouse__cdc_selected_file_predicate", macro)
        self.assertIn("source('pipeline_runtime', 'cdc_transform_run_files')", macro)
        self.assertIn("- name: pipeline_runtime", sources)

    def test_realtime_compose_init_no_longer_bootstraps_postgres_raw_cdc(self) -> None:
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
        service = compose["services"]["cdc-warehouse-init"]
        self.assertNotIn("postgres", service["depends_on"])
        self.assertIn("clickhouse-init", service["depends_on"])
        self.assertNotIn("postgres_password", service.get("secrets", []))
        self.assertNotIn("warehouse_ingest.py", " ".join(service["entrypoint"]))


if __name__ == "__main__":
    unittest.main()
