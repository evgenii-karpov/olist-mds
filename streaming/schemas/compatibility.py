"""Conservative nullable/additive and BACKWARD_TRANSITIVE contract checks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .avro import canonical_schema_json


@dataclass(frozen=True)
class CompatibilityIssue:
    path: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.code}: {self.message}"


def _is_nullable_with_null_default(field: Mapping[str, Any]) -> bool:
    avro_type = field.get("type")
    return (
        isinstance(avro_type, list)
        and "null" in avro_type
        and "default" in field
        and field["default"] is None
    )


def _record_identity(schema: Mapping[str, Any]) -> tuple[Any, Any]:
    return schema.get("namespace"), schema.get("name")


def _compare_type(reader: Any, writer: Any, path: str) -> list[CompatibilityIssue]:
    if isinstance(reader, Mapping) and isinstance(writer, Mapping):
        reader_type = reader.get("type")
        writer_type = writer.get("type")
        if reader_type != writer_type:
            return [
                CompatibilityIssue(
                    path,
                    "type_change",
                    f"type changed from {writer_type!r} to {reader_type!r}",
                )
            ]
        if reader_type == "record":
            return compare_reader_to_writer(reader, writer, path=path)
        if reader_type == "array":
            return _compare_type(reader.get("items"), writer.get("items"), f"{path}[]")
        if reader_type == "map":
            return _compare_type(
                reader.get("values"), writer.get("values"), f"{path}{{}}"
            )
        if canonical_schema_json(reader) != canonical_schema_json(writer):
            return [
                CompatibilityIssue(
                    path,
                    "type_change",
                    "logical/named type definition changed in-place",
                )
            ]
        return []
    if isinstance(reader, list) and isinstance(writer, list):
        if len(reader) != len(writer):
            return [
                CompatibilityIssue(
                    path,
                    "type_change",
                    "union branches changed in-place",
                )
            ]
        issues: list[CompatibilityIssue] = []
        for index, (reader_branch, writer_branch) in enumerate(
            zip(reader, writer, strict=True)
        ):
            issues.extend(
                _compare_type(reader_branch, writer_branch, f"{path}|{index}")
            )
        return issues
    if canonical_schema_json(reader) != canonical_schema_json(writer):
        return [
            CompatibilityIssue(
                path,
                "type_change",
                f"type changed from {writer!r} to {reader!r}",
            )
        ]
    return []


def compare_reader_to_writer(
    reader: Mapping[str, Any],
    writer: Mapping[str, Any],
    *,
    path: str = "$",
) -> list[CompatibilityIssue]:
    """Enforce the plan's stricter-than-Avro nullable/additive policy."""

    issues: list[CompatibilityIssue] = []
    if reader.get("type") != "record" or writer.get("type") != "record":
        return [CompatibilityIssue(path, "not_record", "both schemas must be records")]
    if _record_identity(reader) != _record_identity(writer):
        issues.append(
            CompatibilityIssue(
                path,
                "record_rename",
                f"record identity changed from {_record_identity(writer)!r} "
                f"to {_record_identity(reader)!r}",
            )
        )
    raw_reader_fields = reader.get("fields")
    raw_writer_fields = writer.get("fields")
    if not isinstance(raw_reader_fields, list) or not isinstance(
        raw_writer_fields, list
    ):
        return [
            *issues,
            CompatibilityIssue(path, "invalid_fields", "record fields must be arrays"),
        ]
    reader_fields = {
        field.get("name"): field
        for field in raw_reader_fields
        if isinstance(field, Mapping) and isinstance(field.get("name"), str)
    }
    writer_fields = {
        field.get("name"): field
        for field in raw_writer_fields
        if isinstance(field, Mapping) and isinstance(field.get("name"), str)
    }
    if len(reader_fields) != len(raw_reader_fields) or len(writer_fields) != len(
        raw_writer_fields
    ):
        issues.append(
            CompatibilityIssue(
                path, "invalid_fields", "field names must be unique strings"
            )
        )
        return issues

    for name, writer_field in writer_fields.items():
        field_path = f"{path}.{name}"
        reader_field = reader_fields.get(name)
        if reader_field is None:
            issues.append(
                CompatibilityIssue(
                    field_path,
                    "field_removed_or_renamed",
                    "existing field is missing",
                )
            )
            continue
        issues.extend(
            _compare_type(
                reader_field.get("type"), writer_field.get("type"), field_path
            )
        )

    for name, reader_field in reader_fields.items():
        if name in writer_fields:
            continue
        if not _is_nullable_with_null_default(reader_field):
            issues.append(
                CompatibilityIssue(
                    f"{path}.{name}",
                    "non_nullable_addition",
                    "new fields must be nullable unions with default null",
                )
            )
    return issues


