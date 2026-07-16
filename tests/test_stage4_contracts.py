from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from pathlib import Path

from scripts.cdc.warehouse_ingest import (
    COMMON_COLUMNS,
    Manifest,
    Selector,
    gap_ranges,
    merge_ranges,
    missing_ranges,
    object_matches_selector,
    offsets_to_ranges,
    parse_coverage_manifest,
    parse_manifest,
    validate_coverage_landing_manifest,
    validate_coverage_location,
    validate_manifest_location,
    validate_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def manifest_payload(**overrides):
    value = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "normalized",
        "table": "customers",
        "topic": "olist_cdc.public.customers",
        "partition": 0,
        "schema_id": "42",
        "covered_offset_ranges": [[7, 8]],
        "row_count": 2,
        "operation_counts": {"r": 2},
        "source_ts_min": "2026-07-16T10:00:00+00:00",
        "source_ts_max": "2026-07-16T10:00:00+00:00",
        "closed_at": "2026-07-16T10:00:02+00:00",
        "object": {
            "uri": "s3://olist-cdc/stage/cdc/table=customers/event_date=2026-07-16/hour=10/file.parquet",
            "etag": "etag",
            "sha256": "a" * 64,
            "size_bytes": 123,
        },
    }
    value.update(overrides)
    return value


def customer_row(offset: int) -> dict:
    metadata = {
        "_event_id": f"olist_cdc.public.customers:0:{offset}",
        "_op": "r",
        "_source_ts": datetime(2026, 7, 16, 10, 0, tzinfo=UTC),
        "_source_lsn": 100 + offset,
        "_tx_id": None,
        "_tx_order": None,
        "_topic": "olist_cdc.public.customers",
        "_partition": 0,
        "_offset": offset,
        "_kafka_ts": datetime(2026, 7, 16, 10, 0, tzinfo=UTC),
        "_key_schema_id": 1,
        "_schema_id": 42,
        "_nifi_written_at": datetime(2026, 7, 16, 10, 1, tzinfo=UTC),
    }
    self = {
        "customer_id": f"customer-{offset}",
        "customer_unique_id": f"unique-{offset}",
        "customer_zip_code_prefix": "01001",
        "customer_city": "sao paulo",
        "customer_state": "SP",
    }
    return {**self, **metadata}


def coverage_payload(**overrides):
    value = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "coverage",
        "table": "customers",
        "topic": "olist_cdc.public.customers",
        "partition": 0,
        "consumed_offset_ranges": [[7, 9]],
        "business_event_offset_ranges": [[7, 7], [9, 9]],
        "tombstone_offset_ranges": [[8, 8]],
        "consumed_row_count": 3,
        "business_event_count": 2,
        "tombstone_count": 1,
        "closed_at": "2026-07-16T10:00:02+00:00",
        "landing_manifest": {
            "uri": "s3://olist-cdc/manifests/cdc/kind=landing/table=customers/ingest_date=2026-07-16/hour=10/file.manifest.json",
            "etag": "landing-manifest-etag",
        },
        "landing_object": {
            "uri": "s3://olist-cdc/landing/debezium/table=customers/event_date=2026-07-16/hour=10/file.avro",
            "etag": "landing-etag",
            "sha256": "b" * 64,
            "size_bytes": 456,
        },
    }
    value.update(overrides)
    return value


def landing_manifest_payload(**overrides):
    coverage = coverage_payload()
    value = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "landing",
        "table": coverage["table"],
        "topic": coverage["topic"],
        "partition": coverage["partition"],
        "covered_offset_ranges": coverage["consumed_offset_ranges"],
        "row_count": coverage["consumed_row_count"],
        "object": coverage["landing_object"],
    }
    value.update(overrides)
    return value


