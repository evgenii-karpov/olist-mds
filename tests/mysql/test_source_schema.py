from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MYSQL_ROOT = ROOT / "infra" / "mysql"


def compact(value: str) -> str:
    return " ".join(value.lower().split())


class MySQLServerConfigurationTests(unittest.TestCase):
    def test_server_settings_match_the_lakehouse_source_contract(self) -> None:
        configuration = (MYSQL_ROOT / "conf.d" / "olist.cnf").read_text(
            encoding="utf-8"
        )
        expected = {
            "character-set-server=utf8mb4",
            "collation-server=utf8mb4_0900_bin",
            "default-time-zone=+00:00",
            "server-id=18401",
            "log-bin=mysql-bin",
            "binlog_format=ROW",
            "binlog_row_image=FULL",
            "binlog_row_metadata=FULL",
            "gtid_mode=ON",
            "enforce_gtid_consistency=ON",
            "binlog_expire_logs_seconds=604800",
            "sync_binlog=1",
            "innodb_flush_log_at_trx_commit=1",
        }
        self.assertTrue(expected.issubset(set(configuration.splitlines())))
        self.assertIn(
            "sql_mode=STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY,NO_ZERO_IN_DATE,"
            "NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION",
            configuration,
        )

    def test_init_creates_only_the_two_fixed_databases(self) -> None:
        ddl = (MYSQL_ROOT / "initdb" / "010_create_databases.sql").read_text(
            encoding="utf-8"
        )
        databases = re.findall(
            r"create\s+database\s+if\s+not\s+exists\s+(\w+)", ddl, re.IGNORECASE
        )
        self.assertEqual(databases, ["olist_oltp", "olist_simulator"])
        self.assertEqual(ddl.lower().count("utf8mb4_0900_bin"), 3)


class MySQLBusinessSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (MYSQL_ROOT / "initdb" / "020_create_business_schema.sql").read_text(
            encoding="utf-8"
        )
        cls.ddl = compact(cls.raw)

    def test_business_relation_set_is_exact(self) -> None:
        relations = re.findall(
            r"create\s+table\s+if\s+not\s+exists\s+olist_oltp\.(\w+)",
            self.raw,
            re.IGNORECASE,
        )
        self.assertEqual(
            set(relations),
            {
                "customers",
                "orders",
                "order_items",
                "order_payments",
                "order_reviews",
                "products",
                "sellers",
                "product_category_translation",
                "geolocation",
            },
        )
        self.assertEqual(len(relations), 9)
        self.assertEqual(self.ddl.count("engine = innodb"), 9)

    def test_ids_strings_money_coordinates_and_times_are_exact(self) -> None:
        required_fragments = (
            "customer_id varchar(64) not null",
            "order_id varchar(64) not null",
            "product_category_name varchar(256) not null",
            "price decimal(18, 2) not null",
            "freight_value decimal(18, 2) not null",
            "payment_value decimal(18, 2) not null",
            "geolocation_lat decimal(18, 14) not null",
            "geolocation_lng decimal(18, 14) not null",
            "geolocation_id bigint not null auto_increment",
            "order_purchase_timestamp datetime(6) not null",
            "order_approved_at datetime(6) null",
            "shipping_limit_date datetime(6) not null",
            "review_answer_timestamp datetime(6) not null",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.ddl)
        self.assertNotRegex(self.raw, r"(?i)\b(float|double|real)\b")
        self.assertNotRegex(self.raw, r"(?i)\b(timestamp)\b")

    def test_natural_and_composite_keys_are_preserved(self) -> None:
        for fragment in (
            "primary key (customer_id)",
            "primary key (order_id)",
            "primary key (order_id, order_item_id)",
            "primary key (order_id, payment_sequential)",
            "primary key (review_id, order_id)",
            "primary key (product_category_name)",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.ddl)

    def test_business_checks_and_foreign_keys_are_preserved(self) -> None:
        self.assertIn("customer_state regexp '^[a-z]{2}$'", self.ddl)
        self.assertIn("seller_state regexp '^[a-z]{2}$'", self.ddl)
        self.assertIn("order_item_id > 0", self.ddl)
        self.assertIn("payment_sequential > 0", self.ddl)
        self.assertIn("payment_installments >= 0", self.ddl)
        self.assertIn("review_score between 1 and 5", self.ddl)
        self.assertIn("review_answer_timestamp >= review_creation_date", self.ddl)
        self.assertIn("order_approved_at >= order_purchase_timestamp", self.ddl)
        self.assertIn(
            "order_delivered_customer_date >= order_purchase_timestamp", self.ddl
        )
        self.assertNotIn("ck_orders_carrier_after_purchase", self.ddl)
        self.assertEqual(self.ddl.count(" foreign key ("), 7)
        self.assertNotIn("deferrable", self.ddl)

    def test_enum_checks_preserve_the_source_contract(self) -> None:
        for value in (
            "'created'",
            "'approved'",
            "'invoiced'",
            "'processing'",
            "'shipped'",
            "'delivered'",
            "'unavailable'",
            "'canceled'",
            "'credit_card'",
            "'boleto'",
            "'voucher'",
            "'debit_card'",
            "'not_defined'",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.ddl)

    def test_wire_contract_keeps_original_length_spelling(self) -> None:
        for column in (
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ):
            self.assertRegex(self.raw, rf"(?im)^\s*{column}\s+INT\s+NULL,")


