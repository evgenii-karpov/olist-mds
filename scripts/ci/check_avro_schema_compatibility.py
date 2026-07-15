"""Conservative BACKWARD_TRANSITIVE compatibility check for committed Avro schemas."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_DIR = PROJECT_ROOT / "streaming" / "schemas"
VERSION_PATTERN = re.compile(r"^v([1-9][0-9]*)\.avsc$")
NUMERIC_PROMOTIONS = {
    "int": {"long", "float", "double"},
    "long": {"float", "double"},
    "float": {"double"},
}


def load_schema(path: Path) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(schema, dict) or schema.get("type") != "record":
        raise ValueError(f"{path} must contain one top-level Avro record")
    if not isinstance(schema.get("name"), str) or not isinstance(
        schema.get("fields"), list
    ):
        raise ValueError(f"{path} record must define name and fields")
    names = [field.get("name") for field in schema["fields"] if isinstance(field, dict)]
    if len(names) != len(schema["fields"]) or len(names) != len(set(names)):
        raise ValueError(f"{path} fields must be objects with unique names")
    return schema


def canonical_type(avro_type: Any) -> Any:
    if isinstance(avro_type, dict):
        # Treat nested definitions as an atomic contract. This is stricter than
        # Avro resolution, but it prevents the Phase 0 stub from overlooking a
        # nested record, enum, fixed, array, map, or logical-type change.
        return json.dumps(avro_type, sort_keys=True, separators=(",", ":"))
    if isinstance(avro_type, list):
        return tuple(canonical_type(branch) for branch in avro_type)
    return avro_type


def type_is_backward_compatible(reader_type: Any, writer_type: Any) -> bool:
    reader = canonical_type(reader_type)
    writer = canonical_type(writer_type)
    if reader == writer:
        return True
    if isinstance(reader, str) and isinstance(writer, str):
        return reader in NUMERIC_PROMOTIONS.get(writer, set())
    return False


def compare_reader_to_writer(
    reader: dict[str, Any], writer: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    reader_name = (reader.get("namespace"), reader["name"])
    writer_name = (writer.get("namespace"), writer["name"])
    if reader_name != writer_name:
        errors.append(f"record identity changed from {writer_name} to {reader_name}")

    reader_fields = {field["name"]: field for field in reader["fields"]}
    writer_fields = {field["name"]: field for field in writer["fields"]}

    for name, writer_field in writer_fields.items():
        reader_field = reader_fields.get(name)
        if reader_field is None:
            errors.append(f"field {name!r} was removed or renamed")
        elif not type_is_backward_compatible(
            reader_field.get("type"), writer_field.get("type")
        ):
            errors.append(
                f"field {name!r} changed incompatibly from "
                f"{writer_field.get('type')!r} to {reader_field.get('type')!r}"
            )

    for name, reader_field in reader_fields.items():
        if name not in writer_fields and "default" not in reader_field:
            errors.append(f"new field {name!r} has no default")
    return errors


def discover_subjects(schema_dir: Path) -> dict[str, list[tuple[int, Path]]]:
    subjects: dict[str, list[tuple[int, Path]]] = {}
    for path in sorted(schema_dir.rglob("*.avsc")):
        match = VERSION_PATTERN.match(path.name)
        if path.parent == schema_dir or match is None:
            raise ValueError(
                f"schema path must match <subject>/v<positive-integer>.avsc: {path}"
            )
        subject = path.parent.relative_to(schema_dir).as_posix()
        subjects.setdefault(subject, []).append((int(match.group(1)), path))
    return subjects


def check_schema_directory(schema_dir: Path) -> list[str]:
    errors: list[str] = []
    subjects = discover_subjects(schema_dir)
    for subject, versioned_paths in subjects.items():
        versioned_paths.sort()
        versions = [version for version, _ in versioned_paths]
        expected = list(range(1, len(versions) + 1))
        if versions != expected:
            errors.append(
                f"subject {subject!r} versions must be contiguous from v1: {versions}"
            )
            continue
        schemas = [(version, load_schema(path)) for version, path in versioned_paths]
        for reader_index in range(1, len(schemas)):
            reader_version, reader_schema = schemas[reader_index]
            for writer_version, writer_schema in schemas[:reader_index]:
                for error in compare_reader_to_writer(reader_schema, writer_schema):
                    errors.append(
                        f"{subject} v{reader_version} cannot read v{writer_version}: {error}"
                    )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = check_schema_directory(args.schema_dir)
    except ValueError as exc:
        print(f"Avro schema compatibility check failed: {exc}")
        return 1
    if errors:
        print("Avro schema compatibility check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Avro schemas satisfy the conservative BACKWARD_TRANSITIVE policy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
