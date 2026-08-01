from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

from scripts.simulation.database import (
    DatabaseSettings,
    SimulatorRepository,
    _json_object,
    _read_password_file,
    connect,
)
from scripts.simulation.domain import (
    SimulationConfig,
    WorkloadPlanner,
    normalize_speed_multiplier,
)
from scripts.simulation.engine import RunEngine


class FakeCursor:
    def __init__(self) -> None:
        self.closed = False
        self.executions: list[tuple[str, Any]] = []
        self.rowcount = 1
        self._rows: list[Any] = []
        self.description: Any = None

    def execute(self, statement: str, parameters: Any = None) -> None:
        self.executions.append((statement, parameters))

    def executemany(self, statement: str, parameters: Any) -> None:
        self.executions.append((statement, parameters))

    def fetchone(self) -> Any:
        return self._rows.pop(0) if self._rows else None

    def fetchall(self) -> list[Any]:
        rows = list(self._rows)
        self._rows.clear()
        return rows

    def close(self) -> None:
        self.closed = True


class FakeConnection:
    def __init__(self) -> None:
        self.cursors: list[FakeCursor] = []
        self.started = 0
        self.committed = 0
        self.rolled_back = 0

    def start_transaction(self) -> None:
        self.started += 1

    def cursor(self) -> FakeCursor:
        cursor = FakeCursor()
        self.cursors.append(cursor)
        return cursor

    def commit(self) -> None:
        self.committed += 1

    def rollback(self) -> None:
        self.rolled_back += 1


