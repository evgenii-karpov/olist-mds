"""Run bounded ClickHouse CDC ingest resilience checks.

This is the Phase 8 replacement for the old PostgreSQL Stage 4 integration
check. It uses the production ClickHouse raw CDC sink and PostgreSQL
control-plane audit tables, then exercises retry, offset coverage, watermark
closing, and replay.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pyarrow as pa
import pyarrow.parquet as parquet
from scripts.cdc.warehouse_ingest import (
    BUSINESS_COLUMNS,
    ClickHouseRawCdcSink,
    Selector,
    add_clickhouse_args,
    clickhouse_client,
    ingest,
    request_replay,
    s3_client,
)
from scripts.orchestration.control_postgres import (
    add_control_postgres_args,
    control_connection,
)

TABLE = "customers"
TOPIC = f"olist_cdc.public.{TABLE}"
PARTITION = 0
SCHEMA_ID = 1001
INGEST_DATE = "2026-07-16"
HOUR = "10"
BASE_TS = datetime(2026, 7, 16, 10, 0, tzinfo=UTC)


def utc_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def offset_ranges(offsets: list[int]) -> list[list[int]]:
    ranges: list[list[int]] = []
    for offset in sorted(set(offsets)):
        if not ranges or offset > ranges[-1][1] + 1:
            ranges.append([offset, offset])
        else:
            ranges[-1][1] = offset
    return ranges


def customer_row(offset: int) -> dict[str, Any]:
    source_ts = BASE_TS + timedelta(seconds=offset)
    return {
        "customer_id": f"c{offset}",
        "customer_unique_id": f"u{offset}",
        "customer_zip_code_prefix": "01001",
        "customer_city": f"city-{offset}",
        "customer_state": "SP",
        "_event_id": f"{TOPIC}:{PARTITION}:{offset}",
        "_op": "c",
        "_source_ts": source_ts,
        "_source_lsn": 10_000 + offset,
        "_tx_id": 20_000 + offset,
        "_tx_order": offset,
        "_topic": TOPIC,
        "_partition": PARTITION,
        "_offset": offset,
        "_kafka_ts": source_ts + timedelta(milliseconds=10),
        "_key_schema_id": SCHEMA_ID - 1,
        "_schema_id": SCHEMA_ID,
        "_nifi_written_at": source_ts + timedelta(milliseconds=20),
    }


def parquet_bytes(rows: list[dict[str, Any]]) -> bytes:
    table = pa.Table.from_pylist(
        rows,
        schema=pa.schema(
            [
                *[(column, pa.string()) for column in BUSINESS_COLUMNS[TABLE]],
                ("_event_id", pa.string()),
                ("_op", pa.string()),
                ("_source_ts", pa.timestamp("us", tz="UTC")),
                ("_source_lsn", pa.int64()),
                ("_tx_id", pa.int64()),
                ("_tx_order", pa.int64()),
                ("_topic", pa.string()),
                ("_partition", pa.int32()),
                ("_offset", pa.int64()),
                ("_kafka_ts", pa.timestamp("us", tz="UTC")),
                ("_key_schema_id", pa.int32()),
                ("_schema_id", pa.int32()),
                ("_nifi_written_at", pa.timestamp("us", tz="UTC")),
            ]
        ),
    )
    buffer = io.BytesIO()
    parquet.write_table(table, buffer, compression="zstd")
    return buffer.getvalue()


def put_json(client, bucket: str, key: str, payload: dict[str, Any]) -> str:
    response = client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload, sort_keys=True).encode("utf-8"),
        ContentType="application/json",
    )
    return str(response["ETag"]).strip('"')


def put_bytes(client, bucket: str, key: str, body: bytes) -> tuple[str, str, int]:
    digest = hashlib.sha256(body).hexdigest()
    response = client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        Metadata={"sha256": digest},
    )
    return str(response["ETag"]).strip('"'), digest, len(body)


def ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
    except Exception:
        client.create_bucket(Bucket=bucket)


def put_normalized_manifest(
    client,
    bucket: str,
    *,
    stem: str,
    offsets: list[int],
) -> str:
    rows = [customer_row(offset) for offset in offsets]
    object_key = (
        f"stage/cdc/table={TABLE}/event_date={INGEST_DATE}/hour={HOUR}/{stem}.parquet"
    )
    object_body = parquet_bytes(rows)
    object_etag, object_sha256, object_size = put_bytes(
        client, bucket, object_key, object_body
    )
    manifest_key = (
        f"manifests/cdc/kind=normalized/table={TABLE}/"
        f"ingest_date={INGEST_DATE}/hour={HOUR}/{stem}.manifest.json"
    )
    manifest = {
        "contract_version": 1,
        "kind": "normalized",
        "table": TABLE,
        "topic": TOPIC,
        "partition": PARTITION,
        "covered_offset_ranges": offset_ranges(offsets),
        "row_count": len(rows),
        "operation_counts": {"c": len(rows)},
        "schema_id": str(SCHEMA_ID),
        "source_ts_min": utc_text(min(row["_source_ts"] for row in rows)),
        "source_ts_max": utc_text(max(row["_source_ts"] for row in rows)),
        "closed_at": utc_text(BASE_TS + timedelta(minutes=1)),
        "object": {
            "uri": f"s3://{bucket}/{object_key}",
            "etag": object_etag,
            "sha256": object_sha256,
            "size_bytes": object_size,
        },
    }
    put_json(client, bucket, manifest_key, manifest)
    return f"s3://{bucket}/{manifest_key}"


def put_coverage_manifest(
    client,
    bucket: str,
    *,
    stem: str,
    business_offsets: list[int],
    tombstone_offsets: list[int],
) -> str:
    consumed_offsets = sorted([*business_offsets, *tombstone_offsets])
    landing_key = (
        f"landing/debezium/table={TABLE}/event_date={INGEST_DATE}/hour={HOUR}/"
        f"{stem}.jsonl"
    )
    landing_body = (
        b"\n".join(
            json.dumps({"offset": offset}, sort_keys=True).encode("utf-8")
            for offset in consumed_offsets
        )
        + b"\n"
    )
    landing_etag, landing_sha256, landing_size = put_bytes(
        client, bucket, landing_key, landing_body
    )
    landing_manifest_key = (
        f"manifests/cdc/kind=landing/table={TABLE}/"
        f"ingest_date={INGEST_DATE}/hour={HOUR}/{stem}.manifest.json"
    )
    landing_manifest = {
        "contract_version": 1,
        "kind": "landing",
        "table": TABLE,
        "topic": TOPIC,
        "partition": PARTITION,
        "covered_offset_ranges": offset_ranges(consumed_offsets),
        "row_count": len(consumed_offsets),
        "object": {
            "uri": f"s3://{bucket}/{landing_key}",
            "etag": landing_etag,
            "sha256": landing_sha256,
            "size_bytes": landing_size,
        },
    }
    landing_manifest_etag = put_json(
        client, bucket, landing_manifest_key, landing_manifest
    )
    coverage_key = (
        f"manifests/cdc/kind=coverage/table={TABLE}/"
        f"ingest_date={INGEST_DATE}/hour={HOUR}/{stem}.coverage.json"
    )
    coverage = {
        "contract_version": 1,
        "kind": "coverage",
        "table": TABLE,
        "topic": TOPIC,
        "partition": PARTITION,
        "consumed_offset_ranges": offset_ranges(consumed_offsets),
        "business_event_offset_ranges": offset_ranges(business_offsets),
        "tombstone_offset_ranges": offset_ranges(tombstone_offsets),
        "consumed_row_count": len(consumed_offsets),
        "business_event_count": len(business_offsets),
        "tombstone_count": len(tombstone_offsets),
        "closed_at": utc_text(BASE_TS + timedelta(minutes=2)),
        "landing_manifest": {
            "uri": f"s3://{bucket}/{landing_manifest_key}",
            "etag": landing_manifest_etag,
        },
        "landing_object": {
            "uri": f"s3://{bucket}/{landing_key}",
            "etag": landing_etag,
            "sha256": landing_sha256,
            "size_bytes": landing_size,
        },
    }
    put_json(client, bucket, coverage_key, coverage)
    return f"s3://{bucket}/{coverage_key}"


def fetch_one(connection, query: str) -> tuple[Any, ...]:
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    if row is None:
        raise AssertionError(f"query returned no row: {query}")
    return row


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def clickhouse_raw_count(sink: ClickHouseRawCdcSink) -> int:
    row = sink.client.query(f"SELECT count() FROM raw_cdc.`{TABLE}` FINAL").first_row
    if row is None:
        raise AssertionError("raw CDC count query returned no row")
    return int(row[0])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    add_control_postgres_args(parser)
    add_clickhouse_args(parser)
    parser.add_argument(
        "--s3-endpoint", default=os.environ.get("CDC_S3_ENDPOINT", "http://minio:9000")
    )
    parser.add_argument(
        "--s3-region", default=os.environ.get("CDC_S3_REGION", "us-east-1")
    )
    parser.add_argument(
        "--s3-access-key",
        default=os.environ.get("CDC_S3_ACCESS_KEY", "olist_cdc_loader"),
    )
    parser.add_argument("--s3-secret-key", default=os.environ.get("CDC_S3_SECRET_KEY"))
    parser.add_argument(
        "--s3-secret-file", default=os.environ.get("CDC_S3_SECRET_FILE")
    )
    parser.add_argument("--s3-write-access-key")
    parser.add_argument("--s3-write-secret-key")
    parser.add_argument("--s3-write-secret-file")
    parser.add_argument(
        "--bucket", default=os.environ.get("CDC_S3_BUCKET", "olist-cdc")
    )
    parser.add_argument(
        "--report", default="data/reports/clickhouse-cdc-ingest-resilience.json"
    )
    return parser


def s3_writer_client(args: argparse.Namespace):
    writer_args = argparse.Namespace(
        s3_endpoint=args.s3_endpoint,
        s3_region=args.s3_region,
        s3_access_key=args.s3_write_access_key or args.s3_access_key,
        s3_secret_key=args.s3_write_secret_key or args.s3_secret_key,
        s3_secret_file=args.s3_write_secret_file or args.s3_secret_file,
    )
    return s3_client(writer_args)


def main() -> int:
    args = build_parser().parse_args()
    object_pattern = "phase8_resilience"
    selector = Selector(
        table=TABLE,
        date_from=datetime.fromisoformat(INGEST_DATE).date(),
        date_to=datetime.fromisoformat(INGEST_DATE).date(),
        object_pattern=object_pattern,
    )
    s3 = s3_client(args)
    writer_s3 = s3_writer_client(args)
    ensure_bucket(writer_s3, args.bucket)
    put_normalized_manifest(
        writer_s3,
        args.bucket,
        stem=object_pattern,
        offsets=[0, 1, 4, 5],
    )

    control = control_connection(args)
    sink = ClickHouseRawCdcSink(clickhouse_client(args))
    try:
        try:
            ingest(
                raw_sink=sink,
                control_connection=control,
                client=s3,
                bucket=args.bucket,
                selector=selector,
                ingest_run_id="phase8_resilience_injected_failure",
                run_kind="MANUAL",
                dag_id="ci_clickhouse_cdc_ingest_resilience",
                orchestration_run_id=None,
                inject_failure="after_clickhouse_insert_before_control_commit",
            )
        except RuntimeError as exc:
            if "Injected CDC failure" not in str(exc):
                raise
        else:
            raise AssertionError("injected ClickHouse CDC failure did not fail")

        failed_file = fetch_one(
            control,
            """
            select status, attempt_count
            from cdc_audit.cdc_files
            where object_uri like '%phase8_resilience.parquet'
            """,
        )
        assert_equal(failed_file, ("FAILED", 1), "failed file state")

        recovered = ingest(
            raw_sink=sink,
            control_connection=control,
            client=s3,
            bucket=args.bucket,
            selector=selector,
            ingest_run_id="phase8_resilience_retry",
            run_kind="MANUAL",
            dag_id="ci_clickhouse_cdc_ingest_resilience",
            orchestration_run_id=None,
        )
        assert_equal(recovered.files_loaded, 1, "retry loaded files")
        assert_equal(recovered.inserted_rows, 0, "retry inserted rows")
        assert_equal(recovered.duplicate_rows, 4, "retry duplicate rows")
        assert_equal(recovered.gap_count, 1, "retry open gap count")
        assert_equal(clickhouse_raw_count(sink), 4, "ClickHouse raw row count")

        watermark = fetch_one(
            control,
            """
            select last_contiguous_offset, last_seen_offset, gap_count
            from cdc_audit.cdc_partition_watermarks
            where topic = 'olist_cdc.public.customers' and partition_id = 0
            """,
        )
        assert_equal(watermark, (1, 5, 1), "open watermark")

        put_coverage_manifest(
            writer_s3,
            args.bucket,
            stem=object_pattern,
            business_offsets=[0, 1, 4, 5],
            tombstone_offsets=[2, 3],
        )
        closed = ingest(
            raw_sink=sink,
            control_connection=control,
            client=s3,
            bucket=args.bucket,
            selector=selector,
            ingest_run_id="phase8_resilience_gap_closed",
            run_kind="MANUAL",
            dag_id="ci_clickhouse_cdc_ingest_resilience",
            orchestration_run_id=None,
        )
        assert_equal(closed.files_loaded, 0, "coverage-only loaded files")
        assert_equal(closed.gap_count, 0, "coverage-only gap count")
        closed_watermark = fetch_one(
            control,
            """
            select last_contiguous_offset, last_seen_offset, gap_count
            from cdc_audit.cdc_partition_watermarks
            where topic = 'olist_cdc.public.customers' and partition_id = 0
            """,
        )
        assert_equal(closed_watermark, (5, 5, 0), "closed watermark")

        selected = request_replay(
            control,
            "phase8_resilience_replay",
            "ci",
            selector,
        )
        assert_equal(selected, 1, "selected replay files")
        selected_again = request_replay(
            control,
            "phase8_resilience_replay",
            "ci",
            selector,
        )
        assert_equal(selected_again, selected, "idempotent replay selection")
        replay = ingest(
            raw_sink=sink,
            control_connection=control,
            client=s3,
            bucket=args.bucket,
            selector=selector,
            ingest_run_id="phase8_resilience_replay_run",
            run_kind="REPLAY",
            dag_id="ci_clickhouse_cdc_ingest_resilience",
            orchestration_run_id=None,
            replay_request_id="phase8_resilience_replay",
        )
        assert_equal(replay.files_loaded, 1, "replay loaded files")
        assert_equal(replay.inserted_rows, 0, "replay inserted rows")
        assert_equal(replay.duplicate_rows, 4, "replay duplicate rows")
        assert_equal(clickhouse_raw_count(sink), 4, "raw rows after replay")

        report = {
            "status": "PASS",
            "failed_file_attempts": 1,
            "retry": recovered.as_dict(),
            "gap_closed": closed.as_dict(),
            "replay": replay.as_dict(),
            "raw_rows": clickhouse_raw_count(sink),
        }
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0
    finally:
        sink.close()
        control.close()


if __name__ == "__main__":
    raise SystemExit(main())
