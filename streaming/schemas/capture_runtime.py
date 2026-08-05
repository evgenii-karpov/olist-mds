"""Capture Debezium/Apicurio writer schemas from a live Kafka snapshot.

Only Confluent framing metadata and schema documents are retained.  Kafka
payload bytes are inspected in memory and are never written to the evidence
bundle or printed.  The resulting directory is suitable for the existing
``writer_schemas capture-bundle`` importer.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .avro import parse_confluent_frame
from .registry import ApicurioCCompatClient, RecursiveSchemaResolver
from .writer_schemas import CAPTURED, ENTITY_NAMES, SCHEMA_KINDS

BUSINESS_TOPICS = tuple(f"olist_cdc.olist_oltp.{entity}" for entity in ENTITY_NAMES)
CONNECTOR_NAME = "olist-mysql-cdc"
REGISTRY_GROUP = "olist_cdc"
DEFAULT_BOOTSTRAP_SERVERS = "localhost:9092"
DEFAULT_REGISTRY_URL = "http://localhost:8081/apis/ccompat/v7"
DEFAULT_TIMEOUT_SECONDS = 300.0
_SAFE_ARTIFACT = re.compile(r"[^A-Za-z0-9._-]+")


class RuntimeCaptureError(RuntimeError):
    """Live writer-schema capture failed closed."""


class RegistryMetadataClient:
    """Read schema metadata without retaining Kafka record bytes."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def artifact_metadata(
        self, artifact_id: str, version: str
    ) -> tuple[str, str, str] | None:
        encoded_group = quote(REGISTRY_GROUP, safe="")
        encoded_artifact = quote(artifact_id, safe="")
        encoded_version = quote(str(version), safe="")
        paths = (
            f"/groups/{encoded_group}/artifacts/{encoded_artifact}/versions/{encoded_version}",
            f"/groups/{encoded_group}/artifacts/{encoded_artifact}/versions/{encoded_version}/meta",
        )
        for path in paths:
            request = Request(
                f"{self.base_url.replace('/apis/ccompat/v7', '/apis/registry/v2')}{path}",
                headers={"Accept": "application/json"},
                method="GET",
            )
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    raw = response.read().decode("utf-8", errors="replace")
            except (HTTPError, URLError, TimeoutError, OSError, Exception):
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(value, Mapping):
                continue
            returned_id = value.get("id", value.get("artifactId", artifact_id))
            returned_version = value.get("version", version)
            if isinstance(returned_id, str) and returned_id:
                return REGISTRY_GROUP, returned_id, str(returned_version)
        return None


def _artifact_metadata(
    document: Any,
    *,
    topic: str,
    kind: str,
    registry: RegistryMetadataClient,
) -> tuple[str, str]:
    subject = getattr(document, "subject", None)
    version = getattr(document, "version", None)
    if isinstance(subject, str) and subject and isinstance(version, str) and version:
        return subject, version

    # Apicurio's compatibility endpoint may omit subject/version from an ID
    # lookup.  Resolve metadata through the registry API; never use a mutable
    # ``latest`` endpoint as provenance.
    candidates = (f"{topic}-{kind}", topic, f"{topic}.{kind}")
    for candidate in candidates:
        metadata = registry.artifact_metadata(candidate, "1")
        if metadata is not None:
            _, artifact_id, artifact_version = metadata
            return artifact_id, artifact_version
    raise RuntimeCaptureError(
        f"registry did not return artifact provenance for {topic} {kind} schema"
    )


def _schema_file_name(schema_id: int, fingerprint: str) -> str:
    return f"schema-{schema_id}-{fingerprint[:16]}.avsc"


def _new_manifest() -> dict[str, Any]:
    return {
        "manifest_version": 1,
        "capture_state": CAPTURED,
        "capture_command": (
            "python -m streaming.schemas.writer_schemas capture-bundle "
            "--bundle <runtime-export-directory>"
        ),
        "entities": [
            {
                "entity": entity,
                "key": {"state": CAPTURED, "schemas": []},
                "value": {"state": CAPTURED, "schemas": []},
            }
            for entity in ENTITY_NAMES
        ],
    }


