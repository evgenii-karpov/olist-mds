"""Pure deterministic workload decisions and logical-clock behavior."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Literal

Outcome = Literal["delivered", "canceled", "unavailable"]
Correction = Literal["customer", "product"]


@dataclass(frozen=True)
class SimulationConfig:
    random_seed: int
    start_time: datetime
    target_rate: float = 5.0
    cancel_probability: float = 0.08
    unavailable_probability: float = 0.02
    review_probability: float = 0.35
    correction_probability: float = 0.05
    hard_delete_probability: float = 0.01

    def __post_init__(self) -> None:
        if self.target_rate <= 0:
            raise ValueError("target_rate must be greater than zero")
        probabilities = {
            "cancel_probability": self.cancel_probability,
            "unavailable_probability": self.unavailable_probability,
            "review_probability": self.review_probability,
            "correction_probability": self.correction_probability,
            "hard_delete_probability": self.hard_delete_probability,
        }
        for name, value in probabilities.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between zero and one")
        if self.cancel_probability + self.unavailable_probability > 1:
            raise ValueError("cancel and unavailable probabilities cannot exceed one")

    def as_dict(self) -> dict[str, object]:
        return {
            "random_seed": self.random_seed,
            "start_time": self.start_time.isoformat(),
            "target_rate": self.target_rate,
            "cancel_probability": self.cancel_probability,
            "unavailable_probability": self.unavailable_probability,
            "review_probability": self.review_probability,
            "correction_probability": self.correction_probability,
            "hard_delete_probability": self.hard_delete_probability,
        }


@dataclass(frozen=True)
class Transition:
    sequence_number: int
    status: str
    occurred_at: datetime


@dataclass(frozen=True)
class LifecyclePlan:
    sequence_number: int
    customer_id: str
    customer_unique_id: str
    product_id: str
    seller_id: str
    order_id: str
    review_id: str
    purchase_at: datetime
    estimated_delivery_at: datetime
    price: Decimal
    freight_value: Decimal
    payment_type: str
    payment_installments: int
    outcome: Outcome
    transitions: tuple[Transition, ...]
    add_review: bool
    correction: Correction | None
    hard_delete: bool


class WorkloadPlanner:
    """Generate decisions whose output is independent of wall-clock scheduling."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._random = random.Random(config.random_seed)

    def stable_id(self, entity_type: str, sequence_number: int) -> str:
        material = f"{self.config.random_seed}:{entity_type}:{sequence_number}"
        digest = hashlib.sha256(material.encode()).hexdigest()[:28]
        return f"sim_{digest}"

    def logical_time(self, sequence_number: int) -> datetime:
        interval_seconds = 1 / self.config.target_rate
        return self.config.start_time + timedelta(
            seconds=sequence_number * interval_seconds
        )

    def plan(self, sequence_number: int) -> LifecyclePlan:
        purchase_at = self.logical_time(sequence_number)
        outcome_roll = self._random.random()
        if outcome_roll < self.config.cancel_probability:
            outcome: Outcome = "canceled"
        elif outcome_roll < (
            self.config.cancel_probability + self.config.unavailable_probability
        ):
            outcome = "unavailable"
        else:
            outcome = "delivered"

        approved_at = purchase_at + timedelta(minutes=2)
        if outcome == "delivered":
            transitions = (
                Transition(1, "approved", approved_at),
                Transition(2, "shipped", approved_at + timedelta(hours=12)),
                Transition(3, "delivered", approved_at + timedelta(days=3)),
            )
        elif outcome == "unavailable":
            transitions = (Transition(1, "unavailable", approved_at),)
        else:
            transitions = (Transition(1, "canceled", approved_at),)

        price = Decimal(self._random.randrange(1000, 50001)) / Decimal(100)
        freight = Decimal(self._random.randrange(500, 5001)) / Decimal(100)
        payment_type = self._random.choice(
            ("credit_card", "boleto", "voucher", "debit_card")
        )
        installments = (
            self._random.randint(1, 10) if payment_type == "credit_card" else 1
        )
        add_review = (
            outcome == "delivered"
            and self._random.random() < self.config.review_probability
        )
        correction_roll = self._random.random()
        correction: Correction | None = None
        if correction_roll < self.config.correction_probability:
            correction = self._random.choice(("customer", "product"))
        hard_delete = self._random.random() < self.config.hard_delete_probability

        return LifecyclePlan(
            sequence_number=sequence_number,
            customer_id=self.stable_id("customer", sequence_number),
            customer_unique_id=self.stable_id("customer_unique", sequence_number),
            product_id=self.stable_id("product", sequence_number),
            seller_id=self.stable_id("seller", sequence_number),
            order_id=self.stable_id("order", sequence_number),
            review_id=self.stable_id("review", sequence_number),
            purchase_at=purchase_at,
            estimated_delivery_at=purchase_at + timedelta(days=7),
            price=price.quantize(Decimal("0.01")),
            freight_value=freight.quantize(Decimal("0.01")),
            payment_type=payment_type,
            payment_installments=installments,
            outcome=outcome,
            transitions=transitions,
            add_review=add_review,
            correction=correction,
            hard_delete=hard_delete,
        )
