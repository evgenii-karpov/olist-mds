"""Connection helpers for the dedicated local pipeline control database."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as PgConnection


def read_secret(
    value: str | None, file_path: str | None, default: str | None
) -> str | None:
    if value:
        return value
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    return default


def env_default(name: str, default: str) -> str:
    return os.environ.get(name, default)


def add_control_postgres_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--control-host",
        default=env_default("CONTROL_POSTGRES_HOST", "localhost"),
    )
    parser.add_argument(
        "--control-port",
        type=int,
        default=int(env_default("CONTROL_POSTGRES_PORT", "5432")),
    )
    parser.add_argument(
        "--control-database",
        default=env_default("CONTROL_POSTGRES_DB", "olist_control"),
    )
    parser.add_argument(
        "--control-user",
        default=env_default("CONTROL_POSTGRES_USER", "olist_control"),
    )
    parser.add_argument(
        "--control-password",
        default=os.environ.get("CONTROL_POSTGRES_PASSWORD"),
    )
    parser.add_argument(
        "--control-password-file",
        default=os.environ.get("CONTROL_POSTGRES_PASSWORD_FILE"),
    )


def control_connection(args: argparse.Namespace) -> PgConnection:
    return psycopg2.connect(
        host=args.control_host,
        port=args.control_port,
        dbname=args.control_database,
        user=args.control_user,
        password=read_secret(
            args.control_password,
            args.control_password_file,
            "olist_control",
        ),
        connect_timeout=10,
    )
