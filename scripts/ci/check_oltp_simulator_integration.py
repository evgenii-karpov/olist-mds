"""Bounded Stage 1 integration proof against the Compose OLTP service."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.simulation.database import DatabaseSettings, SimulatorRepository, connect
from scripts.simulation.domain import SimulationConfig, WorkloadPlanner
from scripts.simulation.engine import RunEngine
from scripts.simulation.seeding import SEED_SPECS, seed_archive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5433)
    parser.add_argument("--database", default="olist_oltp")
    parser.add_argument("--user", default="olist_simulator")
    parser.add_argument("--password")
    parser.add_argument("--password-file", required=True)
    parser.add_argument(
        "--archive", default="tests/fixtures/olist_small/olist_small.zip"
    )
    return parser.parse_args()


def table_counts(repository: SimulatorRepository) -> dict[str, int]:
    counts: dict[str, int] = {}
    with repository.connection.cursor() as cursor:
        for spec in SEED_SPECS:
            cursor.execute(f"select count(*) from public.{spec.entity_name}")
            row = cursor.fetchone()
            counts[spec.entity_name] = int(row[0] if row else -1)
    return counts


def assert_true(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


def required_value(row: tuple[Any, ...] | None, message: str) -> Any:
    if row is None:
        raise AssertionError(message)
    return row[0]


def main() -> int:
    args = parse_args()
    settings = DatabaseSettings.with_password_file(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
        password_file=args.password_file,
    )
    connection = connect(settings)
    repository = SimulatorRepository(connection)
    logical_start = datetime(2026, 7, 16)
    try:
        first = seed_archive(
            repository,
            Path(args.archive),
            random_seed=101,
            run_id="integration-seed-first",
            logical_time=logical_start,
        )
        first_counts = table_counts(repository)
        second = seed_archive(
            repository,
            Path(args.archive),
            random_seed=101,
            run_id="integration-seed-second",
            logical_time=logical_start,
        )
        second_counts = table_counts(repository)
        assert_true(first == second, "seed reports changed between identical runs")
        assert_true(first_counts == second_counts, "seed is not idempotent")

        delivered = SimulationConfig(
            random_seed=201,
            start_time=logical_start,
            cancel_probability=0,
            unavailable_probability=0,
            review_probability=1,
            correction_probability=1,
            hard_delete_probability=0,
        )
        RunEngine(repository).run(
            "integration-delivered", delivered, event_limit=4, pace=False
        )
        canceled = replace(
            delivered,
            random_seed=202,
            cancel_probability=1,
            unavailable_probability=0,
            review_probability=0,
            correction_probability=0,
        )
        RunEngine(repository).run(
            "integration-canceled", canceled, event_limit=1, pace=False
        )
        unavailable = replace(
            delivered,
            random_seed=203,
            unavailable_probability=1,
            review_probability=0,
            correction_probability=0,
        )
        RunEngine(repository).run(
            "integration-unavailable", unavailable, event_limit=1, pace=False
        )
        deletion = replace(
            delivered,
            random_seed=204,
            review_probability=1,
            correction_probability=0,
            hard_delete_probability=1,
        )
        RunEngine(repository).run(
            "integration-delete", deletion, event_limit=1, pace=False
        )

        rollback_config = replace(delivered, random_seed=205)
        repository.start_run("integration-rollback", "run", rollback_config)
        rollback_plan = WorkloadPlanner(rollback_config).plan(0)
        try:
            repository.create_lifecycle(
                "integration-rollback",
                rollback_plan,
                inject_failure_after_order=True,
            )
        except RuntimeError:
            pass
        else:
            raise AssertionError("injected transaction failure did not propagate")
        with connection.cursor() as cursor:
            cursor.execute(
                "select count(*) from public.orders where order_id = %s",
                (rollback_plan.order_id,),
            )
            assert_true(
                required_value(cursor.fetchone(), "rollback query returned no row")
                == 0,
                "rollback left a partial order",
            )

            cursor.execute(
                """
                select order_id from public.orders o
                where not exists (
                    select 1 from simulator_control.synthetic_entities s
                    where s.entity_type = 'order' and s.entity_id = o.order_id
                ) order by order_id limit 1
                """
            )
            historical_order = str(
                required_value(cursor.fetchone(), "fixture has no historical order")
            )
        protected_plan = replace(rollback_plan, order_id=historical_order)
        try:
            repository.hard_delete_order("integration-rollback", protected_plan)
        except PermissionError:
            connection.rollback()
        else:
            raise AssertionError("historical seeded order was eligible for deletion")

        replay_config = replace(
            delivered, random_seed=206, start_time=datetime(2030, 1, 1)
        )
        replayed = RunEngine(repository).replay(
            "integration-replay",
            replay_config,
            event_limit=1,
            speed_multiplier=120,
        )
        assert_true(replayed == 1, "replay did not create one inferred lifecycle")

        status = repository.status("integration-delivered")
        required_status = {
            "run_id",
            "random_seed",
            "rate",
            "pending_transitions",
            "run_state",
            "last_committed_source_timestamp",
        }
        assert_true(
            status and required_status <= set(status), "status contract is incomplete"
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                select order_status, count(*) from public.orders
                where order_id in (
                    select entity_id from simulator_control.synthetic_entities
                    where entity_type = 'order'
                ) group by order_status
                """
            )
            statuses = dict(cursor.fetchall())
            cursor.execute(
                "select count(*) from simulator_control.replay_timestamp_mappings"
            )
            mapping_count = int(
                required_value(cursor.fetchone(), "mapping query returned no row")
            )
            cursor.execute("set constraints all immediate")
            cursor.execute(
                """
                select count(*) from public.orders o
                where not exists (
                    select 1 from simulator_control.synthetic_entities s
                    where s.entity_type = 'order' and s.entity_id = o.order_id
                )
                """
            )
            historical_count = int(
                required_value(
                    cursor.fetchone(), "historical count query returned no row"
                )
            )
            cursor.execute(
                """
                select counters from simulator_control.simulation_runs
                where run_id = 'integration-delivered'
                """
            )
            delivered_counters = required_value(
                cursor.fetchone(), "delivered counters query returned no row"
            )
            cursor.execute(
                """
                select counters from simulator_control.simulation_runs
                where run_id = 'integration-delete'
                """
            )
            delete_counters = required_value(
                cursor.fetchone(), "delete counters query returned no row"
            )
        assert_true(statuses.get("delivered", 0) >= 1, "delivered branch missing")
        assert_true(statuses.get("canceled", 0) >= 1, "canceled branch missing")
        assert_true(statuses.get("unavailable", 0) >= 1, "unavailable branch missing")
        assert_true(mapping_count > 0, "replay timestamp mapping missing")
        assert_true(
            historical_count == first_counts["orders"],
            "destructive scenarios changed seeded historical orders",
        )
        assert_true(delivered_counters.get("corrected", 0) > 0, "correction missing")
        assert_true(delete_counters.get("deleted", 0) == 1, "hard delete missing")

        print(
            json.dumps(
                {
                    "event": "oltp_integration_passed",
                    "seed_counts": second_counts,
                    "synthetic_statuses": statuses,
                    "replay_mappings": mapping_count,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
