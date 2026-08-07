"""Spark entry point for versioned Iceberg table migrations."""

from __future__ import annotations

import json

from streaming.spark.platform.config import resolve_catalog_alias
from streaming.spark.platform.migrations.initial_lakehouse import (
    MIGRATION_ID,
    MIGRATION_VERSION,
    apply,
)


def main() -> int:
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("olist_iceberg_migrations").getOrCreate()
    try:
        checksum = apply(spark, catalog_alias=resolve_catalog_alias())
        print(
            json.dumps(
                {
                    "migration_id": MIGRATION_ID,
                    "migration_version": MIGRATION_VERSION,
                    "checksum_sha256": checksum,
                    "status": "APPLIED",
                },
                sort_keys=True,
            )
        )
    finally:
        spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
