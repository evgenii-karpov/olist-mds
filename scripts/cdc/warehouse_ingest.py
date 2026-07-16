#!/usr/bin/env python3
"""Idempotently load closed normalized CDC objects into PostgreSQL."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import boto3
import psycopg2
import pyarrow as pa
import pyarrow.parquet as parquet
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json, execute_values

NORMALIZED_MANIFEST_PREFIX = "manifests/cdc/kind=normalized/"
COVERAGE_MANIFEST_PREFIX = "manifests/cdc/kind=coverage/"
CLAIM_TTL = timedelta(minutes=15)
ALLOWED_OPERATIONS = {"r", "c", "u", "d"}

COMMON_COLUMNS = (
    "_event_id",
    "_op",
    "_source_ts",
    "_source_lsn",
    "_tx_id",
    "_tx_order",
    "_topic",
    "_partition",
    "_offset",
    "_kafka_ts",
    "_key_schema_id",
    "_schema_id",
    "_nifi_written_at",
)

BUSINESS_COLUMNS: dict[str, tuple[str, ...]] = {
    "customers": (
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ),
    "orders": (
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
    "order_items": (
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ),
    "order_payments": (
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ),
    "order_reviews": (
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ),
    "products": (
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ),
    "sellers": (
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ),
    "product_category_translation": (
        "product_category_name",
        "product_category_name_english",
    ),
}


@dataclass(frozen=True)
class ObjectRef:
    bucket: str
    key: str


@dataclass(frozen=True)
class Manifest:
    manifest_uri: str
    manifest_etag: str
    object_uri: str
    object_etag: str
    object_sha256: str
    object_size_bytes: int
    table: str
    topic: str
    partition: int
    offset_ranges: tuple[tuple[int, int], ...]
    schema_id: str
    row_count: int
    operation_counts: dict[str, int]
    ingest_date: date
    source_ts_min: datetime | None
    source_ts_max: datetime | None
    closed_at: datetime

    @property
    def min_offset(self) -> int:
        return min(start for start, _ in self.offset_ranges)

    @property
    def max_offset(self) -> int:
        return max(end for _, end in self.offset_ranges)


@dataclass(frozen=True)
class CoverageManifest:
    coverage_uri: str
    coverage_etag: str
    table: str
    topic: str
    partition: int
    consumed_offset_ranges: tuple[tuple[int, int], ...]
    business_event_offset_ranges: tuple[tuple[int, int], ...]
    tombstone_offset_ranges: tuple[tuple[int, int], ...]
    consumed_row_count: int
    business_event_count: int
    tombstone_count: int
    ingest_date: date
    closed_at: datetime
    landing_manifest_uri: str
    landing_manifest_etag: str
    landing_object_uri: str
    landing_object_etag: str
    landing_object_sha256: str
    landing_object_size_bytes: int


@dataclass(frozen=True)
class Selector:
    table: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    object_pattern: str | None = None


@dataclass(frozen=True)
class IngestSummary:
    ingest_run_id: str
    files_discovered: int
    files_loaded: int
    object_rows: int
    inserted_rows: int
    duplicate_rows: int
    gap_count: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "ingest_run_id": self.ingest_run_id,
            "files_discovered": self.files_discovered,
            "files_loaded": self.files_loaded,
            "object_rows": self.object_rows,
            "inserted_rows": self.inserted_rows,
            "duplicate_rows": self.duplicate_rows,
            "gap_count": self.gap_count,
        }


def utc_now() -> datetime:
    return datetime.now(UTC)


def read_secret(value: str | None, file_path: str | None) -> str | None:
    if value:
        return value
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    return None


def postgres_connection(args: argparse.Namespace) -> PgConnection:
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=read_secret(args.password, args.password_file),
        connect_timeout=10,
        application_name="olist_cdc_ingest",
    )


def s3_client(args: argparse.Namespace):
    return boto3.client(
        "s3",
        endpoint_url=args.s3_endpoint,
        region_name=args.s3_region,
        aws_access_key_id=args.s3_access_key,
        aws_secret_access_key=read_secret(args.s3_secret_key, args.s3_secret_file),
    )


def parse_s3_uri(uri: str) -> ObjectRef:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.lstrip("/"):
        raise ValueError(f"invalid S3 URI: {uri!r}")
    return ObjectRef(parsed.netloc, parsed.path.lstrip("/"))


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"manifest {field} must be an ISO timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def optional_timestamp(value: Any, field: str) -> datetime | None:
    return None if value is None else parse_timestamp(value, field)


def validate_offset_ranges(
    value: Any, *, allow_empty: bool = False
) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError("manifest offset ranges must be a non-empty list")
    result: list[tuple[int, int]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not all(isinstance(offset, int) for offset in item)
        ):
            raise ValueError("manifest offset range must be [integer, integer]")
        start, end = item
        if start < 0 or end < start:
            raise ValueError(f"invalid manifest offset range: {item!r}")
        if result and start <= result[-1][1]:
            raise ValueError("manifest offset ranges must be sorted and disjoint")
        result.append((start, end))
    return tuple(result)


def range_row_count(ranges: Iterable[tuple[int, int]]) -> int:
    return sum(end - start + 1 for start, end in ranges)


def ingest_date_from_uri(uri: str) -> date:
    uri_ref = parse_s3_uri(uri)
    marker = "/ingest_date="
    if marker not in f"/{uri_ref.key}":
        raise ValueError("manifest URI has no ingest_date partition")
    date_text = f"/{uri_ref.key}".split(marker, 1)[1].split("/", 1)[0]
    try:
        return date.fromisoformat(date_text)
    except ValueError as exc:
        raise ValueError("manifest URI has an invalid ingest_date partition") from exc


def parse_manifest(uri: str, etag: str, body: bytes) -> Manifest:
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest JSON at {uri}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"manifest at {uri} must be an object")
    if value.get("contract_version") != 1 or value.get("kind") != "normalized":
        raise ValueError(f"unsupported normalized manifest contract at {uri}")
    table = value.get("table")
    if table not in BUSINESS_COLUMNS:
        raise ValueError(f"unsupported CDC table in manifest: {table!r}")
    obj = value.get("object")
    if not isinstance(obj, dict):
        raise ValueError("manifest object metadata is missing")
    ranges = validate_offset_ranges(value.get("covered_offset_ranges"))
    row_count = value.get("row_count")
    if not isinstance(row_count, int) or row_count <= 0:
        raise ValueError("manifest row_count must be a positive integer")
    range_rows = sum(end - start + 1 for start, end in ranges)
    if range_rows != row_count:
        raise ValueError(
            f"manifest offset coverage {range_rows} does not match row_count {row_count}"
        )
    operations = value.get("operation_counts")
    if not isinstance(operations, dict) or any(
        op not in ALLOWED_OPERATIONS or not isinstance(count, int)
        for op, count in operations.items()
    ):
        raise ValueError("manifest operation_counts is invalid")
    if sum(operations.values()) != row_count:
        raise ValueError("manifest operation_counts do not reconcile to row_count")
    topic = value.get("topic")
    partition = value.get("partition")
    if not isinstance(topic, str) or topic.rsplit(".", 1)[-1] != table:
        raise ValueError("manifest topic/table mismatch")
    if not isinstance(partition, int) or partition < 0:
        raise ValueError("manifest partition must be a non-negative integer")
    object_uri = obj.get("uri")
    object_etag = obj.get("etag")
    object_sha256 = obj.get("sha256")
    object_size = obj.get("size_bytes")
    if not isinstance(object_uri, str) or not object_uri.endswith(".parquet"):
        raise ValueError("normalized manifest must reference a Parquet object")
    parse_s3_uri(object_uri)
    if not isinstance(object_etag, str) or not object_etag:
        raise ValueError("manifest object ETag is missing")
    if (
        not isinstance(object_sha256, str)
        or len(object_sha256) != 64
        or any(char not in "0123456789abcdef" for char in object_sha256.lower())
    ):
        raise ValueError("manifest object SHA-256 is invalid")
    if not isinstance(object_size, int) or object_size <= 0:
        raise ValueError("manifest object size is invalid")
    schema_id = value.get("schema_id")
    if not isinstance(schema_id, (str, int)):
        raise ValueError("manifest schema_id is missing")
    return Manifest(
        manifest_uri=uri,
        manifest_etag=etag,
        object_uri=object_uri,
        object_etag=object_etag,
        object_sha256=object_sha256.lower(),
        object_size_bytes=object_size,
        table=table,
        topic=topic,
        partition=partition,
        offset_ranges=ranges,
        schema_id=str(schema_id),
        row_count=row_count,
        operation_counts={str(op): int(count) for op, count in operations.items()},
        ingest_date=ingest_date_from_uri(uri),
        source_ts_min=optional_timestamp(value.get("source_ts_min"), "source_ts_min"),
        source_ts_max=optional_timestamp(value.get("source_ts_max"), "source_ts_max"),
        closed_at=parse_timestamp(value.get("closed_at"), "closed_at"),
    )


def parse_coverage_manifest(uri: str, etag: str, body: bytes) -> CoverageManifest:
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid coverage JSON at {uri}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"coverage manifest at {uri} must be an object")
    if value.get("contract_version") != 1 or value.get("kind") != "coverage":
        raise ValueError(f"unsupported coverage manifest contract at {uri}")
    table = value.get("table")
    topic = value.get("topic")
    partition = value.get("partition")
    if table not in BUSINESS_COLUMNS:
        raise ValueError(f"unsupported CDC table in coverage: {table!r}")
    if not isinstance(topic, str) or topic.rsplit(".", 1)[-1] != table:
        raise ValueError("coverage topic/table mismatch")
    if not isinstance(partition, int) or partition < 0:
        raise ValueError("coverage partition must be a non-negative integer")
    consumed = validate_offset_ranges(value.get("consumed_offset_ranges"))
    business = validate_offset_ranges(
        value.get("business_event_offset_ranges"), allow_empty=True
    )
    tombstones = validate_offset_ranges(
        value.get("tombstone_offset_ranges"), allow_empty=True
    )
    if merge_ranges([*business, *tombstones]) != list(consumed):
        raise ValueError(
            "business and tombstone coverage does not equal consumed coverage"
        )
    for business_start, business_end in business:
        if any(
            business_start <= tombstone_end and tombstone_start <= business_end
            for tombstone_start, tombstone_end in tombstones
        ):
            raise ValueError("business and tombstone offset coverage overlaps")
    consumed_count = value.get("consumed_row_count")
    business_count = value.get("business_event_count")
    tombstone_count = value.get("tombstone_count")
    if not all(
        isinstance(count, int) and count >= 0
        for count in (consumed_count, business_count, tombstone_count)
    ):
        raise ValueError("coverage row counts must be non-negative integers")
    assert isinstance(consumed_count, int)
    assert isinstance(business_count, int)
    assert isinstance(tombstone_count, int)
    if consumed_count <= 0:
        raise ValueError("coverage consumed_row_count must be positive")
    if (
        range_row_count(consumed) != consumed_count
        or range_row_count(business) != business_count
        or range_row_count(tombstones) != tombstone_count
        or business_count + tombstone_count != consumed_count
    ):
        raise ValueError("coverage ranges do not reconcile to row counts")
    landing_manifest = value.get("landing_manifest")
    landing_object = value.get("landing_object")
    if not isinstance(landing_manifest, dict) or not isinstance(landing_object, dict):
        raise ValueError("coverage landing references are missing")
    landing_manifest_uri = landing_manifest.get("uri")
    landing_manifest_etag = landing_manifest.get("etag")
    landing_object_uri = landing_object.get("uri")
    landing_object_etag = landing_object.get("etag")
    landing_object_sha256 = landing_object.get("sha256")
    landing_object_size = landing_object.get("size_bytes")
    if not all(
        isinstance(item, str) and item
        for item in (
            landing_manifest_uri,
            landing_manifest_etag,
            landing_object_uri,
            landing_object_etag,
        )
    ):
        raise ValueError("coverage landing URI or ETag is invalid")
    if (
        not isinstance(landing_object_sha256, str)
        or len(landing_object_sha256) != 64
        or any(char not in "0123456789abcdef" for char in landing_object_sha256.lower())
    ):
        raise ValueError("coverage landing SHA-256 is invalid")
    if not isinstance(landing_object_size, int) or landing_object_size <= 0:
        raise ValueError("coverage landing object size is invalid")
    return CoverageManifest(
        coverage_uri=uri,
        coverage_etag=etag,
        table=str(table),
        topic=topic,
        partition=partition,
        consumed_offset_ranges=consumed,
        business_event_offset_ranges=business,
        tombstone_offset_ranges=tombstones,
        consumed_row_count=consumed_count,
        business_event_count=business_count,
        tombstone_count=tombstone_count,
        ingest_date=ingest_date_from_uri(uri),
        closed_at=parse_timestamp(value.get("closed_at"), "closed_at"),
        landing_manifest_uri=str(landing_manifest_uri),
        landing_manifest_etag=str(landing_manifest_etag),
        landing_object_uri=str(landing_object_uri),
        landing_object_etag=str(landing_object_etag),
        landing_object_sha256=landing_object_sha256.lower(),
        landing_object_size_bytes=landing_object_size,
    )


def object_matches_selector(key: str, selector: Selector) -> bool:
    if selector.table and f"/table={selector.table}/" not in f"/{key}":
        return False
    if selector.object_pattern and selector.object_pattern not in key:
        return False
    marker = "/ingest_date="
    if selector.date_from or selector.date_to:
        if marker not in key:
            return False
        date_text = key.split(marker, 1)[1].split("/", 1)[0]
        try:
            key_date = date.fromisoformat(date_text)
        except ValueError:
            return False
        if selector.date_from and key_date < selector.date_from:
            return False
        if selector.date_to and key_date > selector.date_to:
            return False
    return True


def validate_manifest_location(manifest: Manifest, bucket: str) -> None:
    manifest_ref = parse_s3_uri(manifest.manifest_uri)
    object_ref = parse_s3_uri(manifest.object_uri)
    expected_manifest_prefix = (
        f"{NORMALIZED_MANIFEST_PREFIX}table={manifest.table}/ingest_date="
    )
    expected_object_prefix = f"stage/cdc/table={manifest.table}/event_date="
    if manifest_ref.bucket != bucket or object_ref.bucket != bucket:
        raise ValueError(
            "manifest cannot reference an object outside the configured bucket"
        )
    if not manifest_ref.key.startswith(expected_manifest_prefix):
        raise ValueError("manifest key does not match the normalized table layout")
    if not object_ref.key.startswith(expected_object_prefix):
        raise ValueError("object key does not match the normalized Parquet layout")


def validate_coverage_location(coverage: CoverageManifest, bucket: str) -> None:
    coverage_ref = parse_s3_uri(coverage.coverage_uri)
    landing_manifest_ref = parse_s3_uri(coverage.landing_manifest_uri)
    landing_object_ref = parse_s3_uri(coverage.landing_object_uri)
    expected_coverage = f"{COVERAGE_MANIFEST_PREFIX}table={coverage.table}/ingest_date="
    expected_landing_manifest = (
        f"manifests/cdc/kind=landing/table={coverage.table}/ingest_date="
    )
    expected_landing_object = f"landing/debezium/table={coverage.table}/event_date="
    if any(
        ref.bucket != bucket
        for ref in (coverage_ref, landing_manifest_ref, landing_object_ref)
    ):
        raise ValueError(
            "coverage cannot reference an object outside the configured bucket"
        )
    if not coverage_ref.key.startswith(expected_coverage):
        raise ValueError("coverage key does not match the table layout")
    if not landing_manifest_ref.key.startswith(expected_landing_manifest):
        raise ValueError("coverage landing manifest reference has an invalid layout")
    if not landing_object_ref.key.startswith(expected_landing_object):
        raise ValueError("coverage landing object reference has an invalid layout")


def validate_coverage_landing_manifest(
    coverage: CoverageManifest, manifest_etag: str, body: bytes
) -> None:
    if manifest_etag != coverage.landing_manifest_etag:
        raise ValueError("coverage landing manifest ETag mismatch")
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("coverage landing manifest is invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("coverage landing manifest must be an object")
    if value.get("contract_version") != 1 or value.get("kind") != "landing":
        raise ValueError("coverage reference is not a v1 landing manifest")
    if (
        value.get("table") != coverage.table
        or value.get("topic") != coverage.topic
        or value.get("partition") != coverage.partition
    ):
        raise ValueError("coverage and landing manifest identities do not match")
    if validate_offset_ranges(value.get("covered_offset_ranges")) != (
        coverage.consumed_offset_ranges
    ):
        raise ValueError("coverage and landing manifest offset ranges do not match")
    if value.get("row_count") != coverage.consumed_row_count:
        raise ValueError("coverage and landing manifest row counts do not match")
    obj = value.get("object")
    if not isinstance(obj, dict):
        raise ValueError("coverage landing manifest object metadata is missing")
    expected_object = {
        "uri": coverage.landing_object_uri,
        "etag": coverage.landing_object_etag,
        "sha256": coverage.landing_object_sha256,
        "size_bytes": coverage.landing_object_size_bytes,
    }
    if any(obj.get(key) != expected for key, expected in expected_object.items()):
        raise ValueError("coverage and landing manifest object identities do not match")


def verify_coverage_references(client, coverage: CoverageManifest) -> None:
    manifest_ref = parse_s3_uri(coverage.landing_manifest_uri)
    object_ref = parse_s3_uri(coverage.landing_object_uri)
    manifest_response = client.get_object(
        Bucket=manifest_ref.bucket, Key=manifest_ref.key
    )
    validate_coverage_landing_manifest(
        coverage,
        str(manifest_response.get("ETag", "")).strip('"'),
        manifest_response["Body"].read(),
    )
    object_head = client.head_object(Bucket=object_ref.bucket, Key=object_ref.key)
    if str(object_head.get("ETag", "")).strip('"') != coverage.landing_object_etag:
        raise ValueError("coverage landing object ETag mismatch")
    if int(object_head.get("ContentLength", -1)) != coverage.landing_object_size_bytes:
        raise ValueError("coverage landing object size mismatch")
    if object_head.get("Metadata", {}).get("sha256") != coverage.landing_object_sha256:
        raise ValueError("coverage landing object SHA-256 metadata mismatch")


def discover_manifests(
    client,
    bucket: str,
    selector: Selector,
    known_etags: Mapping[str, str] | None = None,
) -> list[Manifest]:
    prefix = NORMALIZED_MANIFEST_PREFIX
    if selector.table:
        prefix += f"table={selector.table}/"
    paginator = client.get_paginator("list_objects_v2")
    manifests: list[Manifest] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for entry in page.get("Contents", []):
            key = str(entry["Key"])
            if not key.endswith(".manifest.json") or not object_matches_selector(
                key, selector
            ):
                continue
            uri = f"s3://{bucket}/{key}"
            listed_etag = str(entry.get("ETag") or "").strip('"')
            if known_etags is not None and uri in known_etags:
                if listed_etag and known_etags[uri] != listed_etag:
                    raise ValueError(f"immutable manifest ETag changed: {uri}")
                continue
            response = client.get_object(Bucket=bucket, Key=key)
            body = response["Body"].read()
            etag = str(response.get("ETag") or entry.get("ETag") or "").strip('"')
            manifest = parse_manifest(uri, etag, body)
            validate_manifest_location(manifest, bucket)
            manifests.append(manifest)
    return sorted(manifests, key=lambda item: (item.closed_at, item.manifest_uri))


def discover_coverage_manifests(
    client,
    bucket: str,
    selector: Selector,
    known_etags: Mapping[str, str] | None = None,
) -> list[CoverageManifest]:
    prefix = COVERAGE_MANIFEST_PREFIX
    if selector.table:
        prefix += f"table={selector.table}/"
    manifests: list[CoverageManifest] = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for entry in page.get("Contents", []):
            key = str(entry["Key"])
            if not key.endswith(".coverage.json") or not object_matches_selector(
                key, selector
            ):
                continue
            uri = f"s3://{bucket}/{key}"
            listed_etag = str(entry.get("ETag") or "").strip('"')
            if known_etags is not None and uri in known_etags:
                if listed_etag and known_etags[uri] != listed_etag:
                    raise ValueError(f"immutable coverage ETag changed: {uri}")
                continue
            response = client.get_object(Bucket=bucket, Key=key)
            body = response["Body"].read()
            etag = str(response.get("ETag") or entry.get("ETag") or "").strip('"')
            coverage = parse_coverage_manifest(uri, etag, body)
            validate_coverage_location(coverage, bucket)
            verify_coverage_references(client, coverage)
            manifests.append(coverage)
    return sorted(manifests, key=lambda item: (item.closed_at, item.coverage_uri))


def known_immutable_etags(
    connection: PgConnection,
) -> tuple[dict[str, str], dict[str, str]]:
    with connection.cursor() as cursor:
        cursor.execute("select manifest_uri, manifest_etag from cdc_audit.cdc_files")
        manifests = {str(uri): str(etag) for uri, etag in cursor.fetchall()}
        cursor.execute(
            "select coverage_uri, coverage_etag from cdc_audit.cdc_coverage_files"
        )
        coverage = {str(uri): str(etag) for uri, etag in cursor.fetchall()}
    return manifests, coverage


def execute_bootstrap(connection: PgConnection, sql_dir: Path) -> None:
    with connection.cursor() as cursor:
        for path in sorted(sql_dir.glob("*.sql")):
            cursor.execute(path.read_text(encoding="utf-8"))
    connection.commit()


def register_manifests(connection: PgConnection, manifests: Sequence[Manifest]) -> None:
    statement = """
        insert into cdc_audit.cdc_files (
            manifest_uri, manifest_etag, object_uri, object_etag, object_sha256,
            object_size_bytes, source_table, topic, partition_id, offset_ranges,
            min_offset, max_offset, schema_id, manifest_row_count,
            operation_counts, ingest_date, source_ts_min, source_ts_max,
            closed_at, status
        ) values %s
        on conflict (manifest_uri) do nothing
    """
    values = [
        (
            item.manifest_uri,
            item.manifest_etag,
            item.object_uri,
            item.object_etag,
            item.object_sha256,
            item.object_size_bytes,
            item.table,
            item.topic,
            item.partition,
            Json(item.offset_ranges),
            item.min_offset,
            item.max_offset,
            item.schema_id,
            item.row_count,
            Json(item.operation_counts),
            item.ingest_date,
            item.source_ts_min,
            item.source_ts_max,
            item.closed_at,
            "DISCOVERED",
        )
        for item in manifests
    ]
    if not values:
        return
    with connection.cursor() as cursor:
        for item in manifests:
            cursor.execute(
                """
                select manifest_etag, object_uri, object_etag, object_sha256
                from cdc_audit.cdc_files where manifest_uri = %s
                """,
                (item.manifest_uri,),
            )
            existing = cursor.fetchone()
            expected = (
                item.manifest_etag,
                item.object_uri,
                item.object_etag,
                item.object_sha256,
            )
            if existing is not None and tuple(existing) != expected:
                raise ValueError(
                    f"immutable manifest identity changed: {item.manifest_uri}"
                )
        execute_values(cursor, statement, values)
    connection.commit()


def record_offset_ranges(
    cursor,
    *,
    coverage_kind: str,
    source_uri: str,
    source_etag: str,
    topic: str,
    partition: int,
    ranges: Iterable[tuple[int, int]],
    ingest_run_id: str,
) -> None:
    values = [
        (
            coverage_kind,
            source_uri,
            source_etag,
            topic,
            partition,
            start,
            end,
            ingest_run_id,
        )
        for start, end in ranges
    ]
    if values:
        execute_values(
            cursor,
            """
            insert into cdc_audit.cdc_offset_coverage (
                coverage_kind, source_uri, source_etag, topic, partition_id,
                range_start, range_end, recorded_by_run_id
            ) values %s on conflict do nothing
            """,
            values,
        )


def register_coverage_manifests(
    connection: PgConnection,
    manifests: Sequence[CoverageManifest],
    ingest_run_id: str,
) -> set[tuple[str, str, int]]:
    affected: set[tuple[str, str, int]] = set()
    with connection.cursor() as cursor:
        for item in manifests:
            cursor.execute(
                """
                select coverage_etag, landing_manifest_uri, landing_manifest_etag,
                       landing_object_uri, landing_object_etag, landing_object_sha256
                from cdc_audit.cdc_coverage_files where coverage_uri = %s
                """,
                (item.coverage_uri,),
            )
            existing = cursor.fetchone()
            expected = (
                item.coverage_etag,
                item.landing_manifest_uri,
                item.landing_manifest_etag,
                item.landing_object_uri,
                item.landing_object_etag,
                item.landing_object_sha256,
            )
            if existing is not None and tuple(existing) != expected:
                raise ValueError(
                    f"immutable coverage identity changed: {item.coverage_uri}"
                )
            cursor.execute(
                """
                insert into cdc_audit.cdc_coverage_files (
                    coverage_uri, coverage_etag, source_table, topic, partition_id,
                    consumed_offset_ranges, business_event_offset_ranges,
                    tombstone_offset_ranges, consumed_row_count,
                    business_event_count, tombstone_count, ingest_date, closed_at,
                    landing_manifest_uri, landing_manifest_etag, landing_object_uri,
                    landing_object_etag, landing_object_sha256,
                    landing_object_size_bytes, status, verified_by_run_id
                ) values (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, 'VERIFIED', %s
                ) on conflict (coverage_uri) do nothing
                """,
                (
                    item.coverage_uri,
                    item.coverage_etag,
                    item.table,
                    item.topic,
                    item.partition,
                    Json(item.consumed_offset_ranges),
                    Json(item.business_event_offset_ranges),
                    Json(item.tombstone_offset_ranges),
                    item.consumed_row_count,
                    item.business_event_count,
                    item.tombstone_count,
                    item.ingest_date,
                    item.closed_at,
                    item.landing_manifest_uri,
                    item.landing_manifest_etag,
                    item.landing_object_uri,
                    item.landing_object_etag,
                    item.landing_object_sha256,
                    item.landing_object_size_bytes,
                    ingest_run_id,
                ),
            )
            record_offset_ranges(
                cursor,
                coverage_kind="SOURCE_CONSUMED",
                source_uri=item.coverage_uri,
                source_etag=item.coverage_etag,
                topic=item.topic,
                partition=item.partition,
                ranges=item.consumed_offset_ranges,
                ingest_run_id=ingest_run_id,
            )
            record_offset_ranges(
                cursor,
                coverage_kind="TOMBSTONE_AUDITED",
                source_uri=item.coverage_uri,
                source_etag=item.coverage_etag,
                topic=item.topic,
                partition=item.partition,
                ranges=item.tombstone_offset_ranges,
                ingest_run_id=ingest_run_id,
            )
            affected.add((item.table, item.topic, item.partition))
    connection.commit()
    return affected


def start_run(
    connection: PgConnection,
    ingest_run_id: str,
    run_kind: str,
    dag_id: str | None,
    orchestration_run_id: str | None,
    discovered: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into cdc_audit.cdc_ingest_runs (
                ingest_run_id, dag_id, orchestration_run_id, run_kind, status,
                files_discovered
            ) values (%s, %s, %s, %s, 'STARTED', %s)
            on conflict (ingest_run_id) do update set
                status = 'STARTED',
                files_discovered = greatest(
                    cdc_audit.cdc_ingest_runs.files_discovered,
                    excluded.files_discovered
                ),
                finished_at = null,
                failure_summary = null
            """,
            (ingest_run_id, dag_id, orchestration_run_id, run_kind, discovered),
        )
    connection.commit()


