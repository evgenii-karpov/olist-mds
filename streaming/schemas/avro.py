"""Avro identity and Confluent wire-framing primitives.

Registry numeric IDs identify schemas only inside one disposable lab
generation. ``schema_fingerprint_sha256`` is the durable identity used by the
entity contracts and schema archive. It hashes deterministic canonical JSON,
including logical types and Connect metadata that Avro's parsing canonical form
would intentionally discard.
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

CONFLUENT_MAGIC_BYTE = 0
CONFLUENT_HEADER_SIZE = 5
FINGERPRINT_ALGORITHM = "sha256-canonical-json-v1"


class AvroContractError(ValueError):
    """Base error for deterministic schema-contract failures."""


class ConfluentFramingError(AvroContractError):
    """The raw Kafka bytes do not satisfy Confluent Avro framing."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ConfluentFrame:
    schema_id: int
    payload: bytes


@dataclass(frozen=True)
class FrameInspection:
    is_tombstone: bool
    framing_valid: bool
    schema_id: int | None
    payload: bytes | None
    error_code: str | None
    error_message: str | None


def canonical_schema_json(schema: Any) -> str:
    """Serialize a parsed Avro schema with stable keys and no whitespace."""

    try:
        return json.dumps(
            schema,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AvroContractError(f"schema is not canonical JSON: {exc}") from exc


def schema_fingerprint_sha256(schema: Any) -> str:
    canonical = canonical_schema_json(schema).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def parse_schema_json(schema_json: str | bytes) -> Any:
    if isinstance(schema_json, bytes):
        schema_json = schema_json.decode("utf-8")
    try:
        return json.loads(schema_json)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AvroContractError(f"invalid Avro schema JSON: {exc}") from exc


def parse_confluent_frame(data: bytes | bytearray | memoryview) -> ConfluentFrame:
    """Parse magic byte + unsigned four-byte big-endian schema ID + payload."""

    raw = bytes(data)
    if len(raw) < CONFLUENT_HEADER_SIZE:
        raise ConfluentFramingError(
            "frame_too_short",
            f"Confluent frame has {len(raw)} bytes; at least 5 are required",
        )
    if raw[0] != CONFLUENT_MAGIC_BYTE:
        raise ConfluentFramingError(
            "invalid_magic_byte",
            f"Confluent magic byte must be 0, got {raw[0]}",
        )
    schema_id = struct.unpack(">I", raw[1:CONFLUENT_HEADER_SIZE])[0]
    if schema_id == 0:
        raise ConfluentFramingError(
            "invalid_schema_id", "Confluent schema ID must be a positive integer"
        )
    return ConfluentFrame(schema_id=schema_id, payload=raw[CONFLUENT_HEADER_SIZE:])


def build_confluent_frame(schema_id: int, payload: bytes = b"") -> bytes:
    if not isinstance(schema_id, int) or isinstance(schema_id, bool):
        raise TypeError("schema_id must be an integer")
    if not 0 < schema_id <= 0xFFFFFFFF:
        raise ValueError("schema_id must be in [1, 4294967295]")
    return bytes((CONFLUENT_MAGIC_BYTE,)) + struct.pack(">I", schema_id) + payload


def inspect_confluent_frame(data: bytes | None) -> FrameInspection:
    """Return Bronze-friendly metadata without dropping malformed records."""

    if data is None:
        return FrameInspection(
            is_tombstone=True,
            framing_valid=True,
            schema_id=None,
            payload=None,
            error_code=None,
            error_message=None,
        )
    try:
        frame = parse_confluent_frame(data)
    except ConfluentFramingError as exc:
        return FrameInspection(
            is_tombstone=False,
            framing_valid=False,
            schema_id=None,
            payload=None,
            error_code=exc.code,
            error_message=str(exc),
        )
    return FrameInspection(
        is_tombstone=False,
        framing_valid=True,
        schema_id=frame.schema_id,
        payload=frame.payload,
        error_code=None,
        error_message=None,
    )


def assert_record_schema(schema: Any, *, label: str = "schema") -> Mapping[str, Any]:
    if not isinstance(schema, Mapping) or schema.get("type") != "record":
        raise AvroContractError(f"{label} must be an Avro record")
    if not isinstance(schema.get("name"), str) or not isinstance(
        schema.get("fields"), list
    ):
        raise AvroContractError(f"{label} record must define name and fields")
    fields = schema["fields"]
    names = [field.get("name") for field in fields if isinstance(field, Mapping)]
    if len(names) != len(fields) or len(names) != len(set(names)):
        raise AvroContractError(f"{label} fields must have unique string names")
    return schema