class MySQLControlSchemaAndUserTests(unittest.TestCase):
    def test_control_relation_set_and_json_types_are_exact(self) -> None:
        raw = (MYSQL_ROOT / "initdb" / "030_create_simulator_schema.sql").read_text(
            encoding="utf-8"
        )
        ddl = compact(raw)
        relations = re.findall(
            r"create\s+table\s+if\s+not\s+exists\s+olist_simulator\.(\w+)",
            raw,
            re.IGNORECASE,
        )
        self.assertEqual(
            set(relations),
            {
                "simulation_runs",
                "generated_ids",
                "synthetic_entities",
                "pending_transitions",
                "replay_timestamp_mappings",
                "seed_rows",
                "heartbeats",
            },
        )
        self.assertIn("configuration json not null", ddl)
        self.assertIn("counters json not null default (json_object())", ddl)
        self.assertIn("payload json not null default (json_object())", ddl)
        self.assertIn("heartbeat_id bigint not null", ddl)
        self.assertIn("heartbeat_ts datetime(6) not null", ddl)
        self.assertNotIn("jsonb", ddl)

    def test_replay_speed_and_mapping_constraints_are_exact(self) -> None:
        raw = (MYSQL_ROOT / "initdb" / "030_create_simulator_schema.sql").read_text(
            encoding="utf-8"
        )
        ddl = compact(raw)
        self.assertIn("speed_multiplier decimal(12, 4) not null", ddl)
        self.assertIn("check (speed_multiplier > 0)", ddl)

        repository_code = (ROOT / "scripts" / "simulation" / "database.py").read_text(
            encoding="utf-8"
        )
        replay_statement = repository_code.split(
            "def record_replay_mappings", maxsplit=1
        )[1].split("@staticmethod", maxsplit=1)[0]
        self.assertIn("ON DUPLICATE KEY UPDATE", replay_statement)
        self.assertNotIn("INSERT IGNORE", replay_statement)

    def test_database_settings_have_no_plaintext_password_field(self) -> None:
        repository_code = (ROOT / "scripts" / "simulation" / "database.py").read_text(
            encoding="utf-8"
        )
        settings_block = repository_code.split("class DatabaseSettings", maxsplit=1)[
            1
        ].split("def _password_path", maxsplit=1)[0]
        self.assertIn("password_file", settings_block)
        self.assertNotRegex(settings_block, r"(?m)^\s+password\s*:")

    def test_users_and_minimal_cdc_grants_are_explicit(self) -> None:
        script = (MYSQL_ROOT / "initdb" / "040_create_users.sh").read_text(
            encoding="utf-8"
        )
        normalized = compact(script)
        for user in ("olist_admin", "olist_simulator", "olist_cdc_reader"):
            self.assertIn(f"create user if not exists '{user}'@'%'", normalized)
        self.assertIn(
            "grant reload, show databases, replication slave, replication client "
            "on *.* to 'olist_cdc_reader'@'%'",
            normalized,
        )
        self.assertIn(
            "grant select, lock tables on olist_oltp.* to 'olist_cdc_reader'@'%'",
            normalized,
        )
        self.assertIn(
            "grant insert, update on olist_simulator.heartbeats "
            "to 'olist_cdc_reader'@'%'",
            normalized,
        )
        self.assertNotIn(
            "grant select, insert, update, delete on olist_simulator.* "
            "to 'olist_cdc_reader'@'%'",
            normalized,
        )
        self.assertIn("mysql_simulator_password_file", script.lower())
        self.assertIn("mysql_cdc_reader_password_file", script.lower())


if __name__ == "__main__":
    unittest.main()
