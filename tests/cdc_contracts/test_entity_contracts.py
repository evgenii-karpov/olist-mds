from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from streaming.schemas.compatibility import (
    check_backward_transitive,
    compare_reader_to_writer,
    validate_contract_evolution,
)
from streaming.schemas.contracts import (
    ENTITY_NAMES,
    load_contracts,
    validate_contract_repository,
)
from streaming.schemas.generate_contracts import (
    check_contracts,
    write_contracts,
)
from streaming.schemas.writer_schemas import (
    WriterSchemasPending,
    load_writer_schema_repository,
    validate_writer_schema_repository,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = ROOT / "streaming" / "schemas" / "contracts"
TOPICS_PATH = ROOT / "streaming" / "kafka" / "topics.json"

EXPECTED_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "product_category_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
}

EXPECTED_PRIMARY_KEYS = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id", "order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "product_category_translation": ["product_category_name"],
}


class EntityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contracts = load_contracts(CONTRACT_ROOT)

    def test_repository_has_exactly_eight_current_v1_contracts(self) -> None:
        self.assertEqual([], validate_contract_repository(CONTRACT_ROOT))
        self.assertEqual([], check_contracts(CONTRACT_ROOT))
        self.assertEqual(set(ENTITY_NAMES), set(self.contracts))
        self.assertEqual(
            8,
            len(list(CONTRACT_ROOT.glob("*/v1.json"))),
        )
        self.assertFalse((CONTRACT_ROOT / "geolocation").exists())

    def test_topics_primary_keys_and_mysql_columns_are_fixed(self) -> None:
        topic_manifest = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
        partitions = {
            topic["name"]: topic["partitions"] for topic in topic_manifest["topics"]
        }
        for entity, versioned in self.contracts.items():
            with self.subTest(entity=entity):
                contract = versioned.document
                self.assertEqual(versioned.version, contract["contract_version"])
                self.assertEqual(f"olist_cdc.olist_oltp.{entity}", contract["topic"])
                self.assertEqual(
                    partitions[contract["topic"]], contract["topic_partitions"]
                )
                self.assertEqual(EXPECTED_PRIMARY_KEYS[entity], contract["primary_key"])
                self.assertEqual(
                    EXPECTED_COLUMNS[entity],
                    [column["name"] for column in contract["mysql_columns"]],
                )

    def test_exact_type_mappings_have_no_float_money_or_time(self) -> None:
        for versioned in self.contracts.values():
            for column in versioned.document["mysql_columns"]:
                mysql_type = column["mysql_type"]
                spark_type = column["spark_type"]
                iceberg_type = column["iceberg_type"]
                if mysql_type == "DECIMAL(18,2)":
                    self.assertEqual("decimal(18,2)", spark_type)
                    self.assertEqual("decimal(18,2)", iceberg_type)
                if mysql_type == "DATETIME(6)":
                    self.assertEqual("timestamp", spark_type)
                    self.assertEqual("timestamp", iceberg_type)
                    self.assertEqual(
                        "microseconds", column["type_metadata"]["precision"]
                    )
                self.assertNotIn("float", spark_type.lower())
                self.assertNotIn("double", spark_type.lower())

    def test_writer_fingerprints_fail_closed_until_j1_capture(self) -> None:
        repository = load_writer_schema_repository()
        if repository.capture_complete:
            for _entity, versioned in self.contracts.items():
                avro = versioned.document["avro"]
                self.assertEqual("captured", avro["writer_schema_capture_state"])
                for kind in ("key", "value"):
                    allowed = versioned.allowed_fingerprints(kind)
                    self.assertTrue(allowed)
                    versioned.assert_fingerprint_allowed(kind, next(iter(allowed)))
            self.assertEqual(
                [], validate_writer_schema_repository(require_captured=True)
            )
            return

        for _entity, versioned in self.contracts.items():
            avro = versioned.document["avro"]
            self.assertEqual(
                "pending_runtime_capture", avro["writer_schema_capture_state"]
            )
            for kind in ("key", "value"):
                self.assertEqual([], avro[f"allowed_{kind}_fingerprints"])
                with self.assertRaises(WriterSchemasPending):
                    versioned.assert_fingerprint_allowed(kind, "0" * 64)
        errors = validate_writer_schema_repository(require_captured=True)
        self.assertEqual(1, len(errors))
        self.assertIn("J1 must run", errors[0])

    def test_generator_adds_v1_through_vn_without_rewriting_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "contracts"
            write_contracts(root)
            original_v1 = {
                entity: (root / entity / "v1.json").read_bytes()
                for entity in ENTITY_NAMES
            }
            write_contracts(root, new_version=2)
            original_v2 = {
                entity: (root / entity / "v2.json").read_bytes()
                for entity in ENTITY_NAMES
            }
            write_contracts(root, new_version=3)

            self.assertEqual([], check_contracts(root))
            self.assertEqual([], validate_contract_repository(root))
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            for entry in manifest["entities"]:
                entity = entry["entity"]
                self.assertEqual(
                    original_v1[entity], (root / entity / "v1.json").read_bytes()
                )
                self.assertEqual(
                    original_v2[entity], (root / entity / "v2.json").read_bytes()
                )
                self.assertTrue((root / entity / "v3.json").exists())
                self.assertEqual(
                    [1, 2, 3],
                    [item["contract_version"] for item in entry["versions"]],
                )

    def test_validator_ties_mysql_avro_pk_and_iceberg_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "contracts"
            shutil.copytree(CONTRACT_ROOT, root)
            path = root / "customers" / "v1.json"
            contract = json.loads(path.read_text(encoding="utf-8"))
            contract["mysql_columns"][0]["nullable"] = True
            contract["avro"]["key_reader_schema"]["fields"][0]["type"] = [
                "null",
                "string",
            ]
            contract["iceberg_projection"]["business_columns"][0]["type"] = "binary"
            path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

            errors = validate_contract_repository(root)
            self.assertTrue(
                any(
                    "primary-key columns must be non-nullable" in item
                    for item in errors
                )
            )
            self.assertTrue(
                any("Avro type/nullability differs" in item for item in errors)
            )
            self.assertTrue(any("Iceberg type differs" in item for item in errors))

    def test_spark_reader_and_iceberg_projection_are_complete(self) -> None:
        for entity, versioned in self.contracts.items():
            contract = versioned.document
            spark = contract["spark_reader_schema"]
            self.assertEqual(5, spark["strip_confluent_prefix_bytes"])
            self.assertEqual("FAILFAST", spark["from_avro_mode"])
            self.assertEqual(
                "bronze.avro_schemas.spark_self_contained_schema_json",
                spark["writer_schema_source"],
            )
            projection = contract["iceberg_projection"]
            self.assertEqual(f"silver.{entity}_changes", projection["changes_table"])
            self.assertEqual(f"silver.{entity}_current", projection["current_table"])
            self.assertEqual(
                EXPECTED_COLUMNS[entity],
                [item["name"] for item in projection["business_columns"]],
            )

    def test_evolution_policy_has_only_nullable_addition(self) -> None:
        required_forbidden = {
            "rename",
            "drop",
            "type_narrowing",
            "primary_key_change",
            "key_schema_change",
        }
        for versioned in self.contracts.values():
            evolution = versioned.document["evolution"]
            self.assertEqual("BACKWARD_TRANSITIVE", evolution["registry_compatibility"])
            self.assertEqual(
                ["add_nullable_field_with_default_null"], evolution["allowed"]
            )
            self.assertEqual(required_forbidden, set(evolution["forbidden"]))
            self.assertEqual(
                "stop_affected_silver_query",
                evolution["unknown_fingerprint_action"],
            )
            self.assertEqual(
                "full_reset", evolution["key_schema_or_partition_change_action"]
            )