def update_discovery_counts(
    connection: PgConnection,
    ingest_run_id: str,
    files_discovered: int,
    coverage_manifests_discovered: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update cdc_audit.cdc_ingest_runs
            set files_discovered = %s, coverage_manifests_discovered = %s
            where ingest_run_id = %s
            """,
            (files_discovered, coverage_manifests_discovered, ingest_run_id),
        )
    connection.commit()


def claim_next_file(
    connection: PgConnection,
    ingest_run_id: str,
    selector: Selector,
    run_kind: str,
    replay_request_id: str | None,
) -> tuple[str, int] | None:
    values: list[Any] = []
    if run_kind == "REPLAY":
        if not replay_request_id:
            raise ValueError("REPLAY ingest requires replay_request_id")
        filters = [
            "replay_request_id = %s",
            "(status in ('REPLAY_REQUESTED', 'FAILED') or "
            "(status = 'CLAIMED' and claim_expires_at < clock_timestamp()))",
        ]
        values.append(replay_request_id)
    else:
        if replay_request_id:
            raise ValueError("replay_request_id is only valid for REPLAY ingest")
        filters = [
            "replay_request_id is null",
            "(status in ('DISCOVERED', 'FAILED') or "
            "(status = 'CLAIMED' and claim_expires_at < clock_timestamp()))",
        ]
    if selector.table:
        filters.append("source_table = %s")
        values.append(selector.table)
    if selector.object_pattern:
        filters.append("position(%s in object_uri) > 0")
        values.append(selector.object_pattern)
    if selector.date_from:
        filters.append("ingest_date >= %s")
        values.append(selector.date_from)
    if selector.date_to:
        filters.append("ingest_date <= %s")
        values.append(selector.date_to)
    query = f"""
        select manifest_uri
        from cdc_audit.cdc_files
        where {" and ".join(filters)}
        order by closed_at, manifest_uri
        for update skip locked
        limit 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query, values)
        row = cursor.fetchone()
        if row is None:
            connection.commit()
            return None
        manifest_uri = str(row[0])
        cursor.execute(
            """
            update cdc_audit.cdc_files
            set status = 'CLAIMED',
                attempt_count = attempt_count + 1,
                first_attempt_at = coalesce(first_attempt_at, clock_timestamp()),
                last_attempt_at = clock_timestamp(),
                claimed_by_run_id = %s,
                claim_expires_at = clock_timestamp() + %s::interval,
                last_error = null
            where manifest_uri = %s
            returning attempt_count
            """,
            (ingest_run_id, f"{int(CLAIM_TTL.total_seconds())} seconds", manifest_uri),
        )
        attempt_row = cursor.fetchone()
        if attempt_row is None:
            raise ValueError(f"failed to claim manifest: {manifest_uri}")
        attempt_number = int(attempt_row[0])
        cursor.execute(
            """
            insert into cdc_audit.cdc_file_attempts (
                manifest_uri, ingest_run_id, attempt_number, status
            ) values (%s, %s, %s, 'CLAIMED')
            """,
            (manifest_uri, ingest_run_id, attempt_number),
        )
    connection.commit()
    return manifest_uri, attempt_number


