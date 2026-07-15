"""Idempotent FK-safe loading of an Olist archive into the OLTP source."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO
from zipfile import ZipFile

from psycopg2.extras import execute_values

from scripts.simulation.database import SimulatorRepository
from scripts.simulation.domain import SimulationConfig


@dataclass(frozen=True)
class SeedSpec:
    entity_name: str
    file_name: str
    columns: tuple[str, ...]
    key_columns: tuple[str, ...]
    integer_columns: tuple[str, ...] = ()
    decimal_columns: tuple[str, ...] = ()
    timestamp_columns: tuple[str, ...] = ()


SEED_SPECS = (
    SeedSpec(
        "product_category_translation",
        "product_category_name_translation.csv",
        ("product_category_name", "product_category_name_english"),
        ("product_category_name",),
    ),
    SeedSpec(
        "customers",
        "olist_customers_dataset.csv",
        (
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
        ("customer_id",),
    ),
    SeedSpec(
        "sellers",
        "olist_sellers_dataset.csv",
        ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"),
        ("seller_id",),
    ),
    SeedSpec(
        "products",
        "olist_products_dataset.csv",
        (
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        ("product_id",),
        integer_columns=(
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    SeedSpec(
        "orders",
        "olist_orders_dataset.csv",
        (
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        ("order_id",),
        timestamp_columns=(
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    SeedSpec(
        "order_items",
        "olist_order_items_dataset.csv",
        (
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
        ("order_id", "order_item_id"),
        integer_columns=("order_item_id",),
        decimal_columns=("price", "freight_value"),
        timestamp_columns=("shipping_limit_date",),
    ),
    SeedSpec(
        "order_payments",
        "olist_order_payments_dataset.csv",
        (
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
        ("order_id", "payment_sequential"),
        integer_columns=("payment_sequential", "payment_installments"),
        decimal_columns=("payment_value",),
    ),
    SeedSpec(
        "order_reviews",
        "olist_order_reviews_dataset.csv",
        (
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
        ("review_id", "order_id"),
        integer_columns=("review_score",),
        timestamp_columns=("review_creation_date", "review_answer_timestamp"),
    ),
    SeedSpec(
        "geolocation",
        "olist_geolocation_dataset.csv",
        (
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ),
        (),
        decimal_columns=("geolocation_lat", "geolocation_lng"),
    ),
)


def source_identity(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    else:
        for file_path in sorted(path.glob("*.csv")):
            digest.update(file_path.name.encode())
            with file_path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def open_source(path: Path, file_name: str) -> Iterator[TextIO]:
    if path.is_dir():
        with (path / file_name).open(encoding="utf-8-sig", newline="") as handle:
            yield handle
        return
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        if file_name not in names:
            raise ValueError(f"Archive is missing required file: {file_name}")
        with (
            archive.open(file_name) as raw,
            io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as handle,
        ):
            yield handle


def convert_row(spec: SeedSpec, row: dict[str, str]) -> tuple[Any, ...]:
    if tuple(row) != spec.columns:
        raise ValueError(
            f"Unexpected header for {spec.file_name}: {tuple(row)!r}; "
            f"expected {spec.columns!r}"
        )
    converted: list[Any] = []
    for column in spec.columns:
        value = row[column]
        if value == "":
            converted.append(None)
        elif column in spec.integer_columns:
            converted.append(int(value))
        elif column in spec.decimal_columns:
            converted.append(value)
        elif column in spec.timestamp_columns:
            converted.append(datetime.fromisoformat(value))
        else:
            converted.append(value)
    return tuple(converted)


def batches(
    rows: Iterable[tuple[Any, ...]], size: int = 2000
) -> Iterator[list[tuple[Any, ...]]]:
    batch: list[tuple[Any, ...]] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def upsert_statement(spec: SeedSpec) -> str:
    columns = ", ".join(spec.columns)
    keys = ", ".join(spec.key_columns)
    mutable = [column for column in spec.columns if column not in spec.key_columns]
    update = ", ".join(f"{column} = excluded.{column}" for column in mutable)
    action = f"do update set {update}" if update else "do nothing"
    return f"insert into public.{spec.entity_name} ({columns}) values %s on conflict ({keys}) {action}"


def load_geolocation(
    cursor: Any,
    rows: Iterable[tuple[Any, ...]],
    identity: str,
) -> int:
    loaded = 0
    row_number = 2
    for batch in batches(rows):
        candidates = [
            (identity, row_number + index, *values)
            for index, values in enumerate(batch)
        ]
        execute_values(
            cursor,
            """
            with candidates (
                seed_identity, source_row_number, zip_prefix, lat, lng, city, state
            ) as (values %s),
            new_rows as (
                insert into simulator_control.seed_rows (
                    seed_identity, entity_name, source_row_number,
                    business_key, loaded_at
                )
                select seed_identity, 'geolocation', source_row_number, null,
                       current_timestamp
                from candidates
                on conflict do nothing
                returning seed_identity, source_row_number
            )
            insert into public.geolocation (
                geolocation_zip_code_prefix, geolocation_lat, geolocation_lng,
                geolocation_city, geolocation_state
            )
            select c.zip_prefix, c.lat::numeric, c.lng::numeric, c.city, c.state
            from candidates c join new_rows n using (seed_identity, source_row_number)
            """,
            candidates,
            page_size=len(candidates),
        )
        loaded += len(batch)
        row_number += len(batch)
    return loaded


def seed_archive(
    repository: SimulatorRepository,
    source_path: Path,
    *,
    random_seed: int,
    run_id: str,
    logical_time: datetime,
) -> dict[str, int]:
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    identity = source_identity(source_path)
    config = SimulationConfig(
        random_seed=random_seed, start_time=logical_time, target_rate=1
    )
    repository.start_run(run_id, "seed", config)
    counts: dict[str, int] = {}

    try:
        for spec in SEED_SPECS:
            with open_source(source_path, spec.file_name) as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    raise ValueError(f"{spec.file_name} has no header")
                if tuple(reader.fieldnames) != spec.columns:
                    raise ValueError(
                        f"Unexpected header for {spec.file_name}: {tuple(reader.fieldnames)!r}"
                    )
                converted = (convert_row(spec, row) for row in reader)
                with repository.connection, repository.connection.cursor() as cursor:
                    if spec.entity_name == "geolocation":
                        counts[spec.entity_name] = load_geolocation(
                            cursor, converted, identity
                        )
                        continue
                    entity_count = 0
                    for batch in batches(converted):
                        if spec.entity_name == "products":
                            categories = sorted({row[1] for row in batch if row[1]})
                            if categories:
                                execute_values(
                                    cursor,
                                    """
                                    insert into public.product_category_translation
                                        (product_category_name, product_category_name_english)
                                    values %s on conflict (product_category_name) do nothing
                                    """,
                                    [(value, value) for value in categories],
                                )
                        execute_values(
                            cursor, upsert_statement(spec), batch, page_size=len(batch)
                        )
                        entity_count += len(batch)
                    counts[spec.entity_name] = entity_count
        with repository.connection, repository.connection.cursor() as cursor:
            cursor.execute(
                """
                update simulator_control.simulation_runs
                set counters = %s::jsonb,
                    last_committed_source_timestamp = %s,
                    heartbeat_at = %s,
                    state = 'completed', finished_at = %s
                where run_id = %s
                """,
                (
                    json.dumps(counts, sort_keys=True),
                    logical_time,
                    logical_time,
                    logical_time,
                    run_id,
                ),
            )
    except Exception:
        repository.connection.rollback()
        repository.finish_run(run_id, "failed", logical_time)
        raise
    return counts
