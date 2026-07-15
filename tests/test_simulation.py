from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock

from scripts.simulation.domain import SimulationConfig, WorkloadPlanner
from scripts.simulation.engine import RunEngine
from scripts.simulation.seeding import SEED_SPECS


class WorkloadPlannerTests(unittest.TestCase):
    def config(self, seed: int, **overrides: float) -> SimulationConfig:
        values = {
            "random_seed": seed,
            "start_time": datetime(2026, 1, 1),
            "target_rate": 5.0,
        }
        values.update(overrides)
        return SimulationConfig(**values)  # type: ignore[arg-type]

    def test_same_seed_and_configuration_produce_identical_sequence(self) -> None:
        first = WorkloadPlanner(self.config(42))
        second = WorkloadPlanner(self.config(42))
        self.assertEqual(
            [first.plan(i) for i in range(20)], [second.plan(i) for i in range(20)]
        )

    def test_different_seeds_change_decisions_and_identifiers(self) -> None:
        first = WorkloadPlanner(self.config(1)).plan(0)
        second = WorkloadPlanner(self.config(2)).plan(0)
        self.assertNotEqual(first.order_id, second.order_id)
        self.assertNotEqual(first, second)

    def test_delivered_branch_has_all_transitions_review_correction_and_delete(
        self,
    ) -> None:
        planner = WorkloadPlanner(
            self.config(
                5,
                cancel_probability=0,
                unavailable_probability=0,
                review_probability=1,
                correction_probability=1,
                hard_delete_probability=1,
            )
        )
        plan = planner.plan(0)
        self.assertEqual(plan.outcome, "delivered")
        self.assertEqual(
            [item.status for item in plan.transitions],
            ["approved", "shipped", "delivered"],
        )
        self.assertTrue(plan.add_review)
        self.assertIsNotNone(plan.correction)
        self.assertTrue(plan.hard_delete)

    def test_canceled_branch(self) -> None:
        plan = WorkloadPlanner(
            self.config(7, cancel_probability=1, unavailable_probability=0)
        ).plan(0)
        self.assertEqual(plan.outcome, "canceled")
        self.assertEqual([item.status for item in plan.transitions], ["canceled"])
        self.assertFalse(plan.add_review)

    def test_unavailable_branch(self) -> None:
        plan = WorkloadPlanner(
            self.config(7, cancel_probability=0, unavailable_probability=1)
        ).plan(0)
        self.assertEqual(plan.outcome, "unavailable")
        self.assertEqual([item.status for item in plan.transitions], ["unavailable"])

    def test_logical_clock_uses_rate_not_wall_clock(self) -> None:
        planner = WorkloadPlanner(self.config(11))
        self.assertEqual(
            (planner.plan(5).purchase_at - planner.plan(0).purchase_at).total_seconds(),
            1,
        )


class SourceKeyContractTests(unittest.TestCase):
    def test_three_required_composite_keys(self) -> None:
        keys = {spec.entity_name: spec.key_columns for spec in SEED_SPECS}
        self.assertEqual(keys["order_items"], ("order_id", "order_item_id"))
        self.assertEqual(keys["order_payments"], ("order_id", "payment_sequential"))
        self.assertEqual(keys["order_reviews"], ("review_id", "order_id"))

    def test_geolocation_uses_generated_database_key(self) -> None:
        keys = {spec.entity_name: spec.key_columns for spec in SEED_SPECS}
        self.assertEqual(keys["geolocation"], ())


class RunEngineTests(unittest.TestCase):
    def test_graceful_stop_is_observed_before_the_next_transaction(self) -> None:
        repository = MagicMock()
        repository.stop_requested.return_value = True
        config = SimulationConfig(random_seed=10, start_time=datetime(2026, 1, 1))

        completed = RunEngine(repository).run(  # type: ignore[arg-type]
            "stop-boundary", config, event_limit=10, pace=False
        )

        self.assertEqual(completed, 0)
        repository.create_lifecycle.assert_not_called()
        repository.finish_run.assert_called_once_with(
            "stop-boundary", "stopped", config.start_time
        )


if __name__ == "__main__":
    unittest.main()
