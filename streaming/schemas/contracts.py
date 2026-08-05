"""Load and validate the fixed set of eight versioned entity contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .avro import canonical_schema_json
from .compatibility import validate_contract_evolution
from .writer_schemas import (
    WRITER_SCHEMAS_ROOT,
    WriterSchemaContractError,
    WriterSchemaRepository,
    WriterSchemasPending,
    load_writer_schema_repository,
)

CONTRACTS_ROOT = Path(__file__).with_name("contracts")
ENTITY_NAMES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)
_VERSION_FILE = re.compile(r"^v([1-9][0-9]*)\.json$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class EntityContractError(ValueError):
    """Checked-in entity contract is missing, stale, or internally invalid."""


class UnknownSchemaFingerprint(EntityContractError):
    """Schema is not approved by an entity version; stop only that query."""


@dataclass(frozen=True)
class VersionedEntityContract:
    entity: str
    version: int
    path: Path
    document: Mapping[str, Any]

    def allowed_fingerprints(self, kind: Literal["key", "value"]) -> frozenset[str]:
        avro = self.document["avro"]
        values = avro[f"allowed_{kind}_fingerprints"]
        return frozenset(item["sha256"] for item in values)

    def assert_fingerprint_allowed(
        self, kind: Literal["key", "value"], fingerprint_sha256: str
    ) -> None:
        avro = self.document["avro"]
        if avro.get("writer_schema_capture_state") != "captured":
            raise WriterSchemasPending(
                f"{self.entity} v{self.version} writer schema provenance is pending; "
                "runtime writer-schema capture is required"
            )
        if not self.allowed_fingerprints(kind):
            raise EntityContractError(
                f"{self.entity} v{self.version} captured state has an empty {kind} allowlist"
            )
        if fingerprint_sha256 not in self.allowed_fingerprints(kind):
            raise UnknownSchemaFingerprint(
                f"{self.entity} v{self.version} has unknown {kind} Avro "
                f"fingerprint {fingerprint_sha256}; stop affected Silver query"
            )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EntityContractError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EntityContractError(f"{path} must contain a JSON object")
    return value


def _expected_avro_type(column: Mapping[str, Any]) -> Any:
    spark_type = column.get("spark_type")
    if spark_type == "string":
        base: Any = "string"
    elif spark_type == "int":
        base = "int"
    elif spark_type == "decimal(18,2)":
        base = {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": 18,
            "scale": 2,
        }
    elif spark_type == "timestamp":
        base = {"type": "long", "logicalType": "timestamp-micros"}
    else:
        return None
    return ["null", base] if column.get("nullable") is True else base


def _record_fields(schema: Any) -> list[Mapping[str, Any]] | None:
    if not isinstance(schema, Mapping) or schema.get("type") != "record":
        return None
    fields = schema.get("fields")
    if not isinstance(fields, list) or not all(
        isinstance(field, Mapping) for field in fields
    ):
        return None
    return fields


def _value_row_fields(value_schema: Any) -> list[Mapping[str, Any]] | None:
    envelope_fields = _record_fields(value_schema)
    if envelope_fields is None:
        return None
    before = next(
        (field for field in envelope_fields if field.get("name") == "before"), None
    )
    if not isinstance(before, Mapping) or not isinstance(before.get("type"), list):
        return None
    row_schema = next(
        (
            branch
            for branch in before["type"]
            if isinstance(branch, Mapping) and branch.get("type") == "record"
        ),
        None,
    )
    return _record_fields(row_schema)


def _validate_avro_fields(
    label: str,
    fields: list[Mapping[str, Any]] | None,
    columns: list[Mapping[str, Any]],
) -> list[str]:
    if fields is None:
        return [f"{label}: Avro fields are not a concrete record"]
    expected_names = [column.get("name") for column in columns]
    actual_names = [field.get("name") for field in fields]
    errors: list[str] = []
    if actual_names != expected_names:
        errors.append(f"{label}: Avro field order/set differs from MySQL columns")
        return errors
    for field, column in zip(fields, columns, strict=True):
        expected_type = _expected_avro_type(column)
        if expected_type is None:
            errors.append(
                f"{label}.{field.get('name')}: unsupported Spark/MySQL type mapping"
            )
            continue
        if canonical_schema_json(field.get("type")) != canonical_schema_json(
            expected_type
        ):
            errors.append(
                f"{label}.{field.get('name')}: Avro type/nullability differs from MySQL"
            )
        if column.get("nullable") is True:
            if "default" not in field or field.get("default") is not None:
                errors.append(
                    f"{label}.{field.get('name')}: nullable Avro field needs default null"
                )
        elif "default" in field:
            errors.append(
                f"{label}.{field.get('name')}: non-null MySQL field has Avro default"
            )
    return errors


def _validate_contract(
    entity: str,
    version: int,
    path: Path,
    contract: Mapping[str, Any],
    writer_repository: WriterSchemaRepository,
) -> list[str]:
    errors: list[str] = []
    label = f"{entity} v{version}"
    if contract.get("entity") != entity:
        errors.append(f"{label}: entity does not match its directory")
    if contract.get("contract_version") != version:
        errors.append(f"{label}: contract_version does not match filename")
    if contract.get("topic") != f"olist_cdc.olist_oltp.{entity}":
        errors.append(f"{label}: topic is not the fixed MySQL CDC topic")
    primary_key = contract.get("primary_key")
    if (
        not isinstance(primary_key, list)
        or not primary_key
        or not all(isinstance(item, str) for item in primary_key)
    ):
        errors.append(f"{label}: primary_key must be a non-empty string array")
    columns = contract.get("mysql_columns")
    if not isinstance(columns, list) or not columns:
        errors.append(f"{label}: mysql_columns must be a non-empty array")
        columns = []
    typed_columns = [item for item in columns if isinstance(item, Mapping)]
    column_names = [item.get("name") for item in columns if isinstance(item, Mapping)]
    if len(column_names) != len(columns) or len(column_names) != len(set(column_names)):
        errors.append(f"{label}: MySQL column names must be unique strings")
    if isinstance(primary_key, list):
        keyed_columns = sorted(
            (
                item
                for item in columns
                if isinstance(item, Mapping) and "primary_key_ordinal" in item
            ),
            key=lambda item: item["primary_key_ordinal"],
        )
        if [item["name"] for item in keyed_columns] != primary_key:
            errors.append(f"{label}: primary_key and column ordinals disagree")
        if any(
            column.get("nullable") is not False
            for column in keyed_columns
            if isinstance(column, Mapping)
        ):
            errors.append(f"{label}: primary-key columns must be non-nullable")

    avro = contract.get("avro")
    if not isinstance(avro, Mapping):
        errors.append(f"{label}: avro section must be an object")
        return errors
    if avro.get("wire_format") != "confluent" or avro.get("magic_byte") != 0:
        errors.append(f"{label}: Avro wire framing must be Confluent magic-byte 0")
    if avro.get("reader_schema_role") != "contractual_reader_not_writer_provenance":
        errors.append(f"{label}: reader schema role must not claim writer provenance")
    capture_state = avro.get("writer_schema_capture_state")
    for kind in ("key", "value"):
        schema = avro.get(f"{kind}_reader_schema")
        fingerprints = avro.get(f"allowed_{kind}_fingerprints")
        if not isinstance(schema, Mapping):
            errors.append(f"{label}: missing {kind} reader schema")
            continue
        if not isinstance(fingerprints, list):
            errors.append(f"{label}: {kind} fingerprints must be an array")
            continue
        seen: set[str] = set()
        for fingerprint in fingerprints:
            if not isinstance(fingerprint, Mapping):
                errors.append(f"{label}: {kind} fingerprint entry must be an object")
                continue
            digest = fingerprint.get("sha256")
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                errors.append(f"{label}: invalid {kind} SHA-256 fingerprint")
                continue
            if digest in seen:
                errors.append(f"{label}: duplicate {kind} fingerprint {digest}")
            seen.add(digest)
            if fingerprint.get("status") != "captured_writer_schema":
                errors.append(
                    f"{label}: {kind} allowlist contains a non-captured digest"
                )
                continue
            captured = writer_repository.record_for_digest(
                entity,
                kind,
                digest,  # type: ignore[arg-type]
            )
            if captured is None:
                errors.append(
                    f"{label}: {kind} allowed digest has no checked-in captured source"
                )
                continue
            if dict(fingerprint) != captured.contract_entry():
                errors.append(
                    f"{label}: {kind} allowed digest provenance/source is stale"
                )
        if not fingerprints and capture_state != "pending_runtime_capture":
            errors.append(f"{label}: empty {kind} allowlist must be capture-pending")
    if capture_state == "captured" and any(
        not avro.get(f"allowed_{kind}_fingerprints") for kind in ("key", "value")
    ):
        errors.append(f"{label}: captured state requires key and value fingerprints")
    if capture_state == "captured" and not writer_repository.capture_complete:
        errors.append(
            f"{label}: captured state requires the complete 8x2 writer repository"
        )
    if capture_state == "pending_runtime_capture" and any(
        avro.get(f"allowed_{kind}_fingerprints") for kind in ("key", "value")
    ):
        errors.append(f"{label}: pending state cannot activate writer fingerprints")
    if capture_state not in {"captured", "pending_runtime_capture"}:
        errors.append(f"{label}: invalid writer_schema_capture_state")

    primary_key_columns = (
        [
            next((column for column in typed_columns if column.get("name") == name), {})
            for name in primary_key
        ]
        if isinstance(primary_key, list)
        else []
    )
    errors.extend(
        _validate_avro_fields(
            f"{label}.key",
            _record_fields(avro.get("key_reader_schema")),
            primary_key_columns,
        )
    )
    errors.extend(
        _validate_avro_fields(
            f"{label}.value",
            _value_row_fields(avro.get("value_reader_schema")),
            typed_columns,
        )
    )

    spark = contract.get("spark_reader_schema")
    if not isinstance(spark, Mapping) or spark.get("strip_confluent_prefix_bytes") != 5:
        errors.append(f"{label}: Spark reader must strip exactly five framing bytes")
    projection = contract.get("iceberg_projection")
    if not isinstance(projection, Mapping):
        errors.append(f"{label}: missing Iceberg projection")
    else:
        projected = projection.get("business_columns")
        projected_names = (
            [item.get("name") for item in projected if isinstance(item, Mapping)]
            if isinstance(projected, list)
            else []
        )
        if projected_names != column_names:
            errors.append(f"{label}: Iceberg business projection differs from MySQL")
        elif isinstance(projected, list):
            for projected_column, mysql_column in zip(
                projected, typed_columns, strict=True
            ):
                if not isinstance(projected_column, Mapping):
                    continue
                if projected_column.get("type") != mysql_column.get("iceberg_type"):
                    errors.append(
                        f"{label}: Iceberg type differs for {mysql_column.get('name')}"
                    )
                if projected_column.get("nullable") != mysql_column.get("nullable"):
                    errors.append(
                        f"{label}: Iceberg nullability differs for {mysql_column.get('name')}"
                    )
    evolution = contract.get("evolution")
    if not isinstance(evolution, Mapping):
        errors.append(f"{label}: missing evolution policy")
    else:
        if evolution.get("registry_compatibility") != "BACKWARD_TRANSITIVE":
            errors.append(f"{label}: compatibility must be BACKWARD_TRANSITIVE")
        if evolution.get("allowed") != ["add_nullable_field_with_default_null"]:
            errors.append(f"{label}: only nullable/default-null additions are allowed")
    return errors


def validate_contract_repository(
    root: Path = CONTRACTS_ROOT,
    *,
    writer_root: Path = WRITER_SCHEMAS_ROOT,
) -> list[str]:
    errors: list[str] = []
    try:
        writer_repository = load_writer_schema_repository(writer_root)
    except WriterSchemaContractError as exc:
        return [str(exc)]
    manifest_path = root / "manifest.json"
    try:
        manifest = _load_json(manifest_path)
    except EntityContractError as exc:
        return [str(exc)]
    entries = manifest.get("entities")
    if manifest.get("entity_count") != 8 or not isinstance(entries, list):
        return ["contract manifest must declare exactly eight entities"]
    manifest_entities = [
        entry.get("entity") for entry in entries if isinstance(entry, Mapping)
    ]
    if tuple(manifest_entities) != ENTITY_NAMES:
        errors.append("contract manifest entity order/set is not the fixed eight")

    actual_entity_directories = (
        {path.name for path in root.iterdir() if path.is_dir()}
        if root.exists()
        else set()
    )
    if actual_entity_directories != set(ENTITY_NAMES):
        errors.append(
            "contract directories must be exactly: " + ", ".join(ENTITY_NAMES)
        )

    for entry in entries:
        if not isinstance(entry, Mapping):
            errors.append("contract manifest entries must be objects")
            continue
        entity = entry.get("entity")
        relative_path = entry.get("path")
        version = entry.get("contract_version")
        if (
            not isinstance(entity, str)
            or not isinstance(relative_path, str)
            or not isinstance(version, int)
        ):
            errors.append("contract manifest entry has invalid identity")
            continue
        path = root / relative_path
        match = _VERSION_FILE.match(path.name)
        if (
            path.parent.name != entity
            or match is None
            or int(match.group(1)) != version
        ):
            errors.append(f"{entity}: manifest path/version is invalid")
            continue
        try:
            contract = _load_json(path)
        except EntityContractError as exc:
            errors.append(str(exc))
            continue
        digest = hashlib.sha256(
            canonical_schema_json(contract).encode("utf-8")
        ).hexdigest()
        if entry.get("contract_sha256") != digest:
            errors.append(f"{entity} v{version}: manifest contract SHA-256 is stale")
        errors.extend(
            _validate_contract(entity, version, path, contract, writer_repository)
        )

        raw_versions = entry.get("versions")
        if not isinstance(raw_versions, list):
            errors.append(f"{entity}: manifest versions must be an array")
            raw_versions = []

        version_paths = sorted(
            (int(version_match.group(1)), candidate)
            for candidate in path.parent.glob("v*.json")
            if (version_match := _VERSION_FILE.match(candidate.name))
        )
        unexpected_json = sorted(
            candidate.name
            for candidate in path.parent.glob("*.json")
            if _VERSION_FILE.match(candidate.name) is None
        )
        if unexpected_json:
            errors.append(
                f"{entity}: unexpected contract JSON files: "
                + ", ".join(unexpected_json)
            )
        versions = [item[0] for item in version_paths]
        if versions != list(range(1, max(versions, default=0) + 1)):
            errors.append(f"{entity}: contract versions must be contiguous from v1")
            continue
        if versions and version != versions[-1]:
            errors.append(
                f"{entity}: manifest must point to the latest contract version"
            )
        version_documents: list[tuple[int, Mapping[str, Any]]] = []
        for candidate_version, candidate_path in version_paths:
            try:
                candidate_contract = _load_json(candidate_path)
            except EntityContractError as exc:
                errors.append(str(exc))
                continue
            if candidate_path != path:
                errors.extend(
                    _validate_contract(
                        entity,
                        candidate_version,
                        candidate_path,
                        candidate_contract,
                        writer_repository,
                    )
                )
            version_documents.append((candidate_version, candidate_contract))
        declared_versions = [
            item.get("contract_version")
            for item in raw_versions
            if isinstance(item, Mapping)
        ]
        if declared_versions != versions:
            errors.append(f"{entity}: manifest version history is incomplete")
        for item in raw_versions:
            if not isinstance(item, Mapping):
                continue
            item_version = item.get("contract_version")
            candidate = next(
                (
                    document
                    for number, document in version_documents
                    if number == item_version
                ),
                None,
            )
            if candidate is None:
                continue
            expected_digest = hashlib.sha256(
                canonical_schema_json(candidate).encode("utf-8")
            ).hexdigest()
            expected_path = f"{entity}/v{item_version}.json"
            if item.get("path") != expected_path:
                errors.append(
                    f"{entity} v{item_version}: manifest history path is stale"
                )
            if item.get("contract_sha256") != expected_digest:
                errors.append(
                    f"{entity} v{item_version}: manifest history SHA-256 is stale"
                )
        for reader_index in range(1, len(version_documents)):
            reader_version, reader_contract = version_documents[reader_index]
            for writer_version, writer_contract in version_documents[:reader_index]:
                for issue in validate_contract_evolution(
                    writer_contract, reader_contract
                ):
                    errors.append(
                        f"{entity} v{reader_version} is not backward-compatible "
                        f"with v{writer_version}: {issue}"
                    )
    return errors


def load_contracts(
    root: Path = CONTRACTS_ROOT,
    *,
    writer_root: Path = WRITER_SCHEMAS_ROOT,
    require_captured_writers: bool = False,
) -> dict[str, VersionedEntityContract]:
    errors = validate_contract_repository(root, writer_root=writer_root)
    if errors:
        raise EntityContractError("; ".join(errors))
    if require_captured_writers:
        load_writer_schema_repository(writer_root, require_captured=True)
    manifest = _load_json(root / "manifest.json")
    result: dict[str, VersionedEntityContract] = {}
    for entry in manifest["entities"]:
        path = root / entry["path"]
        document = _load_json(path)
        result[entry["entity"]] = VersionedEntityContract(
            entity=entry["entity"],
            version=entry["contract_version"],
            path=path,
            document=document,
        )
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate eight versioned MySQL CDC entity contracts"
    )
    parser.add_argument("--root", type=Path, default=CONTRACTS_ROOT)
    parser.add_argument("--writer-root", type=Path, default=WRITER_SCHEMAS_ROOT)
    parser.add_argument("--require-captured-writers", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    errors = validate_contract_repository(args.root, writer_root=args.writer_root)
    if not errors and args.require_captured_writers:
        try:
            load_writer_schema_repository(args.writer_root, require_captured=True)
        except WriterSchemaContractError as exc:
            errors.append(str(exc))
    if errors:
        print("CDC entity contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    writer_repository = load_writer_schema_repository(args.writer_root)
    capture = (
        "captured" if writer_repository.capture_complete else "pending_runtime_capture"
    )
    print(f"CDC entity contracts are valid: eight entities, writers={capture}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