class ManifestContractTests(unittest.TestCase):
    def test_valid_manifest_and_rows_reconcile_exactly(self) -> None:
        uri = (
            "s3://olist-cdc/manifests/cdc/kind=normalized/table=customers/"
            "ingest_date=2026-07-16/hour=10/file.manifest.json"
        )
        manifest = parse_manifest(
            uri, "manifest-etag", json.dumps(manifest_payload()).encode()
        )
        validate_manifest_location(manifest, "olist-cdc")
        validate_rows(manifest, [customer_row(7), customer_row(8)])
        self.assertEqual("42", manifest.schema_id)
        self.assertEqual(((7, 8),), manifest.offset_ranges)
        self.assertEqual(13, len(COMMON_COLUMNS))

    def test_manifest_rejects_count_and_offset_mismatch(self) -> None:
        payload = manifest_payload(row_count=3)
        with self.assertRaisesRegex(ValueError, "offset coverage"):
            parse_manifest(
                "s3://olist-cdc/manifest.json", "etag", json.dumps(payload).encode()
            )

    def test_manifest_cannot_escape_configured_bucket_or_layout(self) -> None:
        manifest = Manifest(
            manifest_uri=(
                "s3://olist-cdc/manifests/cdc/kind=normalized/table=customers/"
                "ingest_date=2026-07-16/hour=10/file.manifest.json"
            ),
            manifest_etag="etag",
            object_uri="s3://other/stage/cdc/table=customers/event_date=2026-07-16/file.parquet",
            object_etag="etag",
            object_sha256="a" * 64,
            object_size_bytes=1,
            table="customers",
            topic="olist_cdc.public.customers",
            partition=0,
            offset_ranges=((1, 1),),
            schema_id="1",
            row_count=1,
            operation_counts={"r": 1},
            ingest_date=datetime(2026, 7, 16).date(),
            source_ts_min=None,
            source_ts_max=None,
            closed_at=datetime.now(UTC),
        )
        with self.assertRaisesRegex(ValueError, "configured bucket"):
            validate_manifest_location(manifest, "olist-cdc")

    def test_row_validation_rejects_wrong_event_identity(self) -> None:
        uri = "s3://olist-cdc/manifests/cdc/kind=normalized/table=customers/ingest_date=2026-07-16/hour=10/file.manifest.json"
        manifest = parse_manifest(uri, "etag", json.dumps(manifest_payload()).encode())
        rows = [customer_row(7), customer_row(8)]
        rows[1]["_event_id"] = "wrong"
        with self.assertRaisesRegex(ValueError, "_event_id"):
            validate_rows(manifest, rows)

    def test_coverage_manifest_reconciles_business_and_tombstones(self) -> None:
        uri = (
            "s3://olist-cdc/manifests/cdc/kind=coverage/table=customers/"
            "ingest_date=2026-07-16/hour=10/file.coverage.json"
        )
        coverage = parse_coverage_manifest(
            uri, "coverage-etag", json.dumps(coverage_payload()).encode()
        )
        validate_coverage_location(coverage, "olist-cdc")
        self.assertEqual(((8, 8),), coverage.tombstone_offset_ranges)
        self.assertEqual(3, coverage.consumed_row_count)

    def test_coverage_manifest_rejects_unclassified_offsets(self) -> None:
        payload = coverage_payload(tombstone_offset_ranges=[])
        with self.assertRaisesRegex(ValueError, "does not equal consumed"):
            parse_coverage_manifest(
                "s3://olist-cdc/manifests/cdc/kind=coverage/table=customers/ingest_date=2026-07-16/hour=10/file.coverage.json",
                "etag",
                json.dumps(payload).encode(),
            )

    def test_coverage_reconciles_to_referenced_landing_manifest(self) -> None:
        coverage = parse_coverage_manifest(
            "s3://olist-cdc/manifests/cdc/kind=coverage/table=customers/ingest_date=2026-07-16/hour=10/file.coverage.json",
            "coverage-etag",
            json.dumps(coverage_payload()).encode(),
        )
        validate_coverage_landing_manifest(
            coverage,
            "landing-manifest-etag",
            json.dumps(landing_manifest_payload()).encode(),
        )
        with self.assertRaisesRegex(ValueError, "offset ranges"):
            validate_coverage_landing_manifest(
                coverage,
                "landing-manifest-etag",
                json.dumps(
                    landing_manifest_payload(covered_offset_ranges=[[7, 8]])
                ).encode(),
            )


class OffsetCoverageTests(unittest.TestCase):
    def test_out_of_order_ranges_merge_and_report_then_close_gap(self) -> None:
        merged = merge_ranges([(5, 7), (0, 2)])
        self.assertEqual([(0, 2), (5, 7)], merged)
        self.assertEqual([(3, 4)], gap_ranges(merged))
        closed = merge_ranges([*merged, (3, 4)])
        self.assertEqual([(0, 7)], closed)
        self.assertEqual([], gap_ranges(closed))

    def test_missing_ranges_includes_unproven_tail(self) -> None:
        self.assertEqual([(2, 3), (6, 6)], missing_ranges([(0, 1), (4, 5)], 0, 6))

    def test_exact_ranges_preserve_non_contiguous_offsets(self) -> None:
        self.assertEqual(((1, 2), (4, 4), (9, 10)), offsets_to_ranges([10, 1, 4, 2, 9]))

    def test_selector_uses_manifest_ingest_date(self) -> None:
        key = "manifests/cdc/kind=normalized/table=orders/ingest_date=2026-07-16/hour=10/a.manifest.json"
        self.assertTrue(
            object_matches_selector(
                key,
                Selector(
                    table="orders",
                    date_from=datetime(2026, 7, 16).date(),
                    date_to=datetime(2026, 7, 16).date(),
                ),
            )
        )


class Stage4ConfigurationTests(unittest.TestCase):
    def test_bootstrap_contains_all_typed_raw_and_audit_tables(self) -> None:
        ddl = (ROOT / "infra/postgres/006_create_cdc_tables.sql").read_text(
            encoding="utf-8"
        )
        for table in (
            "customers",
            "orders",
            "order_items",
            "order_payments",
            "order_reviews",
            "products",
            "sellers",
            "product_category_translation",
        ):
            self.assertIn(f"raw_cdc.{table}", ddl)
        for table in (
            "cdc_ingest_runs",
            "cdc_files",
            "cdc_file_attempts",
            "cdc_coverage_files",
            "cdc_offset_coverage",
            "cdc_partition_watermarks",
            "cdc_reconciliation",
            "cdc_replay_requests",
        ):
            self.assertIn(f"cdc_audit.{table}", ddl)

    def test_compose_uses_separate_read_only_minio_loader_identity(self) -> None:
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        policy = (ROOT / "streaming/minio/cdc-loader-policy.json").read_text(
            encoding="utf-8"
        )
        self.assertIn("olist_cdc_loader", compose)
        self.assertIn("cdc-pipeline-exporter", compose)
        self.assertNotIn("s3:PutObject", policy)

    def test_airflow_contract_has_scheduled_ingest_and_manual_backfill(self) -> None:
        dag = (ROOT / "airflow/dags/olist_cdc_local.py").read_text(encoding="utf-8")
        self.assertIn('INGEST_DAG_ID = "olist_cdc_ingest_local"', dag)
        self.assertIn('BACKFILL_DAG_ID = "olist_cdc_backfill_local"', dag)
        self.assertIn('schedule="*/2 * * * *"', dag)
        self.assertIn("max_active_runs=1", dag)


if __name__ == "__main__":
    unittest.main()