def fetch_registered_manifest(connection: PgConnection, uri: str) -> Manifest:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select manifest_etag, object_uri, object_etag, object_sha256,
                   object_size_bytes, source_table, topic, partition_id,
                   offset_ranges, schema_id, manifest_row_count, operation_counts,
                   ingest_date, source_ts_min, source_ts_max, closed_at
            from cdc_audit.cdc_files where manifest_uri = %s
            """,
            (uri,),
        )
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"unregistered manifest: {uri}")
    ranges = tuple((int(item[0]), int(item[1])) for item in row[8])
    return Manifest(
        manifest_uri=uri,
        manifest_etag=str(row[0]),
        object_uri=str(row[1]),
        object_etag=str(row[2]),
        object_sha256=str(row[3]),
        object_size_bytes=int(row[4]),
        table=str(row[5]),
        topic=str(row[6]),
        partition=int(row[7]),
        offset_ranges=ranges,
        schema_id=str(row[9]),
        row_count=int(row[10]),
        operation_counts={str(k): int(v) for k, v in row[11].items()},
        ingest_date=row[12],
        source_ts_min=row[13],
        source_ts_max=row[14],
        closed_at=row[15],
    )


def read_parquet_object(client, manifest: Manifest) -> list[dict[str, Any]]:
    ref = parse_s3_uri(manifest.object_uri)
    response = client.get_object(Bucket=ref.bucket, Key=ref.key)
    body = response["Body"].read()
    etag = str(response.get("ETag", "")).strip('"')
    if etag != manifest.object_etag:
        raise ValueError(f"object ETag mismatch for {manifest.object_uri}")
    if len(body) != manifest.object_size_bytes:
        raise ValueError(f"object size mismatch for {manifest.object_uri}")
    digest = hashlib.sha256(body).hexdigest()
    if digest != manifest.object_sha256:
        raise ValueError(f"object SHA-256 mismatch for {manifest.object_uri}")
    rows = parquet.read_table(source=pa.BufferReader(body)).to_pylist()
    validate_rows(manifest, rows)
    return rows


def offsets_to_ranges(offsets: Iterable[int]) -> tuple[tuple[int, int], ...]:
    result: list[list[int]] = []
    for offset in sorted(set(offsets)):
        if not result or offset > result[-1][1] + 1:
            result.append([offset, offset])
        else:
            result[-1][1] = offset
    return tuple((start, end) for start, end in result)


def validate_rows(manifest: Manifest, rows: Sequence[dict[str, Any]]) -> None:
    if len(rows) != manifest.row_count:
        raise ValueError(
            f"Parquet rows {len(rows)} do not match manifest {manifest.row_count}"
        )
    expected_columns = set(BUSINESS_COLUMNS[manifest.table] + COMMON_COLUMNS)
    operations: dict[str, int] = {}
    event_ids: set[str] = set()
    offsets: list[int] = []
    source_timestamps: list[datetime] = []
    for row in rows:
        missing = expected_columns.difference(row)
        if missing:
            raise ValueError(f"Parquet row is missing columns: {sorted(missing)}")
        extra = set(row).difference(expected_columns)
        if extra:
            raise ValueError(f"Parquet row has unknown columns: {sorted(extra)}")
        op = str(row["_op"])
        operations[op] = operations.get(op, 0) + 1
        if op not in ALLOWED_OPERATIONS:
            raise ValueError(f"unsupported CDC operation: {op!r}")
        if (
            row["_topic"] != manifest.topic
            or int(row["_partition"]) != manifest.partition
        ):
            raise ValueError("Parquet topic/partition does not match manifest")
        if str(row["_schema_id"]) != manifest.schema_id:
            raise ValueError("Parquet schema ID does not match manifest")
        offset = int(row["_offset"])
        expected_event_id = f"{manifest.topic}:{manifest.partition}:{offset}"
        if row["_event_id"] != expected_event_id:
            raise ValueError("Parquet _event_id does not match Kafka coordinates")
        if expected_event_id in event_ids:
            raise ValueError(f"duplicate _event_id inside object: {expected_event_id}")
        event_ids.add(expected_event_id)
        offsets.append(offset)
        if row["_source_ts"] is not None:
            source_timestamps.append(row["_source_ts"])
    if operations != manifest.operation_counts:
        raise ValueError("Parquet operation counts do not match manifest")
    if offsets_to_ranges(offsets) != manifest.offset_ranges:
        raise ValueError("Parquet offset ranges do not match manifest")
    actual_min = min(source_timestamps) if source_timestamps else None
    actual_max = max(source_timestamps) if source_timestamps else None
    if actual_min != manifest.source_ts_min or actual_max != manifest.source_ts_max:
        raise ValueError("Parquet source timestamp bounds do not match manifest")


def merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def gap_ranges(ranges: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    return [
        (ranges[index - 1][1] + 1, ranges[index][0] - 1)
        for index in range(1, len(ranges))
        if ranges[index][0] > ranges[index - 1][1] + 1
    ]


def missing_ranges(
    proven_ranges: Sequence[tuple[int, int]], start: int, end: int
) -> list[tuple[int, int]]:
    missing: list[tuple[int, int]] = []
    cursor = start
    for range_start, range_end in merge_ranges(proven_ranges):
        if range_end < cursor:
            continue
        if range_start > end:
            break
        if range_start > cursor:
            missing.append((cursor, min(range_start - 1, end)))
        cursor = max(cursor, range_end + 1)
        if cursor > end:
            break
    if cursor <= end:
        missing.append((cursor, end))
    return missing


def recompute_watermark(
    cursor, table: str, topic: str, partition: int
) -> tuple[int, int]:
    cursor.execute(
        """
        select range_start, range_end
        from cdc_audit.cdc_offset_coverage
        where topic = %s and partition_id = %s
          and coverage_kind in ('NORMALIZED_LOADED', 'TOMBSTONE_AUDITED')
        """,
        (topic, partition),
    )
    all_ranges = [(int(row[0]), int(row[1])) for row in cursor.fetchall()]
    merged = merge_ranges(all_ranges)
    if not merged:
        raise ValueError(f"no loaded offset coverage for {topic}/{partition}")
    cursor.execute(
        """
        select min(range_start), max(range_end)
        from cdc_audit.cdc_offset_coverage
        where topic = %s and partition_id = %s
          and coverage_kind = 'NORMALIZED_LOADED'
        """,
        (topic, partition),
    )
    loaded_row = cursor.fetchone()
    if loaded_row is None or loaded_row[0] is None:
        raise ValueError(f"no normalized loaded coverage for {topic}/{partition}")
    first_seen = int(loaded_row[0])
    last_loaded_event = int(loaded_row[1])
    relevant = [item for item in merged if item[1] >= first_seen]
    if not relevant or relevant[0][0] > first_seen:
        raise ValueError(
            f"normalized coverage baseline is missing for {topic}/{partition}"
        )
    relevant[0] = (first_seen, relevant[0][1])
    cursor.execute(
        """
        select max(range_end)
        from cdc_audit.cdc_offset_coverage
        where topic = %s and partition_id = %s
        """,
        (topic, partition),
    )
    last_seen_row = cursor.fetchone()
    last_seen = max(last_loaded_event, int(last_seen_row[0]))
    gaps = missing_ranges(relevant, first_seen, last_seen)
    contiguous = gaps[0][0] - 1 if gaps else last_seen
    cursor.execute(
        sql.SQL(
            """
            select _source_lsn, _source_ts
            from raw_cdc.{}
            where _topic = %s and _partition = %s and _offset <= %s
            order by _offset desc limit 1
            """
        ).format(sql.Identifier(table)),
        (topic, partition, contiguous),
    )
    source_row = cursor.fetchone()
    source_lsn = source_row[0] if source_row else None
    source_ts = source_row[1] if source_row else None
    cursor.execute(
        """
        insert into cdc_audit.cdc_partition_watermarks (
            topic, partition_id, first_seen_offset, last_contiguous_offset,
            last_seen_offset, last_loaded_event_offset, gap_count, gap_ranges,
            source_lsn, source_ts
        ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        on conflict (topic, partition_id) do update set
            first_seen_offset = excluded.first_seen_offset,
            last_contiguous_offset = excluded.last_contiguous_offset,
            last_seen_offset = excluded.last_seen_offset,
            last_loaded_event_offset = excluded.last_loaded_event_offset,
            gap_count = excluded.gap_count,
            gap_ranges = excluded.gap_ranges,
            source_lsn = excluded.source_lsn,
            source_ts = excluded.source_ts,
            updated_at = clock_timestamp()
        """,
        (
            topic,
            partition,
            first_seen,
            contiguous,
            last_seen,
            last_loaded_event,
            len(gaps),
            Json(gaps),
            source_lsn,
            source_ts,
        ),
    )
    return contiguous, len(gaps)


def load_claimed_file(
    connection: PgConnection,
    manifest: Manifest,
    attempt_number: int,
    ingest_run_id: str,
    rows: Sequence[dict[str, Any]],
) -> tuple[int, int, int]:
    columns = (
        BUSINESS_COLUMNS[manifest.table] + COMMON_COLUMNS + ("_source_object_uri",)
    )
    values = [
        (*tuple(row[column] for column in columns[:-1]), manifest.object_uri)
        for row in rows
    ]
    temp_name = f"cdc_stage_{uuid.uuid4().hex}"
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                "create temp table {} (like raw_cdc.{} including defaults) on commit drop"
            ).format(sql.Identifier(temp_name), sql.Identifier(manifest.table))
        )
        insert_stage = sql.SQL("insert into {} ({}) values %s").format(
            sql.Identifier(temp_name),
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        )
        execute_values(cursor, insert_stage.as_string(cursor), values, page_size=1000)
        insert_target = sql.SQL(
            "insert into raw_cdc.{} ({}) select {} from {} "
            "on conflict (_event_id) do nothing"
        ).format(
            sql.Identifier(manifest.table),
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(temp_name),
        )
        cursor.execute(insert_target)
        inserted = cursor.rowcount
        duplicates = len(rows) - inserted
        cursor.execute(
            """
            update cdc_audit.cdc_files
            set status = 'LOADED', loaded_by_run_id = %s,
                loaded_at = clock_timestamp(), claim_expires_at = null,
                last_error = null, replay_request_id = null
            where manifest_uri = %s and status = 'CLAIMED'
              and claimed_by_run_id = %s
            """,
            (ingest_run_id, manifest.manifest_uri, ingest_run_id),
        )
        if cursor.rowcount != 1:
            raise ValueError(f"file claim was lost: {manifest.manifest_uri}")
        record_offset_ranges(
            cursor,
            coverage_kind="NORMALIZED_LOADED",
            source_uri=manifest.manifest_uri,
            source_etag=manifest.manifest_etag,
            topic=manifest.topic,
            partition=manifest.partition,
            ranges=manifest.offset_ranges,
            ingest_run_id=ingest_run_id,
        )
        _, gaps = recompute_watermark(
            cursor, manifest.table, manifest.topic, manifest.partition
        )
        status = "PASS" if inserted + duplicates == len(rows) else "FAIL"
        cursor.execute(
            """
            insert into cdc_audit.cdc_reconciliation (
                ingest_run_id, manifest_uri, source_table, object_rows,
                warehouse_inserted_rows, duplicate_rows, rejected_rows,
                gap_count, status, failure_reason
            ) values (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s)
            """,
            (
                ingest_run_id,
                manifest.manifest_uri,
                manifest.table,
                len(rows),
                inserted,
                duplicates,
                gaps,
                status,
                None if status == "PASS" else "inserted + duplicates != object rows",
            ),
        )
        cursor.execute(
            """
            update cdc_audit.cdc_file_attempts
            set status = 'SUCCEEDED', object_rows = %s, inserted_rows = %s,
                duplicate_rows = %s, rejected_rows = 0,
                finished_at = clock_timestamp()
            where manifest_uri = %s and attempt_number = %s
            """,
            (len(rows), inserted, duplicates, manifest.manifest_uri, attempt_number),
        )
    connection.commit()
    return inserted, duplicates, gaps


def mark_file_failed(
    connection: PgConnection,
    manifest_uri: str,
    attempt_number: int,
    ingest_run_id: str,
    error: Exception,
) -> None:
    connection.rollback()
    message = f"{type(error).__name__}: {error}"[:65535]
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update cdc_audit.cdc_files
            set status = 'FAILED', claim_expires_at = null, last_error = %s
            where manifest_uri = %s and claimed_by_run_id = %s
            """,
            (message, manifest_uri, ingest_run_id),
        )
        cursor.execute(
            """
            update cdc_audit.cdc_file_attempts
            set status = 'FAILED', finished_at = clock_timestamp(), error_message = %s
            where manifest_uri = %s and attempt_number = %s
            """,
            (message, manifest_uri, attempt_number),
        )
    connection.commit()


