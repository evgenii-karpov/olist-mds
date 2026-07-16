"""Disposable PostgreSQL proof for Phase 5 ordering, history, and delete semantics."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import psycopg2
from psycopg2 import sql

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "olist_cdc_phase5_test_"


def password(args: argparse.Namespace) -> str:
    if args.password:
        return args.password
    if args.password_file:
        return Path(args.password_file).read_text(encoding="utf-8").strip()
    return "olist"


def maintenance_connection(args: argparse.Namespace):
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.maintenance_database,
        user=args.user,
        password=password(args),
    )


def test_connection(args: argparse.Namespace, database: str):
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=database,
        user=args.user,
        password=password(args),
    )


def apply_bootstrap(connection) -> None:
    with connection, connection.cursor() as cursor:
        for name in (
            "001_create_schemas.sql",
            "006_create_cdc_tables.sql",
            "007_create_cdc_transform_audit.sql",
        ):
            cursor.execute((ROOT / "infra/postgres" / name).read_text(encoding="utf-8"))


def add_file(connection, run_id: str, table: str, batch: int, row_count: int) -> str:
    object_uri = f"s3://phase5/{run_id}/{table}-{batch}.parquet"
    manifest_uri = f"s3://phase5/{run_id}/{table}-{batch}.manifest.json"
    topic = f"olist_cdc.public.{table}"
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
            insert into cdc_audit.cdc_ingest_runs (
                ingest_run_id, run_kind, status, finished_at
            ) values (%s, 'MANUAL', 'SUCCEEDED', clock_timestamp())
            on conflict (ingest_run_id) do nothing
            """,
            (run_id,),
        )
        cursor.execute(
            """
            insert into cdc_audit.cdc_files (
                manifest_uri, manifest_etag, object_uri, object_etag,
                object_sha256, object_size_bytes, source_table, topic,
                partition_id, offset_ranges, min_offset, max_offset, schema_id,
                manifest_row_count, operation_counts, ingest_date,
                source_ts_min, source_ts_max, closed_at, status,
                loaded_by_run_id, loaded_at
            ) values (
                %s, %s, %s, %s, %s, 1, %s, %s, 0, %s, %s, %s, '1',
                %s, %s, current_date, clock_timestamp(), clock_timestamp(),
                clock_timestamp(), 'LOADED', %s, clock_timestamp()
            )
            """,
            (
                manifest_uri,
                f"manifest-{batch}",
                object_uri,
                f"object-{batch}",
                str(batch).zfill(64),
                table,
                topic,
                json.dumps([[batch, batch + row_count - 1]]),
                batch,
                batch + row_count - 1,
                row_count,
                json.dumps({"r": row_count}),
                run_id,
            ),
        )
    return object_uri


def add_event(
    connection,
    table: str,
    business: dict[str, object],
    operation: str,
    lsn: int,
    tx_order: int,
    offset: int,
    object_uri: str,
) -> None:
    topic = f"olist_cdc.public.{table}"
    now = datetime.now(UTC)
    values = {
        **business,
        "_event_id": f"{topic}:0:{offset}",
        "_op": operation,
        "_source_ts": now,
        "_source_lsn": lsn,
        "_tx_id": 1,
        "_tx_order": tx_order,
        "_topic": topic,
        "_partition": 0,
        "_offset": offset,
        "_kafka_ts": now,
        "_key_schema_id": 1,
        "_schema_id": 1,
        "_nifi_written_at": now,
        "_source_object_uri": object_uri,
    }
    columns = list(values)
    query = sql.SQL("insert into raw_cdc.{} ({}) values ({})").format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    with connection, connection.cursor() as cursor:
        cursor.execute(query, [values[column] for column in columns])


