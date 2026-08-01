"""Command-independent simulator execution loop."""

from __future__ import annotations

import time
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from scripts.simulation.database import SimulatorRepository
from scripts.simulation.domain import (
    SimulationConfig,
    Transition,
    WorkloadPlanner,
    normalize_speed_multiplier,
)


def _scaled_timedelta(value: timedelta, divisor: Decimal) -> timedelta:
    total_microseconds = Decimal(
        (value.days * 86_400 + value.seconds) * 1_000_000 + value.microseconds
    )
    scaled_microseconds = int(
        (total_microseconds / divisor).to_integral_value(rounding=ROUND_HALF_UP)
    )
    return timedelta(microseconds=scaled_microseconds)


def _failure_reason(error: BaseException) -> str:
    return f"{type(error).__name__}: simulator command failed"


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
        last_committed_at = config.start_time
        self.repository.start_run(run_id, "run", config)
        try:
            planner = WorkloadPlanner(config)
            completed = 0
            sequence_number = 0
            while event_limit is None or completed < event_limit:
                if self._finish_if_stop_requested(run_id, last_committed_at):
                    return completed
                plan = planner.plan(sequence_number)
                self.repository.create_lifecycle(run_id, plan)
                last_committed_at = max(last_committed_at, plan.purchase_at)
                for transition in plan.transitions:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.apply_transition(run_id, plan.order_id, transition)
                    last_committed_at = max(
                        last_committed_at,
                        transition.occurred_at,
                    )
                if plan.add_review:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.add_review(run_id, plan)
                    last_committed_at = max(
                        last_committed_at,
                        plan.transitions[-1].occurred_at + timedelta(days=1),
                    )
                if plan.correction:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.apply_correction(run_id, plan)
                    last_committed_at = max(
                        last_committed_at,
                        plan.transitions[-1].occurred_at + timedelta(hours=1),
                    )
                if plan.hard_delete:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.hard_delete_order(run_id, plan)
                    last_committed_at = max(
                        last_committed_at,
                        plan.transitions[-1].occurred_at + timedelta(days=2),
                    )
                completed += 1
                sequence_number += 1
                if self._finish_if_stop_requested(run_id, last_committed_at):
                    return completed
                if pace:
                    time.sleep(1 / config.target_rate)
            finished_at = max(
                planner.logical_time(sequence_number),
                last_committed_at,
            )
            self.repository.finish_run(run_id, "completed", finished_at)
            return completed
        except BaseException as exc:
            self.repository.fail_run(
                run_id,
                last_committed_at,
                _failure_reason(exc),
            )
            raise

    def replay(
        self,
        run_id: str,
        config: SimulationConfig,
        *,
        event_limit: int | None,
        speed_multiplier: Decimal | float | str,
    ) -> int:
        normalized_speed = normalize_speed_multiplier(speed_multiplier)
        candidates = self.repository.replay_candidates(event_limit)
        if not candidates:
            raise ValueError(
                "No seeded terminal order lifecycles are available to replay"
            )
        last_committed_at = config.start_time
        self.repository.start_run(run_id, "replay", config)
        try:
            planner = WorkloadPlanner(config)
            source_base = candidates[0]["order_purchase_timestamp"]
            completed = 0
            for sequence_number, source in enumerate(candidates):
                if self._finish_if_stop_requested(run_id, last_committed_at):
                    return completed
                base_plan = planner.plan(sequence_number)

                def mapped(value: datetime | None, fallback: datetime) -> datetime:
                    if value is None:
                        return fallback
                    return config.start_time + _scaled_timedelta(
                        value - source_base,
                        normalized_speed,
                    )

                purchase_at = mapped(
                    source["order_purchase_timestamp"],
                    config.start_time,
                )
                approved_at = mapped(
                    source["order_approved_at"],
                    purchase_at + timedelta(minutes=2),
                )
                carrier_at = mapped(
                    source["order_delivered_carrier_date"],
                    approved_at + timedelta(hours=12),
                )
                delivered_at = mapped(
                    source["order_delivered_customer_date"],
                    carrier_at + timedelta(days=3),
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
                    run_id,
                    source["order_id"],
                    mappings,
                    normalized_speed,
                )
                if self._finish_if_stop_requested(run_id, last_committed_at):
                    return completed
                self.repository.create_lifecycle(run_id, plan)
                last_committed_at = max(last_committed_at, purchase_at)
                for transition in plan.transitions:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.apply_transition(run_id, plan.order_id, transition)
                    last_committed_at = max(
                        last_committed_at,
                        transition.occurred_at,
                    )
                if plan.add_review:
                    if self._finish_if_stop_requested(run_id, last_committed_at):
                        return completed
                    self.repository.add_review(run_id, plan)
                    last_committed_at = max(
                        last_committed_at,
                        plan.transitions[-1].occurred_at + timedelta(days=1),
                    )
                completed += 1
                if self._finish_if_stop_requested(run_id, last_committed_at):
                    return completed

            finished_at = max(
                planner.logical_time(completed),
                last_committed_at,
            )
            self.repository.finish_run(run_id, "completed", finished_at)
            return completed
        except BaseException as exc:
            self.repository.fail_run(
                run_id,
                last_committed_at,
                _failure_reason(exc),
            )
            raise

    def _finish_if_stop_requested(self, run_id: str, boundary_at: datetime) -> bool:
        if not self.repository.stop_requested(run_id):
            return False
        self.repository.finish_run(run_id, "stopped", boundary_at)
        return True


def deterministic_run_id(command: str, seed: int, started_at: datetime) -> str:
    return f"{command}-{seed}-{started_at.strftime('%Y%m%dT%H%M%S')}"
