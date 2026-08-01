"""Generate the eight versioned entity contracts from one exact type catalog.

The generated JSON is committed. Run with ``--check`` in CI; ``--write`` is a
deliberate maintainer action after reviewing a new contract version.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .avro import (
    FINGERPRINT_ALGORITHM,
    canonical_schema_json,
)
from .writer_schemas import (
    WRITER_SCHEMAS_ROOT,
    WriterSchemaRepository,
    load_writer_schema_repository,
)

CONTRACTS_ROOT = Path(__file__).with_name("contracts")


@dataclass(frozen=True)
class Column:
    name: str
    mysql_type: str
    spark_type: str
    iceberg_type: str
    nullable: bool = False
    primary_key_ordinal: int | None = None
    checks: tuple[str, ...] = ()
    references: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Entity:
    name: str
    partitions: int
    columns: tuple[Column, ...]

    @property
    def primary_key(self) -> tuple[str, ...]:
        return tuple(
            column.name
            for column in sorted(
                (column for column in self.columns if column.primary_key_ordinal),
                key=lambda column: int(column.primary_key_ordinal or 0),
            )
        )


STRING = ("string", "string")
INT = ("int", "int")
DECIMAL_18_2 = ("decimal(18,2)", "decimal(18,2)")
TIMESTAMP_MICROS = ("timestamp", "timestamp")


def column(
    name: str,
    mysql_type: str,
    logical_type: tuple[str, str],
    *,
    nullable: bool = False,
    pk: int | None = None,
    checks: Sequence[str] = (),
    references: str | None = None,
    metadata: dict[str, str] | None = None,
) -> Column:
    return Column(
        name=name,
        mysql_type=mysql_type,
        spark_type=logical_type[0],
        iceberg_type=logical_type[1],
        nullable=nullable,
        primary_key_ordinal=pk,
        checks=tuple(checks),
        references=references,
        metadata=metadata or {},
    )


ENTITIES: tuple[Entity, ...] = (
    Entity(
        "customers",
        1,
        (
            column("customer_id", "VARCHAR(64)", STRING, pk=1),
            column("customer_unique_id", "VARCHAR(64)", STRING),
            column("customer_zip_code_prefix", "VARCHAR(16)", STRING),
            column("customer_city", "VARCHAR(256)", STRING),
            column(
                "customer_state",
                "VARCHAR(2)",
                STRING,
                checks=("REGEXP '^[A-Z]{2}$'",),
            ),
        ),
    ),
    Entity(
        "orders",
        3,
        (
            column("order_id", "VARCHAR(64)", STRING, pk=1),
            column(
                "customer_id",
                "VARCHAR(64)",
                STRING,
                references="olist_oltp.customers(customer_id)",
            ),
            column(
                "order_status",
                "VARCHAR(32)",
                STRING,
                checks=(
                    "IN ('created','approved','invoiced','processing','shipped','delivered','unavailable','canceled')",
                ),
            ),
            column(
                "order_purchase_timestamp",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column(
                "order_approved_at",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                nullable=True,
                checks=("order_approved_at >= order_purchase_timestamp",),
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column(
                "order_delivered_carrier_date",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                nullable=True,
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column(
                "order_delivered_customer_date",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                nullable=True,
                checks=("order_delivered_customer_date >= order_purchase_timestamp",),
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column(
                "order_estimated_delivery_date",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
        ),
    ),
    Entity(
        "order_items",
        3,
        (
            column(
                "order_id",
                "VARCHAR(64)",
                STRING,
                pk=1,
                references="olist_oltp.orders(order_id)",
            ),
            column("order_item_id", "INT", INT, pk=2, checks=("> 0",)),
            column(
                "product_id",
                "VARCHAR(64)",
                STRING,
                references="olist_oltp.products(product_id)",
            ),
            column(
                "seller_id",
                "VARCHAR(64)",
                STRING,
                references="olist_oltp.sellers(seller_id)",
            ),
            column(
                "shipping_limit_date",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column("price", "DECIMAL(18,2)", DECIMAL_18_2, checks=(">= 0",)),
            column(
                "freight_value",
                "DECIMAL(18,2)",
                DECIMAL_18_2,
                checks=(">= 0",),
            ),
        ),
    ),
    Entity(
        "order_payments",
        3,
        (
            column(
                "order_id",
                "VARCHAR(64)",
                STRING,
                pk=1,
                references="olist_oltp.orders(order_id)",
            ),
            column("payment_sequential", "INT", INT, pk=2, checks=("> 0",)),
            column(
                "payment_type",
                "VARCHAR(32)",
                STRING,
                checks=(
                    "IN ('credit_card','boleto','voucher','debit_card','not_defined')",
                ),
            ),
            column("payment_installments", "INT", INT, checks=(">= 0",)),
            column(
                "payment_value",
                "DECIMAL(18,2)",
                DECIMAL_18_2,
                checks=(">= 0",),
            ),
        ),
    ),
    Entity(
        "order_reviews",
        3,
        (
            column("review_id", "VARCHAR(64)", STRING, pk=1),
            column(
                "order_id",
                "VARCHAR(64)",
                STRING,
                pk=2,
                references="olist_oltp.orders(order_id)",
            ),
            column("review_score", "INT", INT, checks=("BETWEEN 1 AND 5",)),
            column("review_comment_title", "VARCHAR(1024)", STRING, nullable=True),
            column("review_comment_message", "TEXT", STRING, nullable=True),
            column(
                "review_creation_date",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
            column(
                "review_answer_timestamp",
                "DATETIME(6)",
                TIMESTAMP_MICROS,
                checks=("review_answer_timestamp >= review_creation_date",),
                metadata={"precision": "microseconds", "timezone_semantics": "UTC"},
            ),
        ),
    ),
    Entity(
        "products",
        1,
        (
            column("product_id", "VARCHAR(64)", STRING, pk=1),
            column(
                "product_category_name",
                "VARCHAR(256)",
                STRING,
                nullable=True,
                references="olist_oltp.product_category_translation(product_category_name)",
            ),
            column("product_name_lenght", "INT", INT, nullable=True, checks=(">= 0",)),
            column(
                "product_description_lenght",
                "INT",
                INT,
                nullable=True,
                checks=(">= 0",),
            ),
            column("product_photos_qty", "INT", INT, nullable=True, checks=(">= 0",)),
            column("product_weight_g", "INT", INT, nullable=True, checks=(">= 0",)),
            column("product_length_cm", "INT", INT, nullable=True, checks=(">= 0",)),
            column("product_height_cm", "INT", INT, nullable=True, checks=(">= 0",)),
            column("product_width_cm", "INT", INT, nullable=True, checks=(">= 0",)),
        ),
    ),
    Entity(
        "sellers",
        1,
        (
            column("seller_id", "VARCHAR(64)", STRING, pk=1),
            column("seller_zip_code_prefix", "VARCHAR(16)", STRING),
            column("seller_city", "VARCHAR(256)", STRING),
            column(
                "seller_state",
                "VARCHAR(2)",
                STRING,
                checks=("REGEXP '^[A-Z]{2}$'",),
            ),
        ),
    ),
    Entity(
        "product_category_translation",
        1,
        (
            column("product_category_name", "VARCHAR(256)", STRING, pk=1),
            column("product_category_name_english", "VARCHAR(256)", STRING),
        ),
    ),
)


def avro_type(contract_column: Column) -> Any:
    if contract_column.spark_type == "string":
        base: Any = "string"
    elif contract_column.spark_type == "int":
        base = "int"
    elif contract_column.spark_type == "decimal(18,2)":
        base = {
            "type": "bytes",
            "logicalType": "decimal",
            "precision": 18,
            "scale": 2,
        }
    elif contract_column.spark_type == "timestamp":
        base = {"type": "long", "logicalType": "timestamp-micros"}
    else:
        raise ValueError(f"unsupported logical type: {contract_column.spark_type}")
    return ["null", base] if contract_column.nullable else base


def avro_field(contract_column: Column) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": contract_column.name,
        "type": avro_type(contract_column),
    }
    if contract_column.nullable:
        result["default"] = None
    return result


def source_schema() -> dict[str, Any]:
    nullable_string = ["null", "string"]
    nullable_long = ["null", "long"]
    return {
        "type": "record",
        "name": "Source",
        "namespace": "io.debezium.connector.mysql",
        "fields": [
            {"name": "version", "type": "string"},
            {"name": "connector", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "ts_ms", "type": "long"},
            {"name": "snapshot", "type": nullable_string, "default": None},
            {"name": "db", "type": "string"},
            {"name": "sequence", "type": nullable_string, "default": None},
            {"name": "ts_us", "type": nullable_long, "default": None},
            {"name": "ts_ns", "type": nullable_long, "default": None},
            {"name": "table", "type": ["null", "string"], "default": None},
            {"name": "server_id", "type": "long"},
            {"name": "gtid", "type": nullable_string, "default": None},
            {"name": "file", "type": "string"},
            {"name": "pos", "type": "long"},
            {"name": "row", "type": "int"},
            {"name": "thread", "type": nullable_long, "default": None},
            {"name": "query", "type": nullable_string, "default": None},
        ],
    }


def transaction_schema() -> dict[str, Any]:
    return {
        "type": "record",
        "name": "Transaction",
        "namespace": "io.olist.cdc.debezium",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "total_order", "type": "long"},
            {"name": "data_collection_order", "type": "long"},
        ],
    }


def key_schema(entity: Entity) -> dict[str, Any]:
    primary_key_columns = [
        next(column for column in entity.columns if column.name == key)
        for key in entity.primary_key
    ]
    return {
        "type": "record",
        "name": "Key",
        "namespace": f"olist_cdc.olist_oltp.{entity.name}",
        "fields": [
            avro_field(contract_column) for contract_column in primary_key_columns
        ],
    }


def value_schema(entity: Entity) -> dict[str, Any]:
    namespace = f"olist_cdc.olist_oltp.{entity.name}"
    row_schema = {
        "type": "record",
        "name": "Value",
        "namespace": namespace,
        "fields": [avro_field(contract_column) for contract_column in entity.columns],
    }
    return {
        "type": "record",
        "name": "Envelope",
        "namespace": namespace,
        "fields": [
            {"name": "before", "type": ["null", row_schema], "default": None},
            {"name": "after", "type": ["null", "Value"], "default": None},
            {"name": "source", "type": source_schema()},
            {
                "name": "transaction",
                "type": ["null", transaction_schema()],
                "default": None,
            },
            {"name": "op", "type": "string"},
            {"name": "ts_ms", "type": ["null", "long"], "default": None},
            {"name": "ts_us", "type": ["null", "long"], "default": None},
            {"name": "ts_ns", "type": ["null", "long"], "default": None},
        ],
    }


def mysql_column(contract_column: Column) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": contract_column.name,
        "mysql_type": contract_column.mysql_type,
        "nullable": contract_column.nullable,
        "spark_type": contract_column.spark_type,
        "iceberg_type": contract_column.iceberg_type,
    }
    if contract_column.primary_key_ordinal is not None:
        result["primary_key_ordinal"] = contract_column.primary_key_ordinal
    if contract_column.checks:
        result["checks"] = list(contract_column.checks)
    if contract_column.references:
        result["references"] = contract_column.references
    if contract_column.metadata:
        result["type_metadata"] = contract_column.metadata
    return result


def _allowed_writer_fingerprints(
    previous_contract: Mapping[str, Any] | None,
    repository: WriterSchemaRepository,
    entity: str,
    kind: str,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    if previous_contract is not None:
        previous_avro = previous_contract.get("avro")
        if isinstance(previous_avro, Mapping):
            previous_entries = previous_avro.get(f"allowed_{kind}_fingerprints", [])
            if isinstance(previous_entries, list):
                for entry in previous_entries:
                    if not isinstance(entry, Mapping):
                        continue
                    if entry.get("status") != "captured_writer_schema":
                        raise ValueError(
                            f"{entity}: refusing to carry non-captured {kind} fingerprint"
                        )
                    digest = entry.get("sha256")
                    if isinstance(digest, str) and digest not in seen:
                        entries.append(dict(entry))
                        seen.add(digest)
    # A partially captured manifest is useful as a J1 work product, but must
    # not activate any production allowlist. Only the complete 8x2 bundle is
    # eligible to generate new approved fingerprints.
    if repository.capture_complete:
        for entry in repository.allowed_entries(entity, kind):  # type: ignore[arg-type]
            digest = entry["sha256"]
            if digest not in seen:
                entries.append(entry)
                seen.add(digest)
    return entries


def generate_contract(
    entity: Entity,
    *,
    version: int = 1,
    previous_contract: Mapping[str, Any] | None = None,
    writer_repository: WriterSchemaRepository | None = None,
) -> dict[str, Any]:
    if version < 1:
        raise ValueError("contract version must be positive")
    if previous_contract is not None:
        if previous_contract.get("entity") != entity.name:
            raise ValueError("previous contract belongs to another entity")
        if previous_contract.get("contract_version") != version - 1:
            raise ValueError(
                "previous contract version must immediately precede target"
            )
    repository = writer_repository or load_writer_schema_repository()
    key = key_schema(entity)
    value = value_schema(entity)
    allowed_key = _allowed_writer_fingerprints(
        previous_contract, repository, entity.name, "key"
    )
    allowed_value = _allowed_writer_fingerprints(
        previous_contract, repository, entity.name, "value"
    )
    capture_state = (
        "captured" if allowed_key and allowed_value else "pending_runtime_capture"
    )
    return {
        "entity": entity.name,
        "contract_version": version,
        "topic": f"olist_cdc.olist_oltp.{entity.name}",
        "topic_partitions": entity.partitions,
        "primary_key": list(entity.primary_key),
        "mysql_database": "olist_oltp",
        "mysql_table": entity.name,
        "mysql_columns": [mysql_column(item) for item in entity.columns],
        "avro": {
            "wire_format": "confluent",
            "magic_byte": 0,
            "schema_id_bytes": 4,
            "schema_id_byte_order": "big-endian",
            "fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "reader_schema_role": "contractual_reader_not_writer_provenance",
            "writer_schema_capture_state": capture_state,
            "key_reader_schema": key,
            "value_reader_schema": value,
            "allowed_key_fingerprints": allowed_key,
            "allowed_value_fingerprints": allowed_value,
        },
        "spark_reader_schema": {
            "key_schema_json_pointer": "#/avro/key_reader_schema",
            "value_schema_json_pointer": "#/avro/value_reader_schema",
            "strip_confluent_prefix_bytes": 5,
            "from_avro_mode": "FAILFAST",
            "writer_schema_source": "bronze.avro_schemas.spark_self_contained_schema_json",
        },
        "iceberg_projection": {
            "changes_table": f"silver.{entity.name}_changes",
            "current_table": f"silver.{entity.name}_current",
            "business_columns": [
                {
                    "name": item.name,
                    "type": item.iceberg_type,
                    "nullable": item.nullable,
                }
                for item in entity.columns
            ],
        },
        "evolution": {
            "registry_compatibility": "BACKWARD_TRANSITIVE",
            "allowed": ["add_nullable_field_with_default_null"],
            "forbidden": [
                "rename",
                "drop",
                "type_narrowing",
                "primary_key_change",
                "key_schema_change",
            ],
            "unknown_fingerprint_action": "stop_affected_silver_query",
            "incompatible_registration_action": "stop_connector",
            "key_schema_or_partition_change_action": "full_reset",
        },
    }


def _version_paths(root: Path, entity: str) -> list[tuple[int, Path]]:
    paths: list[tuple[int, Path]] = []
    for path in (root / entity).glob("v*.json"):
        stem = path.stem
        if stem.startswith("v") and stem[1:].isdigit() and int(stem[1:]) > 0:
            paths.append((int(stem[1:]), path))
    return sorted(paths)


def _load_contract(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def generated_files(
    root: Path = CONTRACTS_ROOT,
    *,
    new_version: int | None = None,
    writer_root: Path = WRITER_SCHEMAS_ROOT,
) -> dict[Path, str]:
    files: dict[Path, str] = {}
    manifest_entities: list[dict[str, Any]] = []
    repository = load_writer_schema_repository(writer_root)
    for entity in ENTITIES:
        existing = _version_paths(root, entity.name)
        latest = existing[-1][0] if existing else 0
        if new_version is not None:
            if new_version != latest + 1:
                raise ValueError(
                    f"{entity.name}: new version must be v{latest + 1}, got v{new_version}"
                )
            target_version = new_version
        else:
            target_version = latest or 1
        previous_contract = None
        if target_version > 1:
            previous_path = root / entity.name / f"v{target_version - 1}.json"
            if not previous_path.exists():
                raise ValueError(
                    f"{entity.name}: missing previous contract {previous_path.name}"
                )
            previous_contract = _load_contract(previous_path)
        contract = generate_contract(
            entity,
            version=target_version,
            previous_contract=previous_contract,
            writer_repository=repository,
        )
        relative_path = Path(entity.name) / f"v{target_version}.json"
        rendered = json.dumps(contract, ensure_ascii=False, indent=2) + "\n"
        files[relative_path] = rendered
        version_documents: dict[int, tuple[Path, dict[str, Any]]] = {
            number: (path.relative_to(root), _load_contract(path))
            for number, path in existing
        }
        version_documents[target_version] = (relative_path, contract)
        versions = [
            {
                "contract_version": number,
                "path": path.as_posix(),
                "contract_sha256": hashlib.sha256(
                    canonical_schema_json(document).encode("utf-8")
                ).hexdigest(),
            }
            for number, (path, document) in sorted(version_documents.items())
        ]
        current = versions[-1]
        manifest_entities.append(
            {
                "entity": entity.name,
                "contract_version": current["contract_version"],
                "path": current["path"],
                "contract_sha256": current["contract_sha256"],
                "versions": versions,
            }
        )
    manifest = {
        "manifest_version": 1,
        "entity_count": 8,
        "entities": manifest_entities,
    }
    files[Path("manifest.json")] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    return files


def write_contracts(
    root: Path = CONTRACTS_ROOT,
    *,
    new_version: int | None = None,
    writer_root: Path = WRITER_SCHEMAS_ROOT,
) -> None:
    for relative_path, content in generated_files(
        root, new_version=new_version, writer_root=writer_root
    ).items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def check_contracts(
    root: Path = CONTRACTS_ROOT, *, writer_root: Path = WRITER_SCHEMAS_ROOT
) -> list[str]:
    errors: list[str] = []
    try:
        expected = generated_files(root, writer_root=writer_root)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    expected_paths = {root / relative_path for relative_path in expected}
    actual_paths = set(root.rglob("*.json")) if root.exists() else set()
    historical_paths = {
        path for entity in ENTITIES for _, path in _version_paths(root, entity.name)
    }
    for path in sorted(expected_paths - actual_paths):
        errors.append(f"missing generated contract: {path}")
    for path in sorted(actual_paths - expected_paths - historical_paths):
        errors.append(f"unexpected generated contract JSON: {path}")
    for relative_path, expected_content in expected.items():
        path = root / relative_path
        if path.exists() and path.read_text(encoding="utf-8") != expected_content:
            errors.append(f"generated contract is stale: {path}")
    return errors


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=CONTRACTS_ROOT)
    parser.add_argument("--writer-root", type=Path, default=WRITER_SCHEMAS_ROOT)
    parser.add_argument("--new-version", type=int)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.write:
        try:
            write_contracts(
                args.root,
                new_version=args.new_version,
                writer_root=args.writer_root,
            )
        except (OSError, ValueError) as exc:
            print(exc)
            return 1
        print(f"Wrote eight current entity contracts under {args.root}")
        return 0
    if args.new_version is not None:
        print("--new-version is valid only with --write")
        return 1
    errors = check_contracts(args.root, writer_root=args.writer_root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Eight versioned entity contract chains are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