def finish_run(
    connection: PgConnection,
    ingest_run_id: str,
    status: str,
    *,
    files_claimed: int,
    files_loaded: int,
    object_rows: int,
    inserted_rows: int,
    duplicate_rows: int,
    gap_count: int,
    failure: str | None = None,
) -> None:
    connection.rollback()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update cdc_audit.cdc_ingest_runs r
            set status = %s,
                files_claimed = (
                    select count(*) from cdc_audit.cdc_file_attempts a
                    where a.ingest_run_id = r.ingest_run_id
                ),
                files_loaded = (
                    select count(*) from cdc_audit.cdc_reconciliation x
                    where x.ingest_run_id = r.ingest_run_id and x.status = 'PASS'
                ),
                object_rows = coalesce((
                    select sum(x.object_rows) from cdc_audit.cdc_reconciliation x
                    where x.ingest_run_id = r.ingest_run_id
                ), 0),
                inserted_rows = coalesce((
                    select sum(x.warehouse_inserted_rows)
                    from cdc_audit.cdc_reconciliation x
                    where x.ingest_run_id = r.ingest_run_id
                ), 0),
                duplicate_rows = coalesce((
                    select sum(x.duplicate_rows) from cdc_audit.cdc_reconciliation x
                    where x.ingest_run_id = r.ingest_run_id
                ), 0),
                gap_count = coalesce((
                    select sum(w.gap_count)
                    from cdc_audit.cdc_partition_watermarks w
                    join (
                        select topic, partition_id
                        from cdc_audit.cdc_files
                        where loaded_by_run_id = r.ingest_run_id
                        union
                        select topic, partition_id
                        from cdc_audit.cdc_coverage_files
                        where verified_by_run_id = r.ingest_run_id
                    ) touched using (topic, partition_id)
                ), 0),
                finished_at = clock_timestamp(), failure_summary = %s
            where ingest_run_id = %s
            """,
            (
                status,
                failure,
                ingest_run_id,
            ),
        )
    connection.commit()


def ingest(
    connection: PgConnection,
    client,
    bucket: str,
    selector: Selector,
    ingest_run_id: str,
    run_kind: str,
    dag_id: str | None,
    orchestration_run_id: str | None,
    replay_request_id: str | None = None,
) -> IngestSummary:
    start_run(
        connection,
        ingest_run_id,
        run_kind,
        dag_id,
        orchestration_run_id,
        0,
    )
    claimed = loaded = object_rows = inserted = duplicates = gap_count = 0
    try:
        known_manifests, known_coverage = known_immutable_etags(connection)
        manifests = discover_manifests(
            client, bucket, selector, known_etags=known_manifests
        )
        coverage_manifests = discover_coverage_manifests(
            client, bucket, selector, known_etags=known_coverage
        )
        update_discovery_counts(
            connection,
            ingest_run_id,
            len(manifests),
            len(coverage_manifests),
        )
        register_manifests(connection, manifests)
        affected = register_coverage_manifests(
            connection, coverage_manifests, ingest_run_id
        )
        if affected:
            with connection.cursor() as cursor:
                for table, topic, partition in affected:
                    cursor.execute(
                        """
                        select exists (
                            select 1 from cdc_audit.cdc_offset_coverage
                            where topic = %s and partition_id = %s
                              and coverage_kind = 'NORMALIZED_LOADED'
                        )
                        """,
                        (topic, partition),
                    )
                    normalized_row = cursor.fetchone()
                    if normalized_row is not None and normalized_row[0]:
                        _, gap_count = recompute_watermark(
                            cursor, table, topic, partition
                        )
            connection.commit()
        while claim := claim_next_file(
            connection,
            ingest_run_id,
            selector,
            run_kind,
            replay_request_id,
        ):
            manifest_uri, attempt_number = claim
            claimed += 1
            manifest = fetch_registered_manifest(connection, manifest_uri)
            try:
                rows = read_parquet_object(client, manifest)
                file_inserted, file_duplicates, gap_count = load_claimed_file(
                    connection, manifest, attempt_number, ingest_run_id, rows
                )
            except Exception as exc:
                mark_file_failed(
                    connection, manifest_uri, attempt_number, ingest_run_id, exc
                )
                raise
            loaded += 1
            object_rows += len(rows)
            inserted += file_inserted
            duplicates += file_duplicates
        finish_run(
            connection,
            ingest_run_id,
            "SUCCEEDED",
            files_claimed=claimed,
            files_loaded=loaded,
            object_rows=object_rows,
            inserted_rows=inserted,
            duplicate_rows=duplicates,
            gap_count=gap_count,
        )
    except Exception as exc:
        finish_run(
            connection,
            ingest_run_id,
            "FAILED",
            files_claimed=claimed,
            files_loaded=loaded,
            object_rows=object_rows,
            inserted_rows=inserted,
            duplicate_rows=duplicates,
            gap_count=gap_count,
            failure=f"{type(exc).__name__}: {exc}"[:65535],
        )
        raise
    return IngestSummary(*fetch_run_summary(connection, ingest_run_id))


def fetch_run_summary(
    connection: PgConnection, ingest_run_id: str
) -> tuple[str, int, int, int, int, int, int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select ingest_run_id, files_discovered, files_loaded, object_rows,
                   inserted_rows, duplicate_rows, gap_count
            from cdc_audit.cdc_ingest_runs where ingest_run_id = %s
            """,
            (ingest_run_id,),
        )
        row = cursor.fetchone()
    if row is None:
        raise ValueError(f"missing ingest run summary: {ingest_run_id}")
    return (
        str(row[0]),
        int(row[1]),
        int(row[2]),
        int(row[3]),
        int(row[4]),
        int(row[5]),
        int(row[6]),
    )