def run_transform(args: argparse.Namespace, database: str, run_id: str) -> None:
    base = [
        sys.executable,
        str(ROOT / "scripts/cdc/realtime_transform.py"),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--database",
        database,
        "--user",
        args.user,
        "--password",
        password(args),
    ]
    env = {
        **os.environ,
        "POSTGRES_HOST": args.host,
        "POSTGRES_PORT": str(args.port),
        "POSTGRES_DB": database,
        "POSTGRES_USER": args.user,
        "POSTGRES_PASSWORD": password(args),
        "DBT_PROFILES_DIR": str(ROOT / "dbt/olist_analytics"),
        "PYTHONUTF8": "1",
    }
    subprocess.run(
        [
            *base,
            "prepare",
            "--transform-run-id",
            run_id,
            "--dag-id",
            "phase5_integration",
            "--orchestration-run-id",
            run_id,
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [*base, "build", "--transform-run-id", run_id],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [*base, "finish", "--transform-run-id", run_id],
        cwd=ROOT,
        env=env,
        check=True,
    )


def verify_publication_round_trip(
    args: argparse.Namespace, database: str, connection
) -> None:
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
            create table marts.mart_daily_revenue as
            select
                order_purchase_date, gross_revenue, allocated_payment_revenue,
                product_revenue, freight_revenue, orders_count, customers_count,
                items_count, average_order_value, average_paid_order_value,
                average_delivery_days, late_deliveries_count
            from realtime_marts.mart_daily_revenue_realtime;
            create table marts.mart_monthly_arpu as
            select
                order_month, active_customers, total_revenue, arpu, orders_count,
                orders_per_customer, average_order_value, repeat_customer_rate
            from realtime_marts.mart_monthly_arpu_realtime;
            update cdc_audit.cdc_publication_state
            set parity_status = 'PASS'
            where publication_name = 'olist_marts';
            """
        )
    base = [
        sys.executable,
        str(ROOT / "scripts/cdc/realtime_transform.py"),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--database",
        database,
        "--user",
        args.user,
        "--password",
        password(args),
    ]
    for target in ("realtime", "batch"):
        subprocess.run(
            [*base, "publish", "--target", target, "--approved-by", "integration"],
            cwd=ROOT,
            check=True,
        )
        connection.commit()
        assert (
            scalar(connection, "select count(*) from analytics.mart_daily_revenue") == 1
        )
        connection.commit()


def scalar(connection, query: str):
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            raise AssertionError(f"query returned no row: {query}")
        return row[0]


def seed_initial(connection) -> None:
    run_id = "phase5_seed"
    entities = {
        "customers": {
            "customer_id": "c1",
            "customer_unique_id": "u1",
            "customer_zip_code_prefix": "01001",
            "customer_city": "sao paulo",
            "customer_state": "SP",
        },
        "orders": {
            "order_id": "o1",
            "customer_id": "c1",
            "order_status": "created",
            "order_purchase_timestamp": "2018-01-01T10:00:00+00:00",
            "order_approved_at": None,
            "order_delivered_carrier_date": None,
            "order_delivered_customer_date": None,
            "order_estimated_delivery_date": "2018-01-10T00:00:00+00:00",
        },
        "order_items": {
            "order_id": "o1",
            "order_item_id": 1,
            "product_id": "p1",
            "seller_id": "s1",
            "shipping_limit_date": "2018-01-03T00:00:00+00:00",
            "price": 100,
            "freight_value": 10,
        },
        "order_payments": {
            "order_id": "o1",
            "payment_sequential": 1,
            "payment_type": "credit_card",
            "payment_installments": 1,
            "payment_value": 110,
        },
        "products": {
            "product_id": "p1",
            "product_category_name": "cat",
            "product_name_lenght": 3,
            "product_description_lenght": 4,
            "product_photos_qty": 1,
            "product_weight_g": 100,
            "product_length_cm": 1,
            "product_height_cm": 2,
            "product_width_cm": 3,
        },
        "sellers": {
            "seller_id": "s1",
            "seller_zip_code_prefix": "01001",
            "seller_city": "sao paulo",
            "seller_state": "SP",
        },
        "product_category_translation": {
            "product_category_name": "cat",
            "product_category_name_english": "category",
        },
    }
    for offset, (table, business) in enumerate(entities.items(), start=1):
        uri = add_file(connection, run_id, table, offset, 1)
        add_event(connection, table, business, "r", 100 + offset, offset, offset, uri)


def verify(args: argparse.Namespace, database: str) -> None:
    connection = test_connection(args, database)
    try:
        apply_bootstrap(connection)
        seed_initial(connection)
        run_transform(args, database, "phase5_transform_1")
        assert (
            scalar(
                connection,
                "select count(*) from realtime_core.fact_order_items_realtime",
            )
            == 1
        )
        assert (
            scalar(
                connection,
                "select gross_revenue from realtime_marts.mart_daily_revenue_realtime",
            )
            == 110
        )
        initial_freshness_horizon = scalar(
            connection,
            "select min(max_source_ts) from cdc_audit.cdc_mart_freshness",
        )
        verify_publication_round_trip(args, database, connection)

        order_business = {
            "order_id": "o1",
            "customer_id": "c1",
            "order_status": "shipped",
            "order_purchase_timestamp": "2018-01-02T10:00:00+00:00",
            "order_approved_at": None,
            "order_delivered_carrier_date": None,
            "order_delivered_customer_date": None,
            "order_estimated_delivery_date": "2018-01-10T00:00:00+00:00",
        }
        uri = add_file(connection, "phase5_updates", "orders", 20, 3)
        add_event(
            connection,
            "orders",
            {**order_business, "order_status": "approved"},
            "u",
            120,
            1,
            20,
            uri,
        )
        add_event(connection, "orders", order_business, "u", 130, 2, 21, uri)
        add_event(
            connection,
            "orders",
            {
                **order_business,
                "order_status": "late_old",
                "order_purchase_timestamp": "2018-01-01T10:00:00+00:00",
            },
            "u",
            125,
            3,
            22,
            uri,
        )
        run_transform(args, database, "phase5_transform_2")
        assert (
            scalar(
                connection,
                "select min(max_source_ts) from cdc_audit.cdc_mart_freshness",
            )
            >= initial_freshness_horizon
        )
        assert (
            scalar(
                connection,
                "select order_status from realtime_staging.stg_cdc__orders_current",
            )
            == "shipped"
        )
        assert (
            scalar(
                connection,
                "select order_purchase_date from realtime_marts.mart_daily_revenue_realtime",
            ).isoformat()
            == "2018-01-02"
        )
        assert (
            scalar(
                connection,
                "select count(*) from realtime_core.hist_cdc__orders where order_id='o1'",
            )
            == 4
        )

        item = {
            "order_id": "o1",
            "order_item_id": 1,
            "product_id": "p1",
            "seller_id": "s1",
            "shipping_limit_date": "2018-01-03T00:00:00+00:00",
            "price": 100,
            "freight_value": 10,
        }
        uri = add_file(connection, "phase5_delete", "order_items", 30, 1)
        add_event(connection, "order_items", item, "d", 140, 1, 30, uri)
        run_transform(args, database, "phase5_transform_3")
        assert (
            scalar(
                connection,
                "select count(*) from realtime_core.fact_order_items_realtime",
            )
            == 0
        )
        assert (
            scalar(
                connection,
                "select count(*) from realtime_marts.mart_daily_revenue_realtime",
            )
            == 0
        )
        assert (
            scalar(
                connection,
                "select count(*) from realtime_core.hist_cdc__order_items where is_deleted",
            )
            == 1
        )
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--maintenance-database", default="olist_analytics")
    parser.add_argument("--user", default="olist")
    parser.add_argument("--password")
    parser.add_argument("--password-file")
    args = parser.parse_args()
    database = f"{PREFIX}{uuid.uuid4().hex[:10]}"
    maintenance = maintenance_connection(args)
    maintenance.autocommit = True
    try:
        with maintenance.cursor() as cursor:
            cursor.execute(
                sql.SQL("create database {}").format(sql.Identifier(database))
            )
        verify(args, database)
        print(json.dumps({"database": database, "status": "success"}))
    finally:
        if not database.startswith(PREFIX):
            raise RuntimeError("refusing to drop a non-disposable database")
        with maintenance.cursor() as cursor:
            cursor.execute(
                "select pg_terminate_backend(pid) from pg_stat_activity where datname = %s",
                (database,),
            )
            cursor.execute(
                sql.SQL("drop database if exists {}").format(sql.Identifier(database))
            )
        maintenance.close()


if __name__ == "__main__":
    main()