class RepositoryTransactionTests(unittest.TestCase):
    def test_injected_graph_failure_rolls_back_the_whole_lifecycle(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        plan = WorkloadPlanner(
            SimulationConfig(random_seed=42, start_time=datetime(2026, 1, 1))
        ).plan(0)

        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            repository.create_lifecycle(
                "rollback-run", plan, inject_failure_after_order=True
            )

        self.assertEqual(connection.started, 1)
        self.assertEqual(connection.committed, 0)
        self.assertEqual(connection.rolled_back, 1)
        self.assertTrue(connection.cursors[0].closed)
        statements = "\n".join(item[0] for item in connection.cursors[0].executions)
        self.assertIn("INSERT INTO olist_oltp.orders", statements)
        self.assertNotIn("INSERT INTO olist_oltp.order_items", statements)

    def test_start_run_uses_mysql_upsert_and_commits_once(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        config = SimulationConfig(random_seed=7, start_time=datetime(2026, 1, 1))

        repository.start_run("run-7", "run", config)

        self.assertEqual(connection.started, 1)
        self.assertEqual(connection.committed, 1)
        self.assertEqual(connection.rolled_back, 0)
        statement, parameters = connection.cursors[0].executions[0]
        self.assertIn("olist_simulator.simulation_runs", statement)
        self.assertIn("ON DUPLICATE KEY UPDATE", statement)
        self.assertNotIn("ON CONFLICT", statement)
        self.assertEqual(json.loads(parameters[4]), config.as_dict())

    def test_context_rolls_back_driver_errors_and_closes_cursor(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        with (
            self.assertRaisesRegex(ValueError, "broken unit"),
            repository.transaction(),
        ):
            raise ValueError("broken unit")
        self.assertEqual(connection.rolled_back, 1)
        self.assertEqual(connection.committed, 0)
        self.assertTrue(connection.cursors[0].closed)

    def test_terminal_updates_never_precede_last_committed_logical_time(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        requested_at = datetime(2026, 1, 1)

        repository.finish_run("run-7", "completed", requested_at)

        statement, parameters = connection.cursors[0].executions[0]
        self.assertEqual(statement.count("GREATEST("), 2)
        self.assertEqual(statement.count("last_committed_source_timestamp"), 2)
        self.assertEqual(parameters[0], "completed")
        self.assertEqual(parameters[-1], "run-7")

    def test_fail_run_rolls_back_then_persists_failed_terminal_state(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        failed_at = datetime(2026, 1, 1, 1)

        repository.fail_run("run-7", failed_at, "RuntimeError: simulator failed")

        self.assertEqual(connection.rolled_back, 1)
        self.assertEqual(connection.started, 1)
        self.assertEqual(connection.committed, 1)
        statement, parameters = connection.cursors[0].executions[0]
        self.assertIn("SET state = 'failed'", statement)
        self.assertIn("last_committed_source_timestamp", statement)
        self.assertEqual(parameters[-2], "RuntimeError: simulator failed")
        self.assertEqual(parameters[-1], "run-7")

    def test_replay_mapping_uses_duplicate_specific_upsert(self) -> None:
        connection = FakeConnection()
        repository = SimulatorRepository(connection)
        source_at = datetime(2020, 1, 1)
        replay_at = datetime(2026, 1, 1)

        repository.record_replay_mappings(
            "replay-7",
            "source-order",
            [(source_at, replay_at)],
            Decimal("60.0000"),
        )

        statement, parameters = connection.cursors[0].executions[0]
        self.assertIn("ON DUPLICATE KEY UPDATE", statement)
        self.assertNotIn("INSERT IGNORE", statement)
        self.assertEqual(parameters[0][-1], Decimal("60.0000"))


class RepositoryValueContractTests(unittest.TestCase):
    def test_connection_is_utc_utf8mb4_and_explicitly_transactional(self) -> None:
        connector = MagicMock()
        expected_connection = object()
        connector.connect.return_value = expected_connection
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text("secret\n", encoding="utf-8")
            settings = DatabaseSettings(
                password_file=path,
                host="mysql",
                port=3306,
                database="olist_oltp",
                user="olist_simulator",
                connect_timeout=19,
            )
            with patch(
                "scripts.simulation.database.import_module", return_value=connector
            ) as importer:
                connection = connect(settings)
        self.assertIs(connection, expected_connection)
        importer.assert_called_once_with("mysql.connector")
        connector.connect.assert_called_once_with(
            host="mysql",
            port=3306,
            database="olist_oltp",
            user="olist_simulator",
            password="secret",
            autocommit=True,
            charset="utf8mb4",
            collation="utf8mb4_0900_bin",
            time_zone="+00:00",
            connection_timeout=19,
        )

    def test_json_columns_are_normalized_from_driver_strings_or_dicts(self) -> None:
        self.assertEqual(_json_object('{"created": 2}'), {"created": 2})
        self.assertEqual(_json_object(b'{"deleted": 1}'), {"deleted": 1})
        self.assertEqual(_json_object({"reviewed": 3}), {"reviewed": 3})
        with self.assertRaises(TypeError):
            _json_object("[]")

    def test_password_file_only_removes_line_ending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "password"
            path.write_text("  secret with spaces  \n", encoding="utf-8")
            settings = DatabaseSettings(
                password_file=path,
                host="mysql",
                port=3306,
                database="olist_oltp",
                user="olist_simulator",
            )
            self.assertEqual(
                _read_password_file(settings.password_file), "  secret with spaces  "
            )
        self.assertFalse(hasattr(settings, "password"))
        self.assertEqual(settings.port, 3306)

    def test_password_file_is_required_readable_nonempty_and_one_line(self) -> None:
        with self.assertRaisesRegex(ValueError, "MYSQL_PASSWORD_FILE"):
            DatabaseSettings(password_file="")

        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            with self.assertRaisesRegex(ValueError, "not readable"):
                DatabaseSettings(password_file=missing)

            for name, content, message in (
                ("empty", "", "non-empty"),
                ("whitespace", "   \n", "non-empty"),
                ("multiline", "first\nsecond\n", "exactly one line"),
                ("extra-newline", "secret\n\n", "exactly one line"),
            ):
                with self.subTest(name=name):
                    path = Path(directory) / name
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, message):
                        DatabaseSettings(password_file=path)


class ReplaySpeedContractTests(unittest.TestCase):
    def test_values_are_rounded_to_mysql_decimal_12_4(self) -> None:
        self.assertEqual(normalize_speed_multiplier("1.23456"), Decimal("1.2346"))
        self.assertEqual(normalize_speed_multiplier("0.00005"), Decimal("0.0001"))
        self.assertEqual(
            normalize_speed_multiplier("99999999.9999"),
            Decimal("99999999.9999"),
        )

    def test_zero_nonfinite_and_precision_overflow_are_rejected(self) -> None:
        invalid = (
            "0",
            "-1",
            "NaN",
            "Infinity",
            "0.000049",
            "99999999.99991",
            "99999999.99995",
            "100000000",
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_speed_multiplier(value)


class RecordingEngineRepository:
    def __init__(
        self,
        *,
        candidates: list[dict[str, Any]] | None = None,
        fail_create: bool = False,
    ) -> None:
        self.candidates = candidates or []
        self.fail_create = fail_create
        self.started: list[tuple[str, str]] = []
        self.created: list[Any] = []
        self.mappings: list[tuple[str, str, Decimal]] = []
        self.finished: list[tuple[str, str, datetime]] = []
        self.failed: list[tuple[str, datetime, str]] = []
        self.reviews = 0
        self.deletes = 0

    def start_run(self, run_id: str, command: str, _config: Any) -> None:
        self.started.append((run_id, command))

    def stop_requested(self, _run_id: str) -> bool:
        return False

    def create_lifecycle(self, _run_id: str, plan: Any) -> None:
        if self.fail_create:
            raise RuntimeError("lifecycle write failed")
        self.created.append(plan)

    def apply_transition(self, *_arguments: Any) -> None:
        return None

    def add_review(self, *_arguments: Any) -> None:
        self.reviews += 1

    def apply_correction(self, *_arguments: Any) -> None:
        return None

    def hard_delete_order(self, *_arguments: Any) -> None:
        self.deletes += 1

    def finish_run(self, run_id: str, state: str, finished_at: datetime) -> None:
        self.finished.append((run_id, state, finished_at))

    def fail_run(
        self,
        run_id: str,
        failed_at: datetime,
        error_message: str,
    ) -> None:
        self.failed.append((run_id, failed_at, error_message))

    def replay_candidates(self, _event_limit: int | None) -> list[dict[str, Any]]:
        return self.candidates

    def record_replay_mappings(
        self,
        run_id: str,
        source_order_id: str,
        _mappings: list[tuple[datetime, datetime]],
        speed_multiplier: Decimal,
    ) -> None:
        self.mappings.append((run_id, source_order_id, speed_multiplier))


class RunTerminalStateTests(unittest.TestCase):
    def test_run_failure_is_persisted_after_the_failed_unit_rolls_back(self) -> None:
        repository = RecordingEngineRepository(fail_create=True)
        config = SimulationConfig(random_seed=1, start_time=datetime(2026, 1, 1))

        with self.assertRaisesRegex(RuntimeError, "lifecycle write failed"):
            RunEngine(cast(Any, repository)).run(
                "failed-run",
                config,
                event_limit=1,
                pace=False,
            )

        self.assertEqual(repository.started, [("failed-run", "run")])
        self.assertEqual(repository.finished, [])
        self.assertEqual(
            repository.failed,
            [
                (
                    "failed-run",
                    config.start_time,
                    "RuntimeError: simulator command failed",
                )
            ],
        )

    def test_replay_failure_is_persisted_instead_of_remaining_running(self) -> None:
        source_at = datetime(2018, 1, 1)
        repository = RecordingEngineRepository(
            candidates=[
                {
                    "order_id": "source-order",
                    "order_status": "canceled",
                    "order_purchase_timestamp": source_at,
                    "order_approved_at": source_at + timedelta(minutes=2),
                    "order_delivered_carrier_date": None,
                    "order_delivered_customer_date": None,
                    "order_estimated_delivery_date": source_at + timedelta(days=7),
                    "has_review": False,
                }
            ],
            fail_create=True,
        )
        config = SimulationConfig(random_seed=2, start_time=datetime(2026, 1, 1))

        with self.assertRaisesRegex(RuntimeError, "lifecycle write failed"):
            RunEngine(cast(Any, repository)).replay(
                "failed-replay",
                config,
                event_limit=1,
                speed_multiplier=Decimal("60"),
            )

        self.assertEqual(repository.started, [("failed-replay", "replay")])
        self.assertEqual(repository.finished, [])
        self.assertEqual(repository.failed[0][:2], ("failed-replay", config.start_time))
        self.assertEqual(repository.mappings[0][-1], Decimal("60.0000"))

    def test_run_finish_is_at_or_after_review_and_hard_delete(self) -> None:
        repository = RecordingEngineRepository()
        config = SimulationConfig(
            random_seed=3,
            start_time=datetime(2026, 1, 1),
            cancel_probability=0,
            unavailable_probability=0,
            review_probability=1,
            correction_probability=1,
            hard_delete_probability=1,
        )

        completed = RunEngine(cast(Any, repository)).run(
            "logical-finish",
            config,
            event_limit=1,
            pace=False,
        )

        self.assertEqual(completed, 1)
        plan = repository.created[0]
        expected_finish = plan.transitions[-1].occurred_at + timedelta(days=2)
        self.assertEqual(
            repository.finished,
            [("logical-finish", "completed", expected_finish)],
        )
        self.assertEqual(repository.reviews, 1)
        self.assertEqual(repository.deletes, 1)

    def test_replay_finish_is_at_or_after_the_committed_review(self) -> None:
        source_at = datetime(2018, 1, 1)
        delivered_at = source_at + timedelta(days=3)
        repository = RecordingEngineRepository(
            candidates=[
                {
                    "order_id": "source-order",
                    "order_status": "delivered",
                    "order_purchase_timestamp": source_at,
                    "order_approved_at": source_at + timedelta(minutes=2),
                    "order_delivered_carrier_date": source_at + timedelta(hours=12),
                    "order_delivered_customer_date": delivered_at,
                    "order_estimated_delivery_date": source_at + timedelta(days=7),
                    "has_review": True,
                }
            ]
        )
        config = SimulationConfig(random_seed=4, start_time=datetime(2026, 1, 1))

        completed = RunEngine(cast(Any, repository)).replay(
            "logical-replay-finish",
            config,
            event_limit=1,
            speed_multiplier=Decimal("60"),
        )

        self.assertEqual(completed, 1)
        plan = repository.created[0]
        expected_finish = plan.transitions[-1].occurred_at + timedelta(days=1)
        self.assertEqual(
            repository.finished,
            [("logical-replay-finish", "completed", expected_finish)],
        )
        self.assertEqual(repository.reviews, 1)


class TransactionBoundaryStopTests(unittest.TestCase):
    def test_stop_after_graph_commit_prevents_the_first_transition(self) -> None:
        class StopRepository:
            def __init__(self) -> None:
                self.checks = 0
                self.created = 0
                self.transitions = 0
                self.finished: tuple[str, str, datetime] | None = None

            def start_run(self, _run_id: str, _command: str, _config: Any) -> None:
                return None

            def stop_requested(self, _run_id: str) -> bool:
                self.checks += 1
                return self.checks == 2

            def create_lifecycle(self, _run_id: str, _plan: Any) -> None:
                self.created += 1

            def apply_transition(self, *_arguments: Any) -> None:
                self.transitions += 1

            def add_review(self, *_arguments: Any) -> None:
                raise AssertionError("review must not run after a stop request")

            def apply_correction(self, *_arguments: Any) -> None:
                raise AssertionError("correction must not run after a stop request")

            def hard_delete_order(self, *_arguments: Any) -> None:
                raise AssertionError("delete must not run after a stop request")

            def finish_run(
                self, run_id: str, state: str, finished_at: datetime
            ) -> None:
                self.finished = (run_id, state, finished_at)

        repository = StopRepository()
        config = SimulationConfig(random_seed=10, start_time=datetime(2026, 1, 1))
        completed = RunEngine(cast(Any, repository)).run(
            "boundary-stop", config, event_limit=2, pace=False
        )
        self.assertEqual(completed, 0)
        self.assertEqual(repository.created, 1)
        self.assertEqual(repository.transitions, 0)
        self.assertEqual(
            repository.finished,
            ("boundary-stop", "stopped", config.start_time),
        )


if __name__ == "__main__":
    unittest.main()