def check_backward_transitive(
    schemas: Sequence[Mapping[str, Any]],
) -> list[CompatibilityIssue]:
    issues: list[CompatibilityIssue] = []
    for reader_index in range(1, len(schemas)):
        reader_version = reader_index + 1
        for writer_index in range(reader_index):
            writer_version = writer_index + 1
            compared = compare_reader_to_writer(
                schemas[reader_index],
                schemas[writer_index],
                path=f"v{reader_version}<->v{writer_version}",
            )
            issues.extend(compared)
    return issues


def _allowed_fingerprints(avro: Mapping[str, Any], kind: str) -> set[str]:
    values = avro.get(f"allowed_{kind}_fingerprints")
    if not isinstance(values, list):
        return set()
    result: set[str] = set()
    for entry in values:
        if not isinstance(entry, Mapping):
            continue
        digest = entry.get("sha256")
        if isinstance(digest, str):
            result.add(digest)
    return result


def validate_contract_evolution(
    old: Mapping[str, Any], new: Mapping[str, Any]
) -> list[CompatibilityIssue]:
    issues: list[CompatibilityIssue] = []
    if old.get("entity") != new.get("entity"):
        issues.append(
            CompatibilityIssue("$.entity", "entity_rename", "entity cannot be renamed")
        )
    if old.get("topic") != new.get("topic"):
        issues.append(
            CompatibilityIssue(
                "$.topic", "topic_change", "topic cannot change in-place"
            )
        )
    if old.get("primary_key") != new.get("primary_key"):
        issues.append(
            CompatibilityIssue(
                "$.primary_key",
                "primary_key_change",
                "primary key cannot change in-place",
            )
        )
    if old.get("topic_partitions") != new.get("topic_partitions"):
        evolution = new.get("evolution")
        reset_action = (
            evolution.get("key_schema_or_partition_change_action")
            if isinstance(evolution, Mapping)
            else None
        )
        if reset_action != "full_reset":
            issues.append(
                CompatibilityIssue(
                    "$.topic_partitions",
                    "partition_change_without_reset",
                    "topic partition count may change only with full_reset action",
                )
            )

    old_columns = {
        column.get("name"): column
        for column in old.get("mysql_columns", [])
        if isinstance(column, Mapping)
    }
    new_columns = {
        column.get("name"): column
        for column in new.get("mysql_columns", [])
        if isinstance(column, Mapping)
    }
    for name, old_column in old_columns.items():
        new_column = new_columns.get(name)
        if new_column is None:
            issues.append(
                CompatibilityIssue(
                    f"$.mysql_columns.{name}",
                    "column_removed_or_renamed",
                    "existing MySQL column is missing",
                )
            )
            continue
        for property_name in ("mysql_type", "spark_type", "iceberg_type", "nullable"):
            if old_column.get(property_name) != new_column.get(property_name):
                issues.append(
                    CompatibilityIssue(
                        f"$.mysql_columns.{name}.{property_name}",
                        "column_change",
                        "existing column contract changed in-place",
                    )
                )
    for name, new_column in new_columns.items():
        if name not in old_columns and new_column.get("nullable") is not True:
            issues.append(
                CompatibilityIssue(
                    f"$.mysql_columns.{name}",
                    "non_nullable_addition",
                    "new MySQL columns must be nullable",
                )
            )

    old_avro = old.get("avro")
    new_avro = new.get("avro")
    if isinstance(old_avro, Mapping) and isinstance(new_avro, Mapping):
        old_key = old_avro.get("key_reader_schema")
        new_key = new_avro.get("key_reader_schema")
        if canonical_schema_json(old_key) != canonical_schema_json(new_key):
            issues.append(
                CompatibilityIssue(
                    "$.avro.key_reader_schema",
                    "key_schema_change",
                    "Avro key schema cannot change in-place",
                )
            )
        old_value = old_avro.get("value_reader_schema")
        new_value = new_avro.get("value_reader_schema")
        if isinstance(old_value, Mapping) and isinstance(new_value, Mapping):
            issues.extend(
                compare_reader_to_writer(
                    new_value, old_value, path="$.avro.value_reader_schema"
                )
            )
        for kind in ("key", "value"):
            old_allowed = _allowed_fingerprints(old_avro, kind)
            new_allowed = _allowed_fingerprints(new_avro, kind)
            for removed in sorted(old_allowed - new_allowed):
                issues.append(
                    CompatibilityIssue(
                        f"$.avro.allowed_{kind}_fingerprints",
                        "allowed_fingerprint_removed",
                        f"captured writer fingerprint {removed} cannot be removed",
                    )
                )
    return issues
