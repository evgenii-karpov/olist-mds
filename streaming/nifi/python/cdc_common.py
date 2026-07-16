from __future__ import annotations

import json
import struct
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any

from fastavro import parse_schema, schemaless_reader, writer


class ApicurioAvroDecoder:
    """Resolve Confluent framing and recursive ccompat schema references."""

    def __init__(self, registry_url: str) -> None:
        self.base_url = registry_url.rstrip("/") + "/apis/ccompat/v7"
        self.named_schemas: dict[str, Any] = {}
        self.schemas_by_id: dict[int, Any] = {}
        self.schemas_by_subject_version: dict[tuple[str, int], Any] = {}

    def _get_json(self, path: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(
                f"{self.base_url}{path}", timeout=10
            ) as response:
                value = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ValueError(f"registry schema was not found: {path}") from exc
            raise
        if not isinstance(value, dict):
            raise ValueError(f"registry response is not an object: {path}")
        return value

    def _parse_subject_version(self, subject: str, version: int) -> Any:
        key = (subject, version)
        if key in self.schemas_by_subject_version:
            return self.schemas_by_subject_version[key]
        encoded = urllib.parse.quote(subject, safe="")
        metadata = self._get_json(f"/subjects/{encoded}/versions/{version}")
        self._parse_references(metadata.get("references", []))
        schema = parse_schema(json.loads(metadata["schema"]), self.named_schemas)
        self.schemas_by_subject_version[key] = schema
        return schema

    def _parse_references(self, references: list[dict[str, Any]]) -> None:
        for reference in references:
            self._parse_subject_version(
                str(reference["subject"]), int(reference["version"])
            )

    def _schema_by_id(self, schema_id: int) -> Any:
        if schema_id in self.schemas_by_id:
            return self.schemas_by_id[schema_id]
        metadata = self._get_json(f"/schemas/ids/{schema_id}")
        self._parse_references(metadata.get("references", []))
        schema = parse_schema(json.loads(metadata["schema"]), self.named_schemas)
        self.schemas_by_id[schema_id] = schema
        return schema

    def decode(self, payload: bytes) -> tuple[int, Any]:
        if len(payload) < 5 or payload[0] != 0:
            raise ValueError("payload is not Confluent-framed Avro")
        schema_id = struct.unpack(">I", payload[1:5])[0]
        if schema_id <= 0:
            raise ValueError(f"invalid numeric schema id: {schema_id}")
        value = schemaless_reader(BytesIO(payload[5:]), self._schema_by_id(schema_id))
        return schema_id, value


def json_default(value: Any) -> Any:
    if isinstance(value, (datetime, Decimal)):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def epoch_micros(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=value.tzinfo or UTC)
    number = int(value)
    return datetime.fromtimestamp(number / 1_000_000, tz=UTC)


def epoch_millis(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=value.tzinfo or UTC)
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)


def load_schema(schema_directory: str, kind: str, table: str | None = None) -> Any:
    if kind == "landing":
        path = Path(schema_directory) / "cdc-landing" / "v1.avsc"
    else:
        if not table:
            raise ValueError("normalized schema requires a table")
        path = Path(schema_directory) / "normalized" / table / "v1.avsc"
    return parse_schema(json.loads(path.read_text(encoding="utf-8")))


def avro_container(schema: Any, record: dict[str, Any]) -> bytes:
    output = BytesIO()
    writer(output, schema, [record], codec="deflate")
    return output.getvalue()


def to_long(value: Any) -> int | None:
    return None if value is None else int(value)


def offset_ranges(offsets: list[int]) -> list[list[int]]:
    ranges: list[list[int]] = []
    for offset in sorted(set(offsets)):
        if not ranges or offset > ranges[-1][1] + 1:
            ranges.append([offset, offset])
        else:
            ranges[-1][1] = offset
    return ranges
