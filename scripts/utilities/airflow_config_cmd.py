#!/usr/bin/env python
"""Resolve local Airflow config values from Docker secrets."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def read_secret(name: str, default: str) -> str:
    file_path = os.environ.get(f"{name}_FILE")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    return os.environ.get(name, default)


def sql_alchemy_conn() -> str:
    host = os.environ.get("AIRFLOW_POSTGRES_HOST", "airflow-postgres")
    port = os.environ.get("AIRFLOW_POSTGRES_PORT", "5432")
    database = os.environ.get("AIRFLOW_POSTGRES_DB", "airflow")
    user = os.environ.get("AIRFLOW_POSTGRES_USER", "airflow")
    password = read_secret("AIRFLOW_POSTGRES_PASSWORD", "airflow")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def api_secret_key() -> str:
    return read_secret("AIRFLOW__API__SECRET_KEY", "local_dev_only_secret_key")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_name", choices=("sql_alchemy_conn", "api_secret_key"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.config_name == "sql_alchemy_conn":
        sys.stdout.write(sql_alchemy_conn())
    else:
        sys.stdout.write(api_secret_key())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