def record(fields: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": "record",
        "name": "Entity",
        "namespace": "io.olist.test",
        "fields": fields,
    }


class EvolutionCompatibilityTests(unittest.TestCase):
    def test_nullable_default_null_addition_is_backward_transitive(self) -> None:
        v1 = record([{"name": "id", "type": "string"}])
        v2 = record(
            [
                {"name": "id", "type": "string"},
                {"name": "note", "type": ["null", "string"], "default": None},
            ]
        )
        v3 = record(
            [
                {"name": "id", "type": "string"},
                {"name": "note", "type": ["null", "string"], "default": None},
                {"name": "flag", "type": ["null", "int"], "default": None},
            ]
        )
        self.assertEqual([], check_backward_transitive([v1, v2, v3]))

    def test_drop_rename_narrowing_and_required_addition_are_rejected(self) -> None:
        writer = record(
            [
                {"name": "id", "type": "string"},
                {"name": "count", "type": "long"},
            ]
        )
        reader = record(
            [
                {"name": "renamed_id", "type": "string"},
                {"name": "count", "type": "int"},
                {"name": "required", "type": "string"},
            ]
        )
        codes = {issue.code for issue in compare_reader_to_writer(reader, writer)}
        self.assertIn("field_removed_or_renamed", codes)
        self.assertIn("type_change", codes)
        self.assertIn("non_nullable_addition", codes)

    def test_contract_pk_and_key_schema_change_require_reset(self) -> None:
        contract = load_contracts(CONTRACT_ROOT)["customers"].document
        changed = copy.deepcopy(dict(contract))
        changed["primary_key"] = ["customer_unique_id"]
        changed["avro"]["key_reader_schema"]["fields"][0]["name"] = "customer_unique_id"
        codes = {issue.code for issue in validate_contract_evolution(contract, changed)}
        self.assertIn("primary_key_change", codes)
        self.assertIn("key_schema_change", codes)

    def test_partition_change_requires_explicit_full_reset_action(self) -> None:
        contract = load_contracts(CONTRACT_ROOT)["customers"].document
        changed = copy.deepcopy(dict(contract))
        changed["topic_partitions"] = 2
        changed["evolution"]["key_schema_or_partition_change_action"] = "reject"
        codes = {issue.code for issue in validate_contract_evolution(contract, changed)}
        self.assertIn("partition_change_without_reset", codes)

        changed["evolution"]["key_schema_or_partition_change_action"] = "full_reset"
        codes = {issue.code for issue in validate_contract_evolution(contract, changed)}
        self.assertNotIn("partition_change_without_reset", codes)

    def test_allowed_fingerprints_are_monotonic_supersets(self) -> None:
        contract = load_contracts(CONTRACT_ROOT)["customers"].document
        old = copy.deepcopy(dict(contract))
        new = copy.deepcopy(dict(contract))
        captured = {
            "sha256": "a" * 64,
            "status": "captured_writer_schema",
            "source": "captured-writer-schemas/customers/key/example.avsc",
            "provenance_ref": "manifest-ref",
        }
        old["avro"]["allowed_key_fingerprints"] = [captured]
        new["avro"]["allowed_key_fingerprints"] = []
        codes = {issue.code for issue in validate_contract_evolution(old, new)}
        self.assertIn("allowed_fingerprint_removed", codes)

    def test_contract_nullable_column_addition_is_allowed(self) -> None:
        contract = load_contracts(CONTRACT_ROOT)["customers"].document
        changed = copy.deepcopy(dict(contract))
        changed["contract_version"] = 2
        changed["mysql_columns"].append(
            {
                "name": "customer_note",
                "mysql_type": "VARCHAR(256)",
                "nullable": True,
                "spark_type": "string",
                "iceberg_type": "string",
            }
        )
        changed["avro"]["value_reader_schema"]["fields"][0]["type"][1]["fields"].append(
            {
                "name": "customer_note",
                "type": ["null", "string"],
                "default": None,
            }
        )
        self.assertEqual([], validate_contract_evolution(contract, changed))


if __name__ == "__main__":
    unittest.main()
