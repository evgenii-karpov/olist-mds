"""Transactional PostgreSQL adapter for simulator commands."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection

from scripts.simulation.domain import LifecyclePlan, SimulationConfig, Transition


@dataclass(frozen=True)
class DatabaseSettings:
    host: str = "localhost"
    port: int = 5433
    database: str = "olist_oltp"
    user: str = "olist_simulator"
    password: str = ""

    @classmethod
    def with_password_file(
        cls,
        *,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str | None,
        password_file: str | None,
    ) -> DatabaseSettings:
        resolved = password or ""
        if not resolved and password_file:
            resolved = Path(password_file).read_text(encoding="utf-8").strip()
        return cls(
            host=host, port=port, database=database, user=user, password=resolved
        )


def connect(settings: DatabaseSettings) -> PgConnection:
    return psycopg2.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
    )


class SimulatorRepository:
    def __init__(self, connection: PgConnection) -> None:
        self.connection = connection

    def start_run(self, run_id: str, command: str, config: SimulationConfig) -> None:
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                insert into simulator_control.simulation_runs (
                    run_id, command, random_seed, target_rate, configuration,
                    state, started_at, heartbeat_at
                ) values (%s, %s, %s, %s, %s::jsonb, 'running', %s, %s)
                on conflict (run_id) do update set
                    command = excluded.command,
                    random_seed = excluded.random_seed,
                    target_rate = excluded.target_rate,
                    configuration = excluded.configuration,
                    state = 'running',
                    heartbeat_at = excluded.heartbeat_at,
                    stop_requested_at = null,
                    finished_at = null,
                    error_message = null
                """,
                (
                    run_id,
                    command,
                    config.random_seed,
                    config.target_rate,
                    json.dumps(config.as_dict(), sort_keys=True),
                    config.start_time,
                    config.start_time,
                ),
            )

    def stop_requested(self, run_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                select state = 'stop_requested'
                from simulator_control.simulation_runs where run_id = %s
                """,
                (run_id,),
            )
            row = cursor.fetchone()
        return bool(row and row[0])

    def request_stop(self, run_id: str, requested_at: datetime) -> bool:
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                update simulator_control.simulation_runs
                set state = 'stop_requested', stop_requested_at = %s,
                    heartbeat_at = %s
                where run_id = %s and state in ('starting', 'running')
                """,
                (requested_at, requested_at, run_id),
            )
            return cursor.rowcount == 1

    def create_lifecycle(
        self,
        run_id: str,
        plan: LifecyclePlan,
        *,
        inject_failure_after_order: bool = False,
    ) -> None:
        """Create the order graph atomically and schedule later transactions."""
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.product_category_translation values
                    ('simulated', 'simulated')
                on conflict (product_category_name) do nothing
                """
            )
            cursor.execute(
                """
                insert into public.customers values (%s, %s, '01001', 'sao paulo', 'SP')
                on conflict (customer_id) do nothing
                """,
                (plan.customer_id, plan.customer_unique_id),
            )
            cursor.execute(
                """
                insert into public.products values
                    (%s, 'simulated', 20, 100, 1, 500, 20, 10, 15)
                on conflict (product_id) do nothing
                """,
                (plan.product_id,),
            )
            cursor.execute(
                """
                insert into public.sellers values (%s, '01001', 'sao paulo', 'SP')
                on conflict (seller_id) do nothing
                """,
                (plan.seller_id,),
            )
            cursor.execute(
                """
                insert into public.orders values
                    (%s, %s, 'created', %s, null, null, null, %s)
                """,
                (
                    plan.order_id,
                    plan.customer_id,
                    plan.purchase_at,
                    plan.estimated_delivery_at,
                ),
            )
            if inject_failure_after_order:
                raise RuntimeError("injected failure after order insert")
            cursor.execute(
                """
                insert into public.order_items values (%s, 1, %s, %s, %s, %s, %s)
                """,
                (
                    plan.order_id,
                    plan.product_id,
                    plan.seller_id,
                    plan.purchase_at + timedelta(days=1),
                    plan.price,
                    plan.freight_value,
                ),
            )
            cursor.execute(
                """
                insert into public.order_payments values (%s, 1, %s, %s, %s)
                """,
                (
                    plan.order_id,
                    plan.payment_type,
                    plan.payment_installments,
                    plan.price + plan.freight_value,
                ),
            )
            ids = (
                ("customer", plan.customer_id),
                ("product", plan.product_id),
                ("seller", plan.seller_id),
                ("order", plan.order_id),
            )
            for entity_type, entity_id in ids:
                cursor.execute(
                    """
                    insert into simulator_control.generated_ids values (%s, %s, %s, %s)
                    on conflict do nothing
                    """,
                    (run_id, entity_type, plan.sequence_number, entity_id),
                )
                cursor.execute(
                    """
                    insert into simulator_control.synthetic_entities values
                        (%s, %s, %s, %s)
                    on conflict do nothing
                    """,
                    (entity_type, entity_id, run_id, plan.purchase_at),
                )
            for transition in plan.transitions:
                cursor.execute(
                    """
                    insert into simulator_control.pending_transitions (
                        transition_id, run_id, order_id, transition_type,
                        due_at, sequence_number, payload
                    ) values (%s, %s, %s, 'order_status', %s, %s, %s::jsonb)
                    on conflict (transition_id) do nothing
                    """,
                    (
                        f"{plan.order_id}:{transition.sequence_number}",
                        run_id,
                        plan.order_id,
                        transition.occurred_at,
                        transition.sequence_number,
                        json.dumps({"status": transition.status}),
                    ),
                )
            self._touch(cursor, run_id, plan.purchase_at, {"created": 1})

    def apply_transition(
        self, run_id: str, order_id: str, transition: Transition
    ) -> None:
        assignments = {
            "approved": "order_status = %s, order_approved_at = %s",
            "shipped": "order_status = %s, order_delivered_carrier_date = %s",
            "delivered": "order_status = %s, order_delivered_customer_date = %s",
            "canceled": "order_status = %s",
            "unavailable": "order_status = %s",
        }
        clause = assignments[transition.status]
        parameters: tuple[Any, ...]
        if transition.status in {"approved", "shipped", "delivered"}:
            parameters = (transition.status, transition.occurred_at, order_id)
        else:
            parameters = (transition.status, order_id)
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                f"update public.orders set {clause} where order_id = %s", parameters
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Order not found for transition: {order_id}")
            cursor.execute(
                """
                update simulator_control.pending_transitions
                set state = 'applied', applied_at = %s
                where run_id = %s and order_id = %s and sequence_number = %s
                """,
                (transition.occurred_at, run_id, order_id, transition.sequence_number),
            )
            self._touch(cursor, run_id, transition.occurred_at, {transition.status: 1})

    def add_review(self, run_id: str, plan: LifecyclePlan) -> None:
        delivered_at = plan.transitions[-1].occurred_at
        created_at = delivered_at + timedelta(days=1)
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                insert into public.order_reviews values
                    (%s, %s, 5, 'deterministic review',
                     'generated by the deterministic simulator', %s, %s)
                """,
                (
                    plan.review_id,
                    plan.order_id,
                    created_at,
                    created_at + timedelta(hours=1),
                ),
            )
            cursor.execute(
                """
                insert into simulator_control.generated_ids values (%s, 'review', %s, %s)
                on conflict do nothing
                """,
                (run_id, plan.sequence_number, plan.review_id),
            )
            cursor.execute(
                """
                insert into simulator_control.synthetic_entities values
                    ('review', %s, %s, %s) on conflict do nothing
                """,
                (plan.review_id, run_id, created_at),
            )
            self._touch(cursor, run_id, created_at, {"reviewed": 1})

    def apply_correction(self, run_id: str, plan: LifecyclePlan) -> None:
        corrected_at = plan.transitions[-1].occurred_at + timedelta(hours=1)
        with self.connection, self.connection.cursor() as cursor:
            if plan.correction == "customer":
                cursor.execute(
                    """
                    update public.customers set customer_city = 'rio de janeiro',
                        customer_state = 'RJ' where customer_id = %s
                    """,
                    (plan.customer_id,),
                )
            elif plan.correction == "product":
                cursor.execute(
                    """
                    update public.products set product_weight_g = product_weight_g + 1
                    where product_id = %s
                    """,
                    (plan.product_id,),
                )
            else:
                return
            self._touch(cursor, run_id, corrected_at, {"corrected": 1})

    def hard_delete_order(self, run_id: str, plan: LifecyclePlan) -> None:
        deleted_at = plan.transitions[-1].occurred_at + timedelta(days=2)
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                select 1 from simulator_control.synthetic_entities
                where entity_type = 'order' and entity_id = %s and run_id = %s
                for update
                """,
                (plan.order_id, run_id),
            )
            if cursor.fetchone() is None:
                raise PermissionError(
                    "hard delete is restricted to simulator-owned orders"
                )
            cursor.execute(
                "delete from public.order_reviews where order_id = %s", (plan.order_id,)
            )
            cursor.execute(
                "delete from public.order_payments where order_id = %s",
                (plan.order_id,),
            )
            cursor.execute(
                "delete from public.order_items where order_id = %s", (plan.order_id,)
            )
            cursor.execute(
                "delete from public.orders where order_id = %s", (plan.order_id,)
            )
            cursor.execute(
                """
                delete from simulator_control.pending_transitions
                where run_id = %s and order_id = %s
                """,
                (run_id, plan.order_id),
            )
            self._touch(cursor, run_id, deleted_at, {"deleted": 1})

    def finish_run(self, run_id: str, state: str, finished_at: datetime) -> None:
        with self.connection, self.connection.cursor() as cursor:
            cursor.execute(
                """
                update simulator_control.simulation_runs
                set state = %s, heartbeat_at = %s, finished_at = %s
                where run_id = %s
                """,
                (state, finished_at, finished_at, run_id),
            )

    def status(self, run_id: str | None = None) -> dict[str, Any] | None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                select r.run_id, r.random_seed, r.target_rate, r.state,
                       r.last_committed_source_timestamp, r.counters,
                       count(t.transition_id) filter (where t.state = 'pending')
                from simulator_control.simulation_runs r
                left join simulator_control.pending_transitions t on t.run_id = r.run_id
                where (%s is null or r.run_id = %s)
                group by r.run_id
                order by r.started_at desc limit 1
                """,
                (run_id, run_id),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return {
            "run_id": row[0],
            "random_seed": row[1],
            "rate": float(row[2]),
            "run_state": row[3],
            "last_committed_source_timestamp": row[4].isoformat() if row[4] else None,
            "counters": row[5],
            "pending_transitions": row[6],
        }

    def replay_candidates(self, event_limit: int | None) -> list[dict[str, Any]]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                select o.order_id, o.order_status, o.order_purchase_timestamp,
                       o.order_approved_at, o.order_delivered_carrier_date,
                       o.order_delivered_customer_date,
                       o.order_estimated_delivery_date,
                       exists (
                           select 1 from public.order_reviews r
                           where r.order_id = o.order_id
                       ) as has_review
                from public.orders o
                where o.order_status in ('delivered', 'canceled', 'unavailable')
                  and not exists (
                      select 1 from simulator_control.synthetic_entities s
                      where s.entity_type = 'order' and s.entity_id = o.order_id
                  )
                order by o.order_purchase_timestamp, o.order_id
                limit %s
                """,
                (event_limit,),
            )
            if cursor.description is None:
                raise RuntimeError("Replay candidate query returned no description")
            columns = [description.name for description in cursor.description]
            return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    def record_replay_mappings(
        self,
        run_id: str,
        source_order_id: str,
        mappings: list[tuple[datetime, datetime]],
        speed_multiplier: float,
    ) -> None:
        with self.connection, self.connection.cursor() as cursor:
            for source_timestamp, replay_timestamp in mappings:
                cursor.execute(
                    """
                    insert into simulator_control.replay_timestamp_mappings (
                        run_id, entity_type, source_entity_id, source_timestamp,
                        replay_timestamp, speed_multiplier
                    ) values (%s, 'order', %s, %s, %s, %s)
                    on conflict do nothing
                    """,
                    (
                        run_id,
                        source_order_id,
                        source_timestamp,
                        replay_timestamp,
                        speed_multiplier,
                    ),
                )

    @staticmethod
    def _touch(
        cursor: Any, run_id: str, source_at: datetime, increments: dict[str, int]
    ) -> None:
        cursor.execute(
            """
            select counters from simulator_control.simulation_runs
            where run_id = %s for update
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        counters = dict(row[0] if row else {})
        for name, increment in increments.items():
            counters[name] = int(counters.get(name, 0)) + increment
        cursor.execute(
            """
            update simulator_control.simulation_runs
            set heartbeat_at = %s,
                last_committed_source_timestamp = %s,
                counters = %s::jsonb
            where run_id = %s
            """,
            (source_at, source_at, json.dumps(counters, sort_keys=True), run_id),
        )
