"""Decode Confluent-framed Avro records through Apicurio's ccompat API."""

from __future__ import annotations

import json
import struct
import urllib.parse
import urllib.request
from io import BytesIO
from typing import Any

from fastavro import parse_schema, schemaless_reader


class ApicurioAvroDecoder:
    def __init__(self, registry_url: str) -> None:
        self.base_url = registry_url.rstrip("/") + "/apis/ccompat/v7"
        self.named_schemas: dict[str, Any] = {}
        self.schemas_by_id: dict[int, Any] = {}
        self.schemas_by_subject_version: dict[tuple[str, int], Any] = {}

    def _get_json(self, path: str) -> dict[str, Any]:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=10) as response:
            value = json.loads(response.read())
        if not isinstance(value, dict):
            raise ValueError(f"Registry response is not an object: {path}")
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
            raise ValueError("Payload is not Confluent-framed Avro")
        schema_id = struct.unpack(">I", payload[1:5])[0]
        if schema_id <= 0:
            raise ValueError(f"Invalid numeric schema id: {schema_id}")
        value = schemaless_reader(BytesIO(payload[5:]), self._schema_by_id(schema_id))
        return schema_id, value
