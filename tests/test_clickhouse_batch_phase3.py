from __future__ import annotations

import argparse
import csv
import gzip
import tempfile
import unittest
from pathlib import Path
from typing import Any

from scripts.loading.load_raw_to_clickhouse import (
    FAILURE_POINTS,
    deterministic_staging_table,
    load_csv_to_staging,
    validate_source_schema,
)
from scripts.loading.load_raw_to_postgres import RawLoadSpec
from scripts.quality.reconcile_batch import count_clickhouse_raw_rows


class FakeClickHouseQueryResult:
    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self.result_rows = rows
        self.first_row = rows[0] if rows else None


class FakeClickHouseClient:
    def __init__(self) -> None:
        self.queries: list[str] = []
        self.raw_inserts: list[dict[str, object]] = []

    def query(self, query: str, *args: Any, **kwargs: Any) -> FakeClickHouseQueryResult:
        self.queries.append(query)
        if "system.columns" in query:
            return FakeClickHouseQueryResult(
                [
                    ("customer_id",),
                    ("_batch_id",),
                    ("_loaded_at",),
                    ("_source_file",),
                    ("_source_system",),
                ]
            )
        return FakeClickHouseQueryResult([(7,)])

    def raw_insert(self, *args: Any, **kwargs: Any) -> object:
        self.raw_inserts.append({"args": args, "kwargs": kwargs})
        return object()

    def command(self, *args: Any, **kwargs: Any) -> object:
        return object()

    def close(self) -> None:
        return None


class ClickHouseBatchPhase3Tests(unittest.TestCase):
    def test_staging_table_name_is_deterministic_bounded_and_sanitized(self) -> None:
        long_run_id = "manual__2026-07-23T08:30:00+00:00/" + ("x" * 200)

        first = deterministic_staging_table("2018-09-01", long_run_id, "customers")
        second = deterministic_staging_table("2018-09-01", long_run_id, "customers")

        self.assertEqual(first, second)
        self.assertLessEqual(len(first), 93)
        self.assertRegex(first, r"^batch_staging_2018_09_01_manual__2026_07_23t")
        self.assertRegex(first, r"_[0-9a-f]{12}$")

    def test_validate_source_schema_rejects_header_drift(self) -> None:
        client = FakeClickHouseClient()
        spec = RawLoadSpec(entity_name="customers", file_name="customers.csv.gz")
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "customers.csv.gz"
            with gzip.open(
                source_path, mode="wt", encoding="utf-8", newline=""
            ) as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["customer_id", "_batch_id"])

            with self.assertRaisesRegex(ValueError, "does not match"):
                validate_source_schema(client, spec, source_path)

    def test_raw_insert_uses_csv_with_names_and_nullable_csv_settings(self) -> None:
        client = FakeClickHouseClient()
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "customers.csv.gz"
            with gzip.open(
                source_path, mode="wt", encoding="utf-8", newline=""
            ) as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["customer_id", "_batch_id"])
                writer.writerow(["c1", "2018-09-01"])

            load_csv_to_staging(
                client,
                "batch_staging_customers",
                source_path,
                ["customer_id", "_batch_id"],
            )

        insert_kwargs = client.raw_inserts[0]["kwargs"]
        self.assertIsInstance(insert_kwargs, dict)
        assert isinstance(insert_kwargs, dict)
        self.assertEqual(insert_kwargs["fmt"], "CSVWithNames")
        self.assertEqual(
            insert_kwargs["settings"]["input_format_csv_empty_as_default"],
            1,
        )
        self.assertEqual(
            insert_kwargs["settings"]["input_format_null_as_default"],
            1,
        )

    def test_clickhouse_raw_count_uses_batch_partition_filter(self) -> None:
        client = FakeClickHouseClient()

        observed = count_clickhouse_raw_rows(
            client,
            RawLoadSpec(entity_name="customers", file_name="customers.csv.gz"),
            "2018-09-01",
        )

        self.assertEqual(observed, 7)
        self.assertIn("raw_data", client.queries[0])
        self.assertIn("customers", client.queries[0])
        self.assertIn("_batch_id = '2018-09-01'", client.queries[0])

    def test_all_declared_failure_points_are_cli_choices(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--inject-failure", choices=sorted(FAILURE_POINTS))

        for point in FAILURE_POINTS:
            args = parser.parse_args(["--inject-failure", point])
            self.assertEqual(args.inject_failure, point)

    def test_local_dag_exposes_explicit_clickhouse_candidate_parameters(self) -> None:
        dag_text = (
            Path(__file__).resolve().parents[1]
            / "airflow"
            / "dags"
            / "olist_modern_data_stack_local.py"
        ).read_text(encoding="utf-8")

        self.assertIn('"warehouse_target"', dag_text)
        self.assertIn('enum=["postgres", "clickhouse"]', dag_text)
        self.assertIn("scripts/loading/load_raw_to_clickhouse.py", dag_text)
        self.assertIn('"--warehouse-type"', dag_text)
        self.assertIn('"run_dbt"', dag_text)


if __name__ == "__main__":
    unittest.main()
