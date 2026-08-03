"""Resolve Apicurio/Confluent Avro schemas and recursive references."""

from __future__ import annotations

import copy
import json
import re
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .avro import AvroContractError, parse_schema_json, schema_fingerprint_sha256


class RegistryUnavailable(RuntimeError):
    """Transient registry access failure; callers must not advance checkpoints."""


class RegistryContractViolation(AvroContractError):
    """Permanent schema/reference violation for one affected entity query."""


@dataclass(frozen=True)
class SchemaReference:
    name: str
    subject: str
    version: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> SchemaReference:
        name = value.get("name")
        subject = value.get("subject", value.get("artifactId"))
        version = value.get("version")
        if not isinstance(name, str) or not isinstance(subject, str):
            raise RegistryContractViolation(
                "schema reference must define string name and subject/artifactId"
            )
        if not isinstance(version, (str, int)) or isinstance(version, bool):
            raise RegistryContractViolation(
                f"schema reference {name!r} has invalid version {version!r}"
            )
        return cls(name=name, subject=subject, version=str(version))


@dataclass(frozen=True)
class RegistrySchemaDocument:
    schema: Any
    references: tuple[SchemaReference, ...]
    subject: str | None = None
    version: str | None = None


@dataclass(frozen=True)
class ResolvedAvroSchema:
    schema_id: int
    schema: Any
    references: tuple[SchemaReference, ...]
    self_contained_schema: Any
    fingerprint_sha256: str

    def archive_row(
        self,
        *,
        subject: str,
        registry_version: str,
        first_seen_at: str,
        last_verified_at: str,
    ) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "fingerprint_sha256": self.fingerprint_sha256,
            "subject": subject,
            "registry_version": registry_version,
            "schema_json": json.dumps(
                self.schema, ensure_ascii=False, separators=(",", ":")
            ),
            "references_json": json.dumps(
                [reference.__dict__ for reference in self.references],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "spark_self_contained_schema_json": json.dumps(
                self.self_contained_schema,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "first_seen_at": first_seen_at,
            "last_verified_at": last_verified_at,
        }


class SchemaRegistryReader(Protocol):
    def schema_by_id(self, schema_id: int) -> RegistrySchemaDocument: ...

    def schema_by_subject_version(
        self, subject: str, version: str
    ) -> RegistrySchemaDocument: ...


class ApicurioCCompatClient:
    """Read schemas through Apicurio's Confluent compatibility API v7."""

    REGISTRY_GROUP = "olist_cdc"

    def __init__(
        self,
        base_url: str = "http://apicurio-registry:8080/apis/ccompat/v7",
        timeout_seconds: float = 15.0,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("registry URL must start with http:// or https://")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _get(self, path: str) -> Mapping[str, Any]:
        request = Request(
            f"{self.base_url}/{path.lstrip('/')}",
            headers={"Accept": "application/json"},
            method="GET",
        )
        deadline = time.monotonic() + max(self.timeout_seconds, 30.0)
        while True:
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    break
            except HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if 400 <= exc.code < 500 and exc.code not in {408, 425, 429}:
                    raise RegistryContractViolation(
                        f"registry GET {path} returned HTTP {exc.code}: {body[:500]}"
                    ) from None
                raise RegistryUnavailable(
                    f"registry GET {path} returned HTTP {exc.code}"
                ) from None
            except (URLError, TimeoutError, Exception) as exc:
                if time.monotonic() < deadline:
                    time.sleep(1.0)
                    continue
                raise RegistryUnavailable(
                    f"registry GET {path} failed: {exc}"
                ) from None
        try:
            value = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RegistryContractViolation(
                f"registry GET {path} returned invalid JSON: {exc}"
            ) from exc
        if not isinstance(value, Mapping):
            raise RegistryContractViolation(
                f"registry GET {path} must return a JSON object"
            )
        return value

    @staticmethod
    def _document(value: Mapping[str, Any]) -> RegistrySchemaDocument:
        raw_schema = value.get("schema")
        if isinstance(raw_schema, str):
            schema = parse_schema_json(raw_schema)
        elif isinstance(raw_schema, (Mapping, list)):
            schema = copy.deepcopy(raw_schema)
        else:
            raise RegistryContractViolation("registry response has no Avro schema")
        raw_references = value.get("references", [])
        if not isinstance(raw_references, list):
            raise RegistryContractViolation("registry references must be an array")
        references = tuple(
            SchemaReference.from_mapping(reference)
            for reference in raw_references
            if isinstance(reference, Mapping)
        )
        if len(references) != len(raw_references):
            raise RegistryContractViolation("registry references must be objects")
        raw_subject = value.get("subject")
        raw_version = value.get("version")
        return RegistrySchemaDocument(
            schema=schema,
            references=references,
            subject=raw_subject if isinstance(raw_subject, str) else None,
            version=str(raw_version) if raw_version is not None else None,
        )

    def schema_by_id(self, schema_id: int) -> RegistrySchemaDocument:
        if (
            not isinstance(schema_id, int)
            or isinstance(schema_id, bool)
            or schema_id <= 0
        ):
            raise ValueError("schema_id must be a positive integer")
        return self._document(self._get(f"schemas/ids/{schema_id}"))

    def schema_by_subject_version(
        self, subject: str, version: str
    ) -> RegistrySchemaDocument:
        encoded_subject = quote(subject, safe="")
        encoded_version = quote(str(version), safe="")
        try:
            return self._document(
                self._get(f"subjects/{encoded_subject}/versions/{encoded_version}")
            )
        except RegistryContractViolation as exc:
            # Apicurio's v7 compatibility endpoint exposes the root schema
            # under a Confluent subject, while the 3.x SQL registry stores
            # referenced artifacts with TopicIdStrategy ids (for example,
            # `topic.Value` becomes `topic-value`).  Resolve that narrow
            # compatibility gap through the native v2 artifact endpoint.
            if "returned HTTP 404" not in str(exc):
                raise
            registry_base = self.base_url.replace(
                "/apis/ccompat/v7", "/apis/registry/v2"
            )
            # References in Apicurio's native v2 API keep their exact
            # artifact ID (for example ``topic.Value``).  The compatibility
            # API's root subject uses TopicIdStrategy (``topic-value``), so
            # trying the mapped ID first can silently return the root
            # Envelope instead of the referenced Value record.
            artifact_ids = (subject, self._artifact_id_for_subject(subject))
            last_error: Exception | None = None
            for artifact_id in dict.fromkeys(artifact_ids):
                request = Request(
                    f"{registry_base}/groups/{quote(self.REGISTRY_GROUP, safe='')}"
                    f"/artifacts/{quote(artifact_id, safe='')}"
                    f"/versions/{encoded_version}",
                    headers={"Accept": "application/json"},
                    method="GET",
                )
                try:
                    with urlopen(request, timeout=self.timeout_seconds) as response:
                        raw = response.read().decode("utf-8")
                    schema = json.loads(raw)
                    if not isinstance(schema, Mapping):
                        raise RegistryContractViolation(
                            f"registry artifact {artifact_id!r} is not an Avro object"
                        )
                    return self._document(
                        {
                            "schema": schema,
                            "references": [],
                            "subject": subject,
                            "version": str(version),
                        }
                    )
                except (
                    HTTPError,
                    URLError,
                    TimeoutError,
                    json.JSONDecodeError,
                ) as error:
                    last_error = error
                    continue
            if last_error is not None:
                raise exc from last_error
            raise exc

    @staticmethod
    def _artifact_id_for_subject(subject: str) -> str:
        for suffix, replacement in ((".Key", "-key"), (".Value", "-value")):
            if subject.endswith(suffix):
                return subject[: -len(suffix)] + replacement
        return subject


def _reference_aliases(reference: SchemaReference) -> tuple[str, ...]:
    short_name = reference.name.rsplit(".", maxsplit=1)[-1]
    if short_name == reference.name:
        return (reference.name,)
    return (reference.name, short_name)


def inline_named_references(schema: Any, definitions: Mapping[str, Any]) -> Any:
    """Inline each external named schema once, preserving later named uses."""

    used: set[str] = set()

    def definition_identity(name: str, definition: Any) -> str:
        if not isinstance(definition, Mapping):
            return name
        declared_name = definition.get("name")
        if not isinstance(declared_name, str):
            return name
        if "." in declared_name:
            return declared_name
        namespace = definition.get("namespace")
        return (
            f"{namespace}.{declared_name}"
            if isinstance(namespace, str) and namespace
            else declared_name
        )

    def resolve_name(name: str) -> Any:
        if name not in definitions:
            return name
        definition = definitions[name]
        canonical_name = definition_identity(name, definition)
        if canonical_name in used:
            return name
        used.add(canonical_name)
        return walk_schema(copy.deepcopy(definition))

    def walk_type(avro_type: Any) -> Any:
        if isinstance(avro_type, str):
            return resolve_name(avro_type)
        if isinstance(avro_type, list):
            return [walk_type(branch) for branch in avro_type]
        if isinstance(avro_type, Mapping):
            return walk_schema(dict(avro_type))
        return avro_type

    def walk_schema(value: Any) -> Any:
        if isinstance(value, list):
            return [walk_schema(item) for item in value]
        if not isinstance(value, Mapping):
            return value
        result = dict(value)
        if "type" in result:
            result["type"] = walk_type(result["type"])
        if isinstance(result.get("fields"), list):
            fields: list[Any] = []
            for raw_field in result["fields"]:
                if not isinstance(raw_field, Mapping):
                    fields.append(raw_field)
                    continue
                field = dict(raw_field)
                field["type"] = walk_type(field.get("type"))
                fields.append(field)
            result["fields"] = fields
        if "items" in result:
            result["items"] = walk_type(result["items"])
        if "values" in result:
            result["values"] = walk_type(result["values"])
        return result

    return walk_schema(copy.deepcopy(schema))


class RecursiveSchemaResolver:
    def __init__(self, reader: SchemaRegistryReader) -> None:
        self.reader = reader

    def resolve(self, schema_id: int) -> ResolvedAvroSchema:
        root = self.reader.schema_by_id(schema_id)
        definitions: dict[str, Any] = {}
        all_references: list[SchemaReference] = []
        loaded: dict[tuple[str, str], Any] = {}

        def load_reference(
            reference: SchemaReference, stack: tuple[tuple[str, str], ...]
        ) -> Any:
            key = (reference.subject, reference.version)
            if key in stack:
                chain = " -> ".join(
                    f"{subject}@{version}" for subject, version in (*stack, key)
                )
                raise RegistryContractViolation(
                    f"cyclic external Avro reference detected: {chain}"
                )
            if key in loaded:
                return loaded[key]
            document = self.reader.schema_by_subject_version(*key)
            nested_definitions: dict[str, Any] = {}
            for nested in document.references:
                nested_schema = load_reference(nested, (*stack, key))
                for alias in _reference_aliases(nested):
                    nested_definitions[alias] = nested_schema
                all_references.append(nested)
            resolved = inline_named_references(document.schema, nested_definitions)
            loaded[key] = resolved
            return resolved

        for reference in root.references:
            resolved_reference = load_reference(reference, ())
            for alias in _reference_aliases(reference):
                previous = definitions.get(alias)
                if previous is not None and previous != resolved_reference:
                    raise RegistryContractViolation(
                        f"reference alias {alias!r} resolves to multiple schemas"
                    )
                definitions[alias] = resolved_reference
            all_references.append(reference)

        self_contained = inline_named_references(root.schema, definitions)
        unique_references = tuple(dict.fromkeys(all_references))
        return ResolvedAvroSchema(
            schema_id=schema_id,
            schema=root.schema,
            references=unique_references,
            self_contained_schema=self_contained,
            fingerprint_sha256=schema_fingerprint_sha256(self_contained),
        )


class SchemaIdConsistencyGuard:
    """Reject one numeric ID resolving to two fingerprints in one generation."""

    def __init__(self) -> None:
        self._fingerprints: dict[int, str] = {}

    def observe(self, schema_id: int, fingerprint_sha256: str) -> None:
        if (
            not isinstance(schema_id, int)
            or isinstance(schema_id, bool)
            or schema_id <= 0
        ):
            raise ValueError("schema_id must be a positive integer")
        if re.fullmatch(r"[0-9a-f]{64}", fingerprint_sha256) is None:
            raise ValueError("fingerprint_sha256 must be 64 lowercase hex characters")
        previous = self._fingerprints.get(schema_id)
        if previous is not None and previous != fingerprint_sha256:
            raise RegistryContractViolation(
                f"schema ID {schema_id} changed fingerprint from {previous} "
                f"to {fingerprint_sha256}"
            )
        self._fingerprints[schema_id] = fingerprint_sha256
