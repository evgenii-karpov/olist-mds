"""Command-independent simulator execution loop."""

from __future__ import annotations

import time
from dataclasses import replace
from datetime import datetime, timedelta

from scripts.simulation.database import SimulatorRepository
from scripts.simulation.domain import SimulationConfig, Transition, WorkloadPlanner


class RunEngine:
    def __init__(self, repository: SimulatorRepository) -> None:
        self.repository = repository

    def run(
        self,
        run_id: str,
        config: SimulationConfig,
        *,
        event_limit: int | None,
        pace: bool = True,
    ) -> int:
        if event_limit is not None and event_limit < 1:
            raise ValueError("event_limit must be positive")
        self.repository.start_run(run_id, "run", config)
        planner = WorkloadPlanner(config)
        completed = 0
        sequence_number = 0
        while event_limit is None or completed < event_limit:
            if self.repository.stop_requested(run_id):
                self.repository.finish_run(
                    run_id, "stopped", planner.logical_time(sequence_number)
                )
                return completed
            plan = planner.plan(sequence_number)
            self.repository.create_lifecycle(run_id, plan)
            for transition in plan.transitions:
                self.repository.apply_transition(run_id, plan.order_id, transition)
            if plan.add_review:
                self.repository.add_review(run_id, plan)
            if plan.correction:
                self.repository.apply_correction(run_id, plan)
            if plan.hard_delete:
                self.repository.hard_delete_order(run_id, plan)
            completed += 1
            sequence_number += 1
            if pace:
                time.sleep(1 / config.target_rate)
        finished_at = planner.logical_time(sequence_number)
        self.repository.finish_run(run_id, "completed", finished_at)
        return completed

    def replay(
        self,
        run_id: str,
        config: SimulationConfig,
        *,
        event_limit: int | None,
        speed_multiplier: float,
    ) -> int:
        if speed_multiplier <= 0:
            raise ValueError("speed_multiplier must be greater than zero")
        candidates = self.repository.replay_candidates(event_limit)
        if not candidates:
            raise ValueError(
                "No seeded terminal order lifecycles are available to replay"
            )
        self.repository.start_run(run_id, "replay", config)
        planner = WorkloadPlanner(config)
        source_base = candidates[0]["order_purchase_timestamp"]

        for sequence_number, source in enumerate(candidates):
            base_plan = planner.plan(sequence_number)

            def mapped(value: datetime | None, fallback: datetime) -> datetime:
                if value is None:
                    return fallback
                return config.start_time + (value - source_base) / speed_multiplier

            purchase_at = mapped(source["order_purchase_timestamp"], config.start_time)
            approved_at = mapped(
                source["order_approved_at"], purchase_at + timedelta(minutes=2)
            )
            carrier_at = mapped(
                source["order_delivered_carrier_date"],
                approved_at + timedelta(hours=12),
            )
            delivered_at = mapped(
                source["order_delivered_customer_date"], carrier_at + timedelta(days=3)
            )
            status = source["order_status"]
            if status == "delivered":
                transitions = (
                    Transition(1, "approved", approved_at),
                    Transition(2, "shipped", carrier_at),
                    Transition(3, "delivered", delivered_at),
                )
            else:
                transitions = (Transition(1, status, approved_at),)
            plan = replace(
                base_plan,
                purchase_at=purchase_at,
                estimated_delivery_at=mapped(
                    source["order_estimated_delivery_date"],
                    purchase_at + timedelta(days=7),
                ),
                outcome=status,
                transitions=transitions,
                add_review=status == "delivered" and bool(source["has_review"]),
                correction=None,
                hard_delete=False,
            )
            mappings = []
            for value in (
                source["order_purchase_timestamp"],
                source["order_approved_at"],
                source["order_delivered_carrier_date"],
                source["order_delivered_customer_date"],
                source["order_estimated_delivery_date"],
            ):
                if value is not None:
                    mappings.append((value, mapped(value, purchase_at)))
            self.repository.record_replay_mappings(
                run_id, source["order_id"], mappings, speed_multiplier
            )
            self.repository.create_lifecycle(run_id, plan)
            for transition in plan.transitions:
                self.repository.apply_transition(run_id, plan.order_id, transition)
            if plan.add_review:
                self.repository.add_review(run_id, plan)

        self.repository.finish_run(
            run_id, "completed", planner.logical_time(len(candidates))
        )
        return len(candidates)


def deterministic_run_id(command: str, seed: int, started_at: datetime) -> str:
    return f"{command}-{seed}-{started_at.strftime('%Y%m%dT%H%M%S')}"
