#!/usr/bin/env python3
"""Run an isolated PostgreSQL/MinIO integration check for Phase 4 CDC ingest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import boto3
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
from psycopg2 import sql
from scripts.cdc.warehouse_ingest import (
    PostgresRawCdcSink,
    Selector,
    execute_bootstrap,
    ingest,
    read_secret,
    request_replay,
)

TOPIC = "olist_cdc.public.customers"
TABLE = "customers"


def customer_row(offset: int) -> dict[str, Any]:
    event_time = datetime(2026, 7, 16, 10, 0, tzinfo=UTC) + timedelta(seconds=offset)
    return {
        "customer_id": f"stage4-customer-{offset}",
        "customer_unique_id": f"stage4-unique-{offset}",
        "customer_zip_code_prefix": "01001",
        "customer_city": "sao paulo",
        "customer_state": "SP",
        "_event_id": f"{TOPIC}:0:{offset}",
        "_op": "r",
        "_source_ts": event_time,
        "_source_lsn": 1000 + offset,
        "_tx_id": None,
        "_tx_order": None,
        "_topic": TOPIC,
        "_partition": 0,
        "_offset": offset,
        "_kafka_ts": event_time,
        "_key_schema_id": 1,
        "_schema_id": 42,
        "_nifi_written_at": event_time + timedelta(seconds=1),
    }


def parquet_bytes(offsets: list[int]) -> bytes:
    output = pa.BufferOutputStream()
    pq.write_table(
        pa.Table.from_pylist([customer_row(offset) for offset in offsets]), output
    )
    return output.getvalue().to_pybytes()


def offset_ranges(offsets: list[int]) -> list[list[int]]:
    ranges: list[list[int]] = []
    for offset in sorted(offsets):
        if not ranges or offset > ranges[-1][1] + 1:
            ranges.append([offset, offset])
        else:
            ranges[-1][1] = offset
    return ranges


def put_closed_object(
    client,
    bucket: str,
    offsets: list[int],
    *,
    suffix: str,
    closed_at: datetime,
) -> None:
    body = parquet_bytes(offsets)
    stem = f"{TOPIC}-p=00000-o={min(offsets):020d}-{max(offsets):020d}-sid=42-{suffix}"
    object_key = f"stage/cdc/table={TABLE}/event_date=2026-07-16/hour=10/{stem}.parquet"
    manifest_key = (
        "manifests/cdc/kind=normalized/table=customers/"
        f"ingest_date=2026-07-16/hour=10/{stem}.manifest.json"
    )
    response = client.put_object(Bucket=bucket, Key=object_key, Body=body)
    etag = str(response["ETag"]).strip('"')
    manifest = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "normalized",
        "table": TABLE,
        "topic": TOPIC,
        "partition": 0,
        "schema_id": "42",
        "covered_offset_ranges": offset_ranges(offsets),
        "row_count": len(offsets),
        "operation_counts": {"r": len(offsets)},
        "source_ts_min": customer_row(min(offsets))["_source_ts"].isoformat(),
        "source_ts_max": customer_row(max(offsets))["_source_ts"].isoformat(),
        "closed_at": closed_at.isoformat(),
        "object": {
            "uri": f"s3://{bucket}/{object_key}",
            "etag": etag,
            "sha256": hashlib.sha256(body).hexdigest(),
            "size_bytes": len(body),
        },
    }
    client.put_object(
        Bucket=bucket,
        Key=manifest_key,
        Body=json.dumps(manifest, sort_keys=True).encode(),
        ContentType="application/json",
    )


def put_coverage_manifest(
    client,
    bucket: str,
    *,
    business_offsets: list[int],
    tombstone_offsets: list[int],
    suffix: str,
    closed_at: datetime,
) -> None:
    consumed = sorted([*business_offsets, *tombstone_offsets])
    landing_body = json.dumps(
        {"business": business_offsets, "tombstones": tombstone_offsets},
        sort_keys=True,
    ).encode()
    digest = hashlib.sha256(landing_body).hexdigest()
    stem = f"{TOPIC}-p=00000-o={min(consumed):020d}-{max(consumed):020d}-sid=mixed-{suffix}"
    landing_key = (
        f"landing/debezium/table={TABLE}/event_date=2026-07-16/hour=10/{stem}.avro"
    )
    landing_response = client.put_object(
        Bucket=bucket,
        Key=landing_key,
        Body=landing_body,
        Metadata={"sha256": digest, "contract-version": "1"},
    )
    landing_etag = str(landing_response["ETag"]).strip('"')
    landing_manifest_key = (
        "manifests/cdc/kind=landing/table=customers/"
        f"ingest_date=2026-07-16/hour=10/{stem}.manifest.json"
    )
    landing_manifest = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "landing",
        "table": TABLE,
        "topic": TOPIC,
        "partition": 0,
        "covered_offset_ranges": offset_ranges(consumed),
        "row_count": len(consumed),
        "object": {
            "uri": f"s3://{bucket}/{landing_key}",
            "etag": landing_etag,
            "sha256": digest,
            "size_bytes": len(landing_body),
        },
    }
    landing_manifest_response = client.put_object(
        Bucket=bucket,
        Key=landing_manifest_key,
        Body=json.dumps(landing_manifest, sort_keys=True).encode(),
        ContentType="application/json",
    )
    landing_manifest_etag = str(landing_manifest_response["ETag"]).strip('"')
    coverage_key = (
        "manifests/cdc/kind=coverage/table=customers/"
        f"ingest_date=2026-07-16/hour=10/{stem}.coverage.json"
    )
    coverage = {
        "contract_version": 1,
        "flow_version": "olist-cdc-v1",
        "kind": "coverage",
        "table": TABLE,
        "topic": TOPIC,
        "partition": 0,
        "consumed_offset_ranges": offset_ranges(consumed),
        "business_event_offset_ranges": offset_ranges(business_offsets),
        "tombstone_offset_ranges": offset_ranges(tombstone_offsets),
        "consumed_row_count": len(consumed),
        "business_event_count": len(business_offsets),
        "tombstone_count": len(tombstone_offsets),
        "closed_at": closed_at.isoformat(),
        "landing_manifest": {
            "uri": f"s3://{bucket}/{landing_manifest_key}",
            "etag": landing_manifest_etag,
        },
        "landing_object": {
            "uri": f"s3://{bucket}/{landing_key}",
            "etag": landing_etag,
            "sha256": digest,
            "size_bytes": len(landing_body),
        },
    }
    client.put_object(
        Bucket=bucket,
        Key=coverage_key,
        Body=json.dumps(coverage, sort_keys=True).encode(),
        ContentType="application/json",
    )


class FailOnceOnParquet:
    def __init__(self, client):
        self.client = client
        self.failed = False

    def get_paginator(self, name: str):
        return self.client.get_paginator(name)

    def get_object(self, **kwargs):
        if str(kwargs.get("Key", "")).endswith(".parquet") and not self.failed:
            self.failed = True
            raise RuntimeError("injected transient object read failure")
        return self.client.get_object(**kwargs)

    def head_object(self, **kwargs):
        return self.client.head_object(**kwargs)


def fetch_one(connection, query: str) -> tuple:
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    if row is None:
        raise AssertionError(f"query returned no row: {query}")
    return row


def create_database(admin_connection, database: str) -> None:
    admin_connection.autocommit = True
    with admin_connection.cursor() as cursor:
        cursor.execute(sql.SQL("create database {}").format(sql.Identifier(database)))


def drop_database(admin_connection, database: str) -> None:
    if not database.startswith("olist_cdc_phase4_test_"):
        raise ValueError(f"refusing to drop unexpected database: {database}")
    admin_connection.autocommit = True
    with admin_connection.cursor() as cursor:
        cursor.execute(
            "select pg_terminate_backend(pid) from pg_stat_activity where datname = %s",
            (database,),
        )
        cursor.execute(
            sql.SQL("drop database if exists {}").format(sql.Identifier(database))
        )


def empty_bucket(client, bucket: str) -> None:
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if objects:
            client.delete_objects(Bucket=bucket, Delete={"Objects": objects})
    client.delete_bucket(Bucket=bucket)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--postgres-host", default=os.environ.get("POSTGRES_HOST", "localhost")
    )
    parser.add_argument(
        "--postgres-port",
        type=int,
        default=int(os.environ.get("POSTGRES_PORT", "5432")),
    )
    parser.add_argument(
        "--postgres-user", default=os.environ.get("POSTGRES_USER", "olist")
    )
    parser.add_argument(
        "--postgres-password", default=os.environ.get("POSTGRES_PASSWORD")
    )
    parser.add_argument(
        "--postgres-password-file", default=os.environ.get("POSTGRES_PASSWORD_FILE")
    )
    parser.add_argument("--s3-endpoint", default="http://localhost:9000")
    parser.add_argument("--s3-access-key", default="minioadmin")
    parser.add_argument(
        "--s3-secret-key", default=os.environ.get("MINIO_ROOT_PASSWORD")
    )
    parser.add_argument(
        "--s3-secret-file", default=os.environ.get("MINIO_ROOT_PASSWORD_FILE")
    )
    args = parser.parse_args()

    token = uuid.uuid4().hex[:12]
    database = f"olist_cdc_phase4_test_{token}"
    bucket = f"olist-cdc-phase4-test-{token}"
    password = read_secret(args.postgres_password, args.postgres_password_file)
    client = boto3.client(
        "s3",
        endpoint_url=args.s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=args.s3_access_key,
        aws_secret_access_key=read_secret(args.s3_secret_key, args.s3_secret_file),
    )
    admin = psycopg2.connect(
        host=args.postgres_host,
        port=args.postgres_port,
        dbname="postgres",
        user=args.postgres_user,
        password=password,
    )
    bucket_created = database_created = False
    try:
        create_database(admin, database)
        database_created = True
        client.create_bucket(Bucket=bucket)
        bucket_created = True
        connection = psycopg2.connect(
            host=args.postgres_host,
            port=args.postgres_port,
            dbname=database,
            user=args.postgres_user,
            password=password,
        )
        try:
            execute_bootstrap(connection, PROJECT_ROOT / "infra/postgres")
            raw_sink = PostgresRawCdcSink(connection)
            base = datetime(2026, 7, 16, 10, 1, tzinfo=UTC)
            put_closed_object(client, bucket, [0, 1], suffix="low", closed_at=base)
            put_closed_object(client, bucket, [4, 5], suffix="high", closed_at=base)
            first = ingest(
                raw_sink,
                connection,
                client,
                bucket,
                Selector(table=TABLE),
                "stage4_gap",
                "MANUAL",
                None,
                None,
            )
            assert first.inserted_rows == 4 and first.gap_count == 1, first
            watermark = fetch_one(
                connection,
                "select last_contiguous_offset, last_seen_offset, gap_count "
                "from cdc_audit.cdc_partition_watermarks",
            )
            assert watermark == (1, 5, 1), watermark

            put_coverage_manifest(
                client,
                bucket,
                business_offsets=[0, 1, 4, 5],
                tombstone_offsets=[2, 3],
                suffix="late-tombstone-coverage",
                closed_at=base + timedelta(minutes=1),
            )
            second = ingest(
                raw_sink,
                connection,
                client,
                bucket,
                Selector(table=TABLE),
                "stage4_gap_closed",
                "MANUAL",
                None,
                None,
            )
            assert second.inserted_rows == 0 and second.gap_count == 0, second
            coverage_kinds = fetch_one(
                connection,
                "select count(*) filter (where coverage_kind = 'NORMALIZED_LOADED'), "
                "count(*) filter (where coverage_kind = 'TOMBSTONE_AUDITED') "
                "from cdc_audit.cdc_offset_coverage",
            )
            assert coverage_kinds == (2, 1), coverage_kinds

            put_coverage_manifest(
                client,
                bucket,
                business_offsets=[6],
                tombstone_offsets=[],
                suffix="business-tail-before-normalized",
                closed_at=base + timedelta(minutes=2),
            )
            expected_tail = ingest(
                raw_sink,
                connection,
                client,
                bucket,
                Selector(table=TABLE),
                "stage4_expected_business_tail",
                "MANUAL",
                None,
                None,
            )
            assert expected_tail.inserted_rows == 0 and expected_tail.gap_count == 1
            tail_watermark = fetch_one(
                connection,
                "select last_contiguous_offset, last_seen_offset, gap_count "
                "from cdc_audit.cdc_partition_watermarks",
            )
            assert tail_watermark == (5, 6, 1), tail_watermark

            put_closed_object(
                client,
                bucket,
                [6],
                suffix="transient",
                closed_at=base + timedelta(minutes=2),
            )
            try:
                ingest(
                    raw_sink,
                    connection,
                    FailOnceOnParquet(client),
                    bucket,
                    Selector(table=TABLE),
                    "stage4_transient_failure",
                    "MANUAL",
                    None,
                    None,
                )
            except RuntimeError as exc:
                assert "injected transient" in str(exc)
            else:
                raise AssertionError("injected object failure did not fail the run")
            failed = fetch_one(
                connection,
                "select status, attempt_count from cdc_audit.cdc_files "
                "where max_offset = 6",
            )
            assert failed == ("FAILED", 1), failed
            recovered = ingest(
                raw_sink,
                connection,
                client,
                bucket,
                Selector(table=TABLE),
                "stage4_transient_recovery",
                "MANUAL",
                None,
                None,
            )
            assert recovered.inserted_rows == 1 and recovered.gap_count == 0, recovered

            selected = request_replay(
                connection,
                "stage4_replay",
                "integration-test",
                Selector(table=TABLE),
            )
            assert selected == 3, selected
            repeated_selected = request_replay(
                connection,
                "stage4_replay",
                "integration-test",
                Selector(table=TABLE),
            )
            assert repeated_selected == selected
            replay = ingest(
                raw_sink,
                connection,
                client,
                bucket,
                Selector(table=TABLE),
                "stage4_replay_run",
                "REPLAY",
                None,
                None,
                "stage4_replay",
            )
            assert replay.inserted_rows == 0 and replay.duplicate_rows == 5, replay
            assert (
                fetch_one(connection, "select count(*) from raw_cdc.customers")[0] == 5
            )
            assert (
                fetch_one(
                    connection,
                    "select count(*) from cdc_audit.cdc_reconciliation where status = 'FAIL'",
                )[0]
                == 0
            )
        finally:
            connection.close()
        print(
            json.dumps(
                {
                    "status": "passed",
                    "missing_business_tail_detected": True,
                    "tombstone_gap_closed": True,
                    "transient_retry_succeeded": True,
                    "replay_duplicates": 5,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        if bucket_created:
            empty_bucket(client, bucket)
        if database_created:
            drop_database(admin, database)
        admin.close()


if __name__ == "__main__":
    raise SystemExit(main())
