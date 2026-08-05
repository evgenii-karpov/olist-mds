"""Transactional MySQL adapter for deterministic simulator commands."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from importlib import import_module
from pathlib import Path
from typing import Any

from scripts.simulation.domain import LifecyclePlan, SimulationConfig, Transition

BUSINESS_DATABASE = "olist_oltp"
CONTROL_DATABASE = "olist_simulator"


@dataclass(frozen=True)
class DatabaseSettings:
    password_file: Path | str
    host: str = "localhost"
    port: int = 3306
    database: str = BUSINESS_DATABASE
    user: str = "olist_simulator"
    connect_timeout: int = 10

    def __post_init__(self) -> None:
        path = _password_path(self.password_file)
        _read_password_file(path)
        object.__setattr__(self, "password_file", path)


def _password_path(value: Path | str | None) -> Path:
    if value is None or not str(value).strip():
        raise ValueError(
            "MYSQL_PASSWORD_FILE or --password-file must name a readable secret file"
        )
    return Path(value)


def _read_password_file(path: Path | str | None) -> str:
    resolved_path = _password_path(path)
    try:
        raw = resolved_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"MySQL password file is not readable: {resolved_path}"
        ) from exc

    if raw.endswith("\r\n"):
        password = raw[:-2]
    elif raw.endswith(("\r", "\n")):
        password = raw[:-1]
    else:
        password = raw

    if "\r" in password or "\n" in password:
        raise ValueError("MySQL password file must contain exactly one line")
    if not password or not password.strip():
        raise ValueError("MySQL password file must contain a non-empty password")
    return password


def connect(settings: DatabaseSettings) -> Any:
    """Open a UTC MySQL session without importing the driver at module import."""
    try:
        connector = import_module("mysql.connector")
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency handoff guard
        raise RuntimeError(
            "mysql-connector-python is required for simulator database commands"
        ) from exc

    password = _read_password_file(settings.password_file)
    return connector.connect(
        host=settings.host,
        port=settings.port,
        database=settings.database,
        user=settings.user,
        password=password,
        autocommit=True,
        charset="utf8mb4",
        collation="utf8mb4_0900_bin",
        time_zone="+00:00",
        connection_timeout=settings.connect_timeout,
    )


def _json_object(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if isinstance(value, str):
        decoded = json.loads(value)
        if not isinstance(decoded, dict):
            raise TypeError("Expected a JSON object from simulator control state")
        return decoded
    raise TypeError(f"Unsupported JSON value returned by MySQL: {type(value).__name__}")


class SimulatorRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        """Commit one explicit unit or roll the complete unit back on failure."""
        cursor: Any | None = None
        self.connection.start_transaction()
        try:
            cursor = self.connection.cursor()
            yield cursor
        except BaseException:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()
        finally:
            if cursor is not None:
                cursor.close()

    @contextmanager
    def _read_cursor(self) -> Iterator[Any]:
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def start_run(self, run_id: str, command: str, config: SimulationConfig) -> None:
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO olist_simulator.simulation_runs (
                    run_id, command, random_seed, target_rate, configuration,
                    state, started_at, heartbeat_at
                ) VALUES (%s, %s, %s, %s, %s, 'running', %s, %s) AS new
                ON DUPLICATE KEY UPDATE
                    command = new.command,
                    random_seed = new.random_seed,
                    target_rate = new.target_rate,
                    configuration = new.configuration,
                    state = 'running',
                    heartbeat_at = new.heartbeat_at,
                    stop_requested_at = NULL,
                    finished_at = NULL,
                    error_message = NULL
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
        with self._read_cursor() as cursor:
            cursor.execute(
                """
                SELECT state = 'stop_requested'
                FROM olist_simulator.simulation_runs
                WHERE run_id = %s
                """,
                (run_id,),
            )
            row = cursor.fetchone()
        return bool(row and row[0])

    def request_stop(self, run_id: str, requested_at: datetime) -> bool:
        with self.transaction() as cursor:
            cursor.execute(
                """
                UPDATE olist_simulator.simulation_runs
                SET state = 'stop_requested',
                    stop_requested_at = %s,
                    heartbeat_at = %s
                WHERE run_id = %s
                  AND state IN ('starting', 'running')
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
        """Create one order graph atomically and schedule later transactions."""
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT IGNORE INTO olist_oltp.product_category_translation (
                    product_category_name, product_category_name_english
                ) VALUES ('simulated', 'simulated')
                """
            )
            cursor.execute(
                """
                INSERT IGNORE INTO olist_oltp.customers (
                    customer_id, customer_unique_id, customer_zip_code_prefix,
                    customer_city, customer_state
                ) VALUES (%s, %s, '01001', 'sao paulo', 'SP')
                """,
                (plan.customer_id, plan.customer_unique_id),
            )
            cursor.execute(
                """
                INSERT IGNORE INTO olist_oltp.products (
                    product_id, product_category_name, product_name_lenght,
                    product_description_lenght, product_photos_qty,
                    product_weight_g, product_length_cm, product_height_cm,
                    product_width_cm
                ) VALUES (%s, 'simulated', 20, 100, 1, 500, 20, 10, 15)
                """,
                (plan.product_id,),
            )
            cursor.execute(
                """
                INSERT IGNORE INTO olist_oltp.sellers (
                    seller_id, seller_zip_code_prefix, seller_city, seller_state
                ) VALUES (%s, '01001', 'sao paulo', 'SP')
                """,
                (plan.seller_id,),
            )
            cursor.execute(
                """
                INSERT INTO olist_oltp.orders (
                    order_id, customer_id, order_status,
                    order_purchase_timestamp, order_approved_at,
                    order_delivered_carrier_date, order_delivered_customer_date,
                    order_estimated_delivery_date
                ) VALUES (%s, %s, 'created', %s, NULL, NULL, NULL, %s)
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
                INSERT INTO olist_oltp.order_items (
                    order_id, order_item_id, product_id, seller_id,
                    shipping_limit_date, price, freight_value
                ) VALUES (%s, 1, %s, %s, %s, %s, %s)
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
                INSERT INTO olist_oltp.order_payments (
                    order_id, payment_sequential, payment_type,
                    payment_installments, payment_value
                ) VALUES (%s, 1, %s, %s, %s)
                """,
                (
                    plan.order_id,
                    plan.payment_type,
                    plan.payment_installments,
                    plan.price + plan.freight_value,
                ),
            )
            identifiers = (
                ("customer", plan.customer_id),
                ("product", plan.product_id),
                ("seller", plan.seller_id),
                ("order", plan.order_id),
            )
            for entity_type, entity_id in identifiers:
                cursor.execute(
                    """
                    INSERT IGNORE INTO olist_simulator.generated_ids (
                        run_id, entity_type, sequence_number, entity_id
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (run_id, entity_type, plan.sequence_number, entity_id),
                )
                cursor.execute(
                    """
                    INSERT IGNORE INTO olist_simulator.synthetic_entities (
                        entity_type, entity_id, run_id, created_at
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (entity_type, entity_id, run_id, plan.purchase_at),
                )
            for transition in plan.transitions:
                cursor.execute(
                    """
                    INSERT IGNORE INTO olist_simulator.pending_transitions (
                        transition_id, run_id, order_id, transition_type,
                        due_at, sequence_number, payload
                    ) VALUES (%s, %s, %s, 'order_status', %s, %s, %s)
                    """,
                    (
                        f"{plan.order_id}:{transition.sequence_number}",
                        run_id,
                        plan.order_id,
                        transition.occurred_at,
                        transition.sequence_number,
                        json.dumps({"status": transition.status}, sort_keys=True),
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

        with self.transaction() as cursor:
            cursor.execute(
                f"UPDATE olist_oltp.orders SET {clause} WHERE order_id = %s",
                parameters,
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Order not found for transition: {order_id}")
            cursor.execute(
                """
                UPDATE olist_simulator.pending_transitions
                SET state = 'applied', applied_at = %s
                WHERE run_id = %s
                  AND order_id = %s
                  AND sequence_number = %s
                """,
                (transition.occurred_at, run_id, order_id, transition.sequence_number),
            )
            self._touch(cursor, run_id, transition.occurred_at, {transition.status: 1})

    def add_review(self, run_id: str, plan: LifecyclePlan) -> None:
        delivered_at = plan.transitions[-1].occurred_at
        created_at = delivered_at + timedelta(days=1)
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO olist_oltp.order_reviews (
                    review_id, order_id, review_score, review_comment_title,
                    review_comment_message, review_creation_date,
                    review_answer_timestamp
                ) VALUES (
                    %s, %s, 5, 'deterministic review',
                    'generated by the deterministic simulator', %s, %s
                )
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
                INSERT IGNORE INTO olist_simulator.generated_ids (
                    run_id, entity_type, sequence_number, entity_id
                ) VALUES (%s, 'review', %s, %s)
                """,
                (run_id, plan.sequence_number, plan.review_id),
            )
            cursor.execute(
                """
                INSERT IGNORE INTO olist_simulator.synthetic_entities (
                    entity_type, entity_id, run_id, created_at
                ) VALUES ('review', %s, %s, %s)
                """,
                (plan.review_id, run_id, created_at),
            )
            self._touch(cursor, run_id, created_at, {"reviewed": 1})

    def apply_correction(self, run_id: str, plan: LifecyclePlan) -> None:
        corrected_at = plan.transitions[-1].occurred_at + timedelta(hours=1)
        if plan.correction is None:
            return
        with self.transaction() as cursor:
            if plan.correction == "customer":
                cursor.execute(
                    """
                    UPDATE olist_oltp.customers
                    SET customer_city = 'rio de janeiro', customer_state = 'RJ'
                    WHERE customer_id = %s
                    """,
                    (plan.customer_id,),
                )
            elif plan.correction == "product":
                cursor.execute(
                    """
                    UPDATE olist_oltp.products
                    SET product_weight_g = product_weight_g + 1
                    WHERE product_id = %s
                    """,
                    (plan.product_id,),
                )
            else:  # pragma: no cover - guarded by the domain type
                raise ValueError(f"Unsupported correction: {plan.correction}")
            self._touch(cursor, run_id, corrected_at, {"corrected": 1})

    def hard_delete_order(self, run_id: str, plan: LifecyclePlan) -> None:
        deleted_at = plan.transitions[-1].occurred_at + timedelta(days=2)
        with self.transaction() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM olist_simulator.synthetic_entities
                WHERE entity_type = 'order'
                  AND entity_id = %s
                  AND run_id = %s
                FOR UPDATE
                """,
                (plan.order_id, run_id),
            )
            if cursor.fetchone() is None:
                raise PermissionError(
                    "hard delete is restricted to simulator-owned orders"
                )
            cursor.execute(
                "DELETE FROM olist_oltp.order_reviews WHERE order_id = %s",
                (plan.order_id,),
            )
            cursor.execute(
                "DELETE FROM olist_oltp.order_payments WHERE order_id = %s",
                (plan.order_id,),
            )
            cursor.execute(
                "DELETE FROM olist_oltp.order_items WHERE order_id = %s",
                (plan.order_id,),
            )
            cursor.execute(
                "DELETE FROM olist_oltp.orders WHERE order_id = %s",
                (plan.order_id,),
            )
            cursor.execute(
                """
                DELETE FROM olist_simulator.pending_transitions
                WHERE run_id = %s AND order_id = %s
                """,
                (run_id, plan.order_id),
            )
            self._touch(cursor, run_id, deleted_at, {"deleted": 1})

    def finish_run(self, run_id: str, state: str, finished_at: datetime) -> None:
        with self.transaction() as cursor:
            cursor.execute(
                """
                UPDATE olist_simulator.simulation_runs
                SET state = %s,
                    heartbeat_at = GREATEST(
                        %s,
                        COALESCE(last_committed_source_timestamp, %s)
                    ),
                    finished_at = GREATEST(
                        %s,
                        COALESCE(last_committed_source_timestamp, %s)
                    ),
                    error_message = NULL
                WHERE run_id = %s
                """,
                (
                    state,
                    finished_at,
                    finished_at,
                    finished_at,
                    finished_at,
                    run_id,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Simulator run does not exist: {run_id}")

    def fail_run(
        self,
        run_id: str,
        failed_at: datetime,
        error_message: str,
    ) -> None:
        """Rollback unfinished work and persist a terminal failure separately."""
        self.connection.rollback()
        with self.transaction() as cursor:
            cursor.execute(
                """
                UPDATE olist_simulator.simulation_runs
                SET state = 'failed',
                    heartbeat_at = GREATEST(
                        %s,
                        COALESCE(last_committed_source_timestamp, %s)
                    ),
                    finished_at = GREATEST(
                        %s,
                        COALESCE(last_committed_source_timestamp, %s)
                    ),
                    error_message = %s
                WHERE run_id = %s
                """,
                (
                    failed_at,
                    failed_at,
                    failed_at,
                    failed_at,
                    error_message,
                    run_id,
                ),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"Simulator run does not exist: {run_id}")

    def status(self, run_id: str | None = None) -> dict[str, Any] | None:
        with self._read_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    r.run_id,
                    r.random_seed,
                    r.target_rate,
                    r.state,
                    r.last_committed_source_timestamp,
                    r.counters,
                    (
                        SELECT COUNT(*)
                        FROM olist_simulator.pending_transitions AS t
                        WHERE t.run_id = r.run_id AND t.state = 'pending'
                    ) AS pending_transitions
                FROM olist_simulator.simulation_runs AS r
                WHERE (%s IS NULL OR r.run_id = %s)
                ORDER BY r.started_at DESC
                LIMIT 1
                """,
                (run_id, run_id),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        source_timestamp = row[4]
        return {
            "run_id": row[0],
            "random_seed": row[1],
            "rate": float(row[2]),
            "run_state": row[3],
            "last_committed_source_timestamp": (
                source_timestamp.isoformat() if source_timestamp else None
            ),
            "counters": _json_object(row[5]),
            "pending_transitions": row[6],
        }

    def replay_candidates(self, event_limit: int | None) -> list[dict[str, Any]]:
        if event_limit is not None and event_limit < 1:
            raise ValueError("event_limit must be positive")
        statement = """
            SELECT
                o.order_id,
                o.order_status,
                o.order_purchase_timestamp,
                o.order_approved_at,
                o.order_delivered_carrier_date,
                o.order_delivered_customer_date,
                o.order_estimated_delivery_date,
                EXISTS (
                    SELECT 1
                    FROM olist_oltp.order_reviews AS r
                    WHERE r.order_id = o.order_id
                ) AS has_review
            FROM olist_oltp.orders AS o
            WHERE o.order_status IN ('delivered', 'canceled', 'unavailable')
              AND NOT EXISTS (
                  SELECT 1
                  FROM olist_simulator.synthetic_entities AS s
                  WHERE s.entity_type = 'order'
                    AND s.entity_id = o.order_id
              )
            ORDER BY o.order_purchase_timestamp, o.order_id
        """
        parameters: tuple[Any, ...] = ()
        if event_limit is not None:
            statement += " LIMIT %s"
            parameters = (event_limit,)

        with self._read_cursor() as cursor:
            cursor.execute(statement, parameters)
            if cursor.description is None:
                raise RuntimeError("Replay candidate query returned no description")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(columns, row, strict=True)) for row in rows]

    def record_replay_mappings(
        self,
        run_id: str,
        source_order_id: str,
        mappings: list[tuple[datetime, datetime]],
        speed_multiplier: Decimal,
    ) -> None:
        with self.transaction() as cursor:
            cursor.executemany(
                """
                INSERT INTO olist_simulator.replay_timestamp_mappings (
                    run_id, entity_type, source_entity_id, source_timestamp,
                    replay_timestamp, speed_multiplier
                ) VALUES (%s, 'order', %s, %s, %s, %s)
                AS new
                ON DUPLICATE KEY UPDATE
                    replay_timestamp = new.replay_timestamp,
                    speed_multiplier = new.speed_multiplier
                """,
                [
                    (
                        run_id,
                        source_order_id,
                        source_timestamp,
                        replay_timestamp,
                        speed_multiplier,
                    )
                    for source_timestamp, replay_timestamp in mappings
                ],
            )

    @staticmethod
    def _touch(
        cursor: Any, run_id: str, source_at: datetime, increments: dict[str, int]
    ) -> None:
        cursor.execute(
            """
            SELECT counters
            FROM olist_simulator.simulation_runs
            WHERE run_id = %s
            FOR UPDATE
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Simulator run does not exist: {run_id}")
        counters = _json_object(row[0])
        for name, increment in increments.items():
            counters[name] = int(counters.get(name, 0)) + increment
        cursor.execute(
            """
            UPDATE olist_simulator.simulation_runs
            SET heartbeat_at = GREATEST(heartbeat_at, %s),
                last_committed_source_timestamp = GREATEST(
                    %s,
                    COALESCE(last_committed_source_timestamp, %s)
                ),
                counters = %s
            WHERE run_id = %s
            """,
            (
                source_at,
                source_at,
                source_at,
                json.dumps(counters, sort_keys=True),
                run_id,
            ),
        )