def _capture_with_consumer(
    *,
    bootstrap_servers: str,
    registry_url: str,
    output: Path,
    timeout_seconds: float,
    group_id: str,
    expected_business_records: int,
) -> None:
    try:
        from confluent_kafka import Consumer, KafkaError
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
        raise RuntimeCaptureError(
            "confluent-kafka is required for runtime capture"
        ) from exc

    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise RuntimeCaptureError(
            f"capture output must be a new empty directory: {output}"
        )
    output.mkdir(parents=True, exist_ok=True)

    registry_reader = ApicurioCCompatClient(registry_url, timeout_seconds=15.0)
    metadata_reader = RegistryMetadataClient(registry_url, timeout_seconds=15.0)
    resolver = RecursiveSchemaResolver(registry_reader)
    manifest = _new_manifest()
    entities = {entry["entity"]: entry for entry in manifest["entities"]}
    captured: dict[tuple[str, str], dict[int, int]] = {}
    records_seen = 0
    eof_partitions: set[tuple[str, int]] = set()
    deadline = time.monotonic() + timeout_seconds
    settle_deadline: float | None = None

    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "enable.partition.eof": True,
            "session.timeout.ms": 10000,
        }
    )
    consumer.subscribe(list(BUSINESS_TOPICS))
    try:
        while True:
            # A connector task can report RUNNING while an initial snapshot is
            # still publishing records.  EOF is therefore only a temporary
            # watermark; do not finish merely because all schema slots have
            # been seen.  Wait until the expected record count is observed,
            # then allow a short settle window for the final partition polls.
            if (
                len(captured) == len(ENTITY_NAMES) * len(SCHEMA_KINDS)
                and records_seen >= expected_business_records
            ):
                if settle_deadline is None:
                    settle_deadline = time.monotonic() + 5.0
                if time.monotonic() >= settle_deadline:
                    break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                pending = [
                    f"{entity}:{kind}"
                    for entity in ENTITY_NAMES
                    for kind in SCHEMA_KINDS
                    if (entity, kind) not in captured
                ]
                raise RuntimeCaptureError(
                    "timed out waiting for live writer schemas: " + ", ".join(pending)
                )
            message = consumer.poll(min(1.0, remaining))
            if message is None:
                continue
            error = message.error()
            if error is not None:
                topic = message.topic()
                partition = message.partition()
                if error.code() == KafkaError._PARTITION_EOF:
                    if topic is not None and partition is not None:
                        eof_partitions.add((topic, partition))
                    continue
                raise RuntimeCaptureError(f"Kafka capture failed: {error.name()}")

            topic = message.topic()
            partition = message.partition()
            if topic is None or partition is None:
                raise RuntimeCaptureError("Kafka message omitted topic or partition")
            if topic not in BUSINESS_TOPICS:
                continue
            records_seen += 1
            entity = topic.rsplit(".", maxsplit=1)[-1]
            for kind, raw_bytes in (("key", message.key()), ("value", message.value())):
                if raw_bytes is None:
                    if kind == "value":
                        continue
                    raise RuntimeCaptureError(f"null key encountered on {topic}")
                try:
                    frame = parse_confluent_frame(raw_bytes)
                except ValueError as exc:
                    raise RuntimeCaptureError(
                        f"invalid Confluent {kind} framing on {topic}"
                    ) from exc
                identity = (entity, kind)
                if identity in captured and frame.schema_id in captured[identity]:
                    continue
                resolved = resolver.resolve(frame.schema_id)
                schema = resolved.self_contained_schema
                if not isinstance(schema, Mapping) or schema.get("type") != "record":
                    raise RuntimeCaptureError(
                        f"registry schema {frame.schema_id} for {topic} {kind} is not a record"
                    )
                artifact_id, artifact_version = _artifact_metadata(
                    registry_reader.schema_by_id(frame.schema_id),
                    topic=topic,
                    kind=kind,
                    registry=metadata_reader,
                )
                relative_dir = Path(entity) / kind
                relative_path = relative_dir / _schema_file_name(
                    frame.schema_id, resolved.fingerprint_sha256
                )
                path = output / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                captured.setdefault(identity, {})[frame.schema_id] = 1
                entry = entities[entity][kind]["schemas"]
                entry.append(
                    {
                        "path": relative_path.as_posix(),
                        "sha256": resolved.fingerprint_sha256,
                        "provenance": {
                            "registry_url": registry_url,
                            "registry_group": REGISTRY_GROUP,
                            "artifact_id": artifact_id,
                            "artifact_version": artifact_version,
                            "schema_id": frame.schema_id,
                            "captured_at_utc": datetime.now(UTC)
                            .isoformat()
                            .replace("+00:00", "Z"),
                            "connector_name": CONNECTOR_NAME,
                            "topic": topic,
                        },
                    }
                )
    finally:
        consumer.close()

    if records_seen < expected_business_records:
        raise RuntimeCaptureError(
            f"live snapshot contained {records_seen} business records; "
            f"expected at least {expected_business_records}"
        )

    for entity in ENTITY_NAMES:
        for kind in SCHEMA_KINDS:
            schemas = entities[entity][kind]["schemas"]
            if not schemas:
                raise RuntimeCaptureError(f"no captured {entity}:{kind} schema")
            schemas.sort(
                key=lambda item: (int(item["provenance"]["schema_id"]), item["sha256"])
            )
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default=DEFAULT_BOOTSTRAP_SERVERS)
    parser.add_argument("--registry-url", default=DEFAULT_REGISTRY_URL)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument("--group-id", required=True)
    parser.add_argument("--expected-business-records", type=int, default=79)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.timeout_seconds <= 0:
            raise RuntimeCaptureError("capture timeout must be positive")
        _capture_with_consumer(
            bootstrap_servers=args.bootstrap_servers,
            registry_url=args.registry_url,
            output=args.output,
            timeout_seconds=args.timeout_seconds,
            group_id=args.group_id,
            expected_business_records=args.expected_business_records,
        )
    except (RuntimeCaptureError, OSError, ValueError) as exc:
        print(f"runtime writer-schema capture failed: {exc}")
        return 1
    print(f"runtime writer-schema evidence captured into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
