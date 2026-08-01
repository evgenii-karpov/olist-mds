"""Checked-in provenance for Avro schemas emitted by the live connector.

Reader schemas generated from the MySQL contract are useful for decoding, but
they are not evidence of what Debezium and the configured converter actually
wrote.  This repository therefore starts in a fail-closed pending state.  J1
imports a runtime-captured bundle; only schemas with checked-in bytes, complete
registry provenance, and a recomputed canonical SHA-256 become allowlisted.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from .avro import assert_record_schema, parse_schema_json, schema_fingerprint_sha256

WRITER_SCHEMAS_ROOT = Path(__file__).with_name("captured-writer-schemas")
MANIFEST_PATH = WRITER_SCHEMAS_ROOT / "manifest.json"
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
SCHEMA_KINDS = ("key", "value")
PENDING = "pending_runtime_capture"
CAPTURED = "captured"
J1_CAPTURE_COMMAND = (
    "python -m streaming.schemas.writer_schemas capture-bundle "
    "--bundle <runtime-export-directory>"
)


class WriterSchemaContractError(ValueError):
    """Captured-writer repository is malformed or has stale evidence."""


class WriterSchemasPending(WriterSchemaContractError):
    """Runtime writer fingerprints are intentionally not approved yet."""


@dataclass(frozen=True)
class CapturedWriterSchema:
    entity: str
    kind: Literal["key", "value"]
    path: Path
    relative_path: str
    sha256: str
    provenance_ref: str
    provenance: Mapping[str, Any]
    schema: Mapping[str, Any]

    def contract_entry(self) -> dict[str, Any]:
        return {
            "sha256": self.sha256,
            "status": "captured_writer_schema",
            "source": f"captured-writer-schemas/{self.relative_path}",
            "provenance_ref": self.provenance_ref,
        }


@dataclass(frozen=True)
class WriterSchemaRepository:
    root: Path
    manifest: Mapping[str, Any]
    records: Mapping[tuple[str, str], tuple[CapturedWriterSchema, ...]]

    @property
    def capture_complete(self) -> bool:
        return all(
            self.records.get((entity, kind))
            for entity in ENTITY_NAMES
            for kind in SCHEMA_KINDS
        )

    def schemas(
        self, entity: str, kind: Literal["key", "value"]
    ) -> tuple[CapturedWriterSchema, ...]:
        return self.records.get((entity, kind), ())

    def allowed_entries(
        self, entity: str, kind: Literal["key", "value"]
    ) -> list[dict[str, Any]]:
        return [record.contract_entry() for record in self.schemas(entity, kind)]

    def require_complete(self) -> None:
        if self.capture_complete:
            return
        pending = [
            f"{entity}:{kind}"
            for entity in ENTITY_NAMES
            for kind in SCHEMA_KINDS
            if not self.records.get((entity, kind))
        ]
        raise WriterSchemasPending(
            "writer schema capture is pending for "
            + ", ".join(pending)
            + f"; J1 must run: {J1_CAPTURE_COMMAND}"
        )

    def record_for_digest(
        self, entity: str, kind: Literal["key", "value"], digest: str
    ) -> CapturedWriterSchema | None:
        return next(
            (item for item in self.schemas(entity, kind) if item.sha256 == digest),
            None,
        )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WriterSchemaContractError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WriterSchemaContractError(f"{path} must contain a JSON object")
    return value


def _safe_relative_path(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise WriterSchemaContractError(f"{label} path must be a non-empty string")
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or candidate.as_posix() != value
    ):
        raise WriterSchemaContractError(f"{label} path must be normalized and relative")
    return value


def _validate_provenance(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WriterSchemaContractError(f"{label} provenance must be an object")
    required_strings = (
        "registry_url",
        "registry_group",
        "artifact_id",
        "artifact_version",
        "captured_at_utc",
        "connector_name",
        "topic",
    )
    for field in required_strings:
        if not isinstance(value.get(field), str) or not value[field]:
            raise WriterSchemaContractError(
                f"{label} provenance.{field} must be a non-empty string"
            )
    schema_id = value.get("schema_id")
    if not isinstance(schema_id, int) or isinstance(schema_id, bool) or schema_id <= 0:
        raise WriterSchemaContractError(
            f"{label} provenance.schema_id must be a positive integer"
        )
    if not value["registry_url"].startswith(("http://", "https://")):
        raise WriterSchemaContractError(
            f"{label} provenance.registry_url must be HTTP(S)"
        )
    if value["registry_group"] != "olist_cdc":
        raise WriterSchemaContractError(
            f"{label} provenance.registry_group must be 'olist_cdc'"
        )
    captured_at = value["captured_at_utc"]
    try:
        captured_time = datetime.fromisoformat(captured_at)
    except ValueError as exc:
        raise WriterSchemaContractError(
            f"{label} provenance.captured_at_utc must be ISO-8601"
        ) from exc
    if captured_time.utcoffset() != timedelta(0):
        raise WriterSchemaContractError(
            f"{label} provenance.captured_at_utc must include a UTC offset"
        )
    return value


def load_writer_schema_repository(
    root: Path = WRITER_SCHEMAS_ROOT, *, require_captured: bool = False
) -> WriterSchemaRepository:
    manifest = _load_json(root / "manifest.json")
    if manifest.get("manifest_version") != 1:
        raise WriterSchemaContractError("writer-schema manifest_version must be 1")
    if manifest.get("j1_capture_command") != J1_CAPTURE_COMMAND:
        raise WriterSchemaContractError("writer-schema J1 capture command is stale")
    entries = manifest.get("entities")
    if not isinstance(entries, list):
        raise WriterSchemaContractError("writer-schema entities must be an array")
    entities = [entry.get("entity") for entry in entries if isinstance(entry, Mapping)]
    if tuple(entities) != ENTITY_NAMES:
        raise WriterSchemaContractError(
            "writer-schema manifest must contain the exact eight entities"
        )

    records: dict[tuple[str, str], tuple[CapturedWriterSchema, ...]] = {}
    for entity_index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise WriterSchemaContractError(
                "writer-schema entity entries must be objects"
            )
        entity = str(entry["entity"])
        for kind in SCHEMA_KINDS:
            label = f"{entity}:{kind}"
            section = entry.get(kind)
            if not isinstance(section, Mapping):
                raise WriterSchemaContractError(f"{label} section must be an object")
            state = section.get("state")
            raw_schemas = section.get("schemas")
            if not isinstance(raw_schemas, list):
                raise WriterSchemaContractError(f"{label} schemas must be an array")
            if state == PENDING:
                if raw_schemas:
                    raise WriterSchemaContractError(
                        f"{label} pending state cannot contain captured schemas"
                    )
                records[(entity, kind)] = ()
                continue
            if state != CAPTURED or not raw_schemas:
                raise WriterSchemaContractError(
                    f"{label} state must be {PENDING!r} or non-empty {CAPTURED!r}"
                )
            loaded: list[CapturedWriterSchema] = []
            seen: set[str] = set()
            for schema_index, raw_schema in enumerate(raw_schemas):
                item_label = f"{label}[{schema_index}]"
                if not isinstance(raw_schema, Mapping):
                    raise WriterSchemaContractError(f"{item_label} must be an object")
                relative_path = _safe_relative_path(
                    raw_schema.get("path"), label=item_label
                )
                expected_prefix = f"{entity}/{kind}/"
                if not relative_path.startswith(expected_prefix):
                    raise WriterSchemaContractError(
                        f"{item_label} path must start with {expected_prefix!r}"
                    )
                if not relative_path.endswith(".avsc"):
                    raise WriterSchemaContractError(
                        f"{item_label} captured writer schema must use .avsc"
                    )
                path = root / Path(relative_path)
                try:
                    parsed = parse_schema_json(path.read_bytes())
                    schema = assert_record_schema(parsed, label=item_label)
                except (OSError, ValueError) as exc:
                    raise WriterSchemaContractError(
                        f"cannot validate captured writer schema {path}: {exc}"
                    ) from exc
                digest = schema_fingerprint_sha256(schema)
                if raw_schema.get("sha256") != digest:
                    raise WriterSchemaContractError(
                        f"{item_label} captured writer schema SHA-256 is stale"
                    )
                if digest in seen:
                    raise WriterSchemaContractError(
                        f"{label} repeats captured writer fingerprint {digest}"
                    )
                seen.add(digest)
                provenance = _validate_provenance(
                    raw_schema.get("provenance"), label=item_label
                )
                expected_topic = f"olist_cdc.olist_oltp.{entity}"
                if provenance["connector_name"] != "olist-mysql-cdc":
                    raise WriterSchemaContractError(
                        f"{item_label} provenance connector_name is not fixed"
                    )
                if provenance["topic"] != expected_topic:
                    raise WriterSchemaContractError(
                        f"{item_label} provenance topic is not {expected_topic}"
                    )
                loaded.append(
                    CapturedWriterSchema(
                        entity=entity,
                        kind=kind,  # type: ignore[arg-type]
                        path=path,
                        relative_path=relative_path,
                        sha256=digest,
                        provenance_ref=(
                            "captured-writer-schemas/manifest.json#/entities/"
                            f"{entity_index}/{kind}/schemas/{schema_index}/provenance"
                        ),
                        provenance=provenance,
                        schema=schema,
                    )
                )
            records[(entity, kind)] = tuple(loaded)

    repository = WriterSchemaRepository(root=root, manifest=manifest, records=records)
    declared_state = manifest.get("capture_state")
    expected_state = CAPTURED if repository.capture_complete else PENDING
    if declared_state != expected_state:
        raise WriterSchemaContractError(
            f"writer-schema capture_state must be {expected_state!r}"
        )
    if require_captured:
        repository.require_complete()
    return repository


def validate_writer_schema_repository(
    root: Path = WRITER_SCHEMAS_ROOT, *, require_captured: bool = False
) -> list[str]:
    try:
        load_writer_schema_repository(root, require_captured=require_captured)
    except WriterSchemaContractError as exc:
        return [str(exc)]
    return []


def capture_bundle(bundle: Path, destination: Path = WRITER_SCHEMAS_ROOT) -> None:
    """Import a J1 evidence bundle without inventing registry fingerprints."""

    repository = load_writer_schema_repository(bundle, require_captured=True)
    destination.mkdir(parents=True, exist_ok=True)
    for records in repository.records.values():
        for record in records:
            target = destination / Path(record.relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(record.path, target)
    shutil.copyfile(bundle / "manifest.json", destination / "manifest.json")
    load_writer_schema_repository(destination, require_captured=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or import runtime-captured CDC writer schemas"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--root", type=Path, default=WRITER_SCHEMAS_ROOT)
    validate.add_argument("--require-captured", action="store_true")
    capture = commands.add_parser("capture-bundle")
    capture.add_argument("--bundle", type=Path, required=True)
    capture.add_argument("--root", type=Path, default=WRITER_SCHEMAS_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "capture-bundle":
        try:
            capture_bundle(args.bundle, args.root)
        except WriterSchemaContractError as exc:
            print(f"writer-schema capture failed: {exc}")
            return 1
        print(f"captured writer schemas imported into {args.root}")
        return 0
    errors = validate_writer_schema_repository(
        args.root, require_captured=args.require_captured
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    repository = load_writer_schema_repository(args.root)
    state = CAPTURED if repository.capture_complete else PENDING
    print(f"captured writer schema repository is valid: {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