def request_replay(
    connection: PgConnection,
    replay_request_id: str,
    requested_by: str,
    selector: Selector,
) -> int:
    if not any(
        (selector.table, selector.date_from, selector.date_to, selector.object_pattern)
    ):
        raise ValueError("replay requires at least one table/date/object selector")
    filters = ["status = 'LOADED'"]
    values: list[Any] = []
    if selector.table:
        filters.append("source_table = %s")
        values.append(selector.table)
    if selector.date_from:
        filters.append("ingest_date >= %s")
        values.append(selector.date_from)
    if selector.date_to:
        filters.append("ingest_date <= %s")
        values.append(selector.date_to)
    if selector.object_pattern:
        filters.append("position(%s in object_uri) > 0")
        values.append(selector.object_pattern)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select requested_by, source_table, ingest_date_from, ingest_date_to,
                   object_uri_pattern, selected_file_count
            from cdc_audit.cdc_replay_requests
            where replay_request_id = %s
            """,
            (replay_request_id,),
        )
        existing = cursor.fetchone()
        expected = (
            requested_by,
            selector.table,
            selector.date_from,
            selector.date_to,
            selector.object_pattern,
        )
        if existing is not None:
            if tuple(existing[:5]) != expected:
                raise ValueError(
                    f"replay request identity changed: {replay_request_id}"
                )
            connection.commit()
            return int(existing[5])
        cursor.execute(
            """
            insert into cdc_audit.cdc_replay_requests (
                replay_request_id, requested_by, source_table, ingest_date_from,
                ingest_date_to, object_uri_pattern, status
            ) values (%s, %s, %s, %s, %s, %s, 'STARTED')
            """,
            (
                replay_request_id,
                requested_by,
                selector.table,
                selector.date_from,
                selector.date_to,
                selector.object_pattern,
            ),
        )
        cursor.execute(
            f"""
            update cdc_audit.cdc_files
            set status = 'REPLAY_REQUESTED', claimed_by_run_id = null,
                claim_expires_at = null, last_error = null,
                replay_request_id = %s
            where {" and ".join(filters)}
            """,
            [replay_request_id, *values],
        )
        selected = cursor.rowcount
        cursor.execute(
            """
            update cdc_audit.cdc_replay_requests
            set status = 'READY', selected_file_count = %s,
                completed_at = clock_timestamp()
            where replay_request_id = %s
            """,
            (selected, replay_request_id),
        )
    connection.commit()
    return selected


def record_orchestration_failure(
    connection: PgConnection,
    ingest_run_id: str,
    dag_id: str | None,
    orchestration_run_id: str | None,
    failure_summary: str,
) -> None:
    """Persist callback failures without replacing a loader's richer audit row."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            insert into cdc_audit.cdc_ingest_runs (
                ingest_run_id, dag_id, orchestration_run_id, run_kind, status,
                started_at, finished_at, failure_summary
            ) values (%s, %s, %s, 'SCHEDULED', 'FAILED',
                      clock_timestamp(), clock_timestamp(), %s)
            on conflict (ingest_run_id) do update set
                status = 'FAILED',
                finished_at = coalesce(cdc_audit.cdc_ingest_runs.finished_at,
                                       clock_timestamp()),
                failure_summary = coalesce(
                    cdc_audit.cdc_ingest_runs.failure_summary, excluded.failure_summary
                )
            where cdc_audit.cdc_ingest_runs.status <> 'SUCCEEDED'
            """,
            (
                ingest_run_id,
                dag_id,
                orchestration_run_id,
                failure_summary[:65535],
            ),
        )
    connection.commit()


def selector_from_args(args: argparse.Namespace) -> Selector:
    selector = Selector(
        table=args.table,
        date_from=date.fromisoformat(args.date_from) if args.date_from else None,
        date_to=date.fromisoformat(args.date_to) if args.date_to else None,
        object_pattern=args.object_pattern,
    )
    if (
        selector.date_from
        and selector.date_to
        and selector.date_from > selector.date_to
    ):
        raise ValueError("date-from cannot be later than date-to")
    return selector


def add_selector_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--table", choices=sorted(BUSINESS_COLUMNS))
    parser.add_argument(
        "--date-from", help="Inclusive manifest ingest date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--date-to", help="Inclusive manifest ingest date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--object-pattern", help="Substring matched against the object URI."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("POSTGRES_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("POSTGRES_PORT", "5432"))
    )
    parser.add_argument(
        "--database", default=os.environ.get("POSTGRES_DB", "olist_analytics")
    )
    parser.add_argument("--user", default=os.environ.get("POSTGRES_USER", "olist"))
    parser.add_argument("--password", default=os.environ.get("POSTGRES_PASSWORD"))
    parser.add_argument(
        "--password-file", default=os.environ.get("POSTGRES_PASSWORD_FILE")
    )
    parser.add_argument("--bootstrap-sql-dir", default="infra/postgres")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("bootstrap")

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument(
        "--s3-endpoint",
        default=os.environ.get("CDC_S3_ENDPOINT", "http://localhost:9000"),
    )
    ingest_parser.add_argument(
        "--s3-region", default=os.environ.get("CDC_S3_REGION", "us-east-1")
    )
    ingest_parser.add_argument(
        "--s3-access-key",
        default=os.environ.get("CDC_S3_ACCESS_KEY", "olist_cdc_loader"),
    )
    ingest_parser.add_argument(
        "--s3-secret-key", default=os.environ.get("CDC_S3_SECRET_KEY")
    )
    ingest_parser.add_argument(
        "--s3-secret-file", default=os.environ.get("CDC_S3_SECRET_FILE")
    )
    ingest_parser.add_argument(
        "--bucket", default=os.environ.get("CDC_S3_BUCKET", "olist-cdc")
    )
    ingest_parser.add_argument("--ingest-run-id", default=f"manual_{uuid.uuid4().hex}")
    ingest_parser.add_argument(
        "--run-kind", choices=("SCHEDULED", "MANUAL", "REPLAY"), default="MANUAL"
    )
    ingest_parser.add_argument("--dag-id")
    ingest_parser.add_argument("--orchestration-run-id")
    ingest_parser.add_argument("--replay-request-id")
    add_selector_arguments(ingest_parser)

    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument(
        "--replay-request-id", default=f"replay_{uuid.uuid4().hex}"
    )
    replay_parser.add_argument(
        "--requested-by", default=os.environ.get("USER", "operator")
    )
    add_selector_arguments(replay_parser)

    failure_parser = subparsers.add_parser("record-failure")
    failure_parser.add_argument("--ingest-run-id", required=True)
    failure_parser.add_argument("--dag-id")
    failure_parser.add_argument("--orchestration-run-id")
    failure_parser.add_argument("--failure-summary", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with postgres_connection(args) as connection:
        if args.command == "bootstrap":
            execute_bootstrap(connection, Path(args.bootstrap_sql_dir))
            return 0
        if args.command == "record-failure":
            record_orchestration_failure(
                connection,
                args.ingest_run_id,
                args.dag_id,
                args.orchestration_run_id,
                args.failure_summary,
            )
            return 0
        selector = selector_from_args(args)
        if args.command == "replay":
            selected = request_replay(
                connection, args.replay_request_id, args.requested_by, selector
            )
            print(
                json.dumps(
                    {
                        "replay_request_id": args.replay_request_id,
                        "selected_files": selected,
                    }
                )
            )
            return 0
        summary = ingest(
            connection,
            s3_client(args),
            args.bucket,
            selector,
            args.ingest_run_id,
            args.run_kind,
            args.dag_id,
            args.orchestration_run_id,
            args.replay_request_id,
        )
        print(json.dumps(summary.as_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
