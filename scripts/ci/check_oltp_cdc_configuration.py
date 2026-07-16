"""Validate the live PostgreSQL publication, role, replica identity, and slot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import psycopg2

CAPTURED = {
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5433)
    parser.add_argument("--database", default="olist_oltp")
    parser.add_argument("--user", default="olist_admin")
    parser.add_argument(
        "--password-file",
        type=Path,
        default=Path("docker/secrets/dev/postgres_password.txt"),
    )
    parser.add_argument("--require-slot", action="store_true")
    return parser.parse_args()


def scalar(cursor: Any, query: str) -> Any:
    cursor.execute(query)
    return cursor.fetchone()[0]


def main() -> int:
    args = parse_args()
    password = args.password_file.read_text(encoding="utf-8").strip()
    connection = psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=password,
    )
    try:
        with connection.cursor() as cursor:
            settings = {
                name: scalar(cursor, f"select current_setting('{name}')")
                for name in (
                    "wal_level",
                    "max_replication_slots",
                    "max_wal_senders",
                    "max_slot_wal_keep_size",
                )
            }
            cursor.execute(
                "select tablename from pg_publication_tables "
                "where pubname='olist_cdc_publication' and schemaname='public'"
            )
            publication = {row[0] for row in cursor.fetchall()}
            cursor.execute(
                "select relname, relreplident from pg_class "
                "where relnamespace='public'::regnamespace and relname=any(%s)",
                (list(CAPTURED),),
            )
            identities = dict(cursor.fetchall())
            replication = scalar(
                cursor,
                "select rolreplication from pg_roles where rolname='olist_cdc_reader'",
            )
            cursor.execute(
                "select slot_name, active, restart_lsn::text, "
                "confirmed_flush_lsn::text, "
                "pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)::bigint "
                "from pg_replication_slots where slot_name='olist_cdc_slot'"
            )
            slot_row = cursor.fetchone()
    finally:
        connection.close()

    errors: list[str] = []
    if settings["wal_level"] != "logical":
        errors.append(f"wal_level is {settings['wal_level']!r}")
    if (
        int(settings["max_replication_slots"]) < 1
        or int(settings["max_wal_senders"]) < 1
    ):
        errors.append(f"logical replication capacity is invalid: {settings}")
    if publication != CAPTURED:
        errors.append(f"publication tables are {sorted(publication)}")
    if identities != {table: "f" for table in CAPTURED}:
        errors.append(f"replica identity is not FULL: {identities}")
    if replication is not True:
        errors.append("olist_cdc_reader is not a replication role")
    if args.require_slot and slot_row is None:
        errors.append("olist_cdc_slot is missing")
    if errors:
        raise AssertionError("; ".join(errors))
    evidence = {
        "settings": settings,
        "publication_tables": sorted(publication),
        "replica_identity": identities,
        "replication_role": replication,
        "slot": None
        if slot_row is None
        else {
            "name": slot_row[0],
            "active": slot_row[1],
            "restart_lsn": slot_row[2],
            "confirmed_flush_lsn": slot_row[3],
            "retained_wal_bytes": slot_row[4],
        },
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
