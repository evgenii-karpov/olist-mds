from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest
from streaming.spark.platform.config import ConfigurationError, SparkPlatformConfig
from streaming.spark.platform.render_spark_properties import render_properties
from streaming.spark.platform.topology import (
    ALL_CONTINUOUS_QUERIES,
    BRONZE_QUERY,
    SILVER_QUERIES,
    checkpoint_path,
)


def _write_secret(directory: Path, name: str, value: str) -> str:
    path = directory / name
    path.write_text(f"{value}\n", encoding="utf-8")
    return str(path)


def _environment(directory: Path) -> dict[str, str]:
    return {
        "POLARIS_SPARK_CLIENT_ID_FILE": _write_secret(
            directory, "polaris-client-id", "spark-id"
        ),
        "POLARIS_SPARK_CLIENT_SECRET_FILE": _write_secret(
            directory, "polaris-client-secret", "spark-secret"
        ),
        "OBJECT_STORE_ACCESS_KEY_FILE": _write_secret(
            directory, "checkpoint-access-key", "checkpoint-user"
        ),
        "OBJECT_STORE_SECRET_KEY_FILE": _write_secret(
            directory, "checkpoint-secret-key", "checkpoint-secret"
        ),
    }


def test_spark_properties_match_the_polaris_and_checkpoint_contract(
    tmp_path: Path,
) -> None:
    properties = SparkPlatformConfig.from_environment(
        _environment(tmp_path)
    ).spark_properties()

    assert properties["spark.sql.extensions"] == (
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
    )
    assert properties["spark.sql.catalog.lakehouse"] == (
        "org.apache.iceberg.spark.SparkCatalog"
    )
    assert properties["spark.sql.catalog.lakehouse.type"] == "rest"
    assert properties["spark.sql.catalog.lakehouse.uri"] == (
        "http://polaris:8181/api/catalog"
    )
    assert properties["spark.sql.catalog.lakehouse.warehouse"] == "olist_lakehouse"
    assert properties["spark.sql.catalog.lakehouse.credential"] == (
        "spark-id:spark-secret"
    )
    assert properties["spark.sql.catalog.lakehouse.scope"] == "PRINCIPAL_ROLE:ALL"
    assert properties["spark.sql.catalog.lakehouse.oauth2-server-uri"] == (
        "http://polaris:8181/api/catalog/v1/oauth/tokens"
    )
    assert (
        properties["spark.sql.catalog.lakehouse.header.X-Iceberg-Access-Delegation"]
        == "vended-credentials"
    )
    assert properties["spark.sql.catalog.lakehouse.token-refresh-enabled"] == "false"
    assert properties["spark.sql.catalog.lakehouse.io-impl"] == (
        "org.apache.iceberg.aws.s3.S3FileIO"
    )
    assert properties["spark.hadoop.fs.s3a.endpoint"] == "http://minio:9000"
    assert properties["spark.hadoop.fs.s3a.endpoint.region"] == "us-east-1"
    assert properties["spark.hadoop.fs.s3a.path.style.access"] == "true"
    assert properties["spark.hadoop.fs.s3a.access.key"] == "checkpoint-user"
    assert properties["spark.hadoop.fs.s3a.secret.key"] == "checkpoint-secret"
    assert properties["spark.olist.checkpoint.root"] == "s3a://olist-checkpoints"
    assert properties["spark.sql.session.timeZone"] == "UTC"
    assert "secret|password|token" in properties["spark.redaction.regex"]


def test_secrets_are_file_only_and_checkpoint_bucket_is_not_configurable(
    tmp_path: Path,
) -> None:
    environment = _environment(tmp_path)
    environment["POLARIS_SPARK_CLIENT_SECRET"] = "must-never-be-read"
    del environment["POLARIS_SPARK_CLIENT_SECRET_FILE"]

    with pytest.raises(ConfigurationError, match="POLARIS_SPARK_CLIENT_SECRET_FILE"):
        SparkPlatformConfig.from_environment(environment)

    environment = _environment(tmp_path)
    environment["SPARK_CHECKPOINT_ROOT"] = "s3a://olist-lakehouse/checkpoints"
    with pytest.raises(ConfigurationError, match="isolated"):
        SparkPlatformConfig.from_environment(environment)


def test_properties_file_is_atomic_private_and_contains_no_file_paths(
    tmp_path: Path,
) -> None:
    environment = _environment(tmp_path)
    output = tmp_path / "rendered" / "spark.properties"

    render_properties(output, SparkPlatformConfig.from_environment(environment))

    rendered = output.read_text(encoding="utf-8")
    assert "spark-id:spark-secret" in rendered
    assert "checkpoint-user" in rendered
    assert not any(secret_path in rendered for secret_path in environment.values())
    if os.name != "nt":
        assert stat.S_IMODE(output.stat().st_mode) == 0o600
    assert list(output.parent.glob(".*.tmp")) == []


def test_query_names_and_checkpoints_are_stable_and_physically_isolated() -> None:
    assert BRONZE_QUERY == "kafka_to_bronze"
    assert SILVER_QUERIES == (
        "capture_avro_schemas",
        "normalize_mysql_transactions",
        "normalize_customers",
        "normalize_orders",
        "normalize_order_items",
        "normalize_order_payments",
        "normalize_order_reviews",
        "normalize_products",
        "normalize_sellers",
        "normalize_product_category_translation",
    )
    assert len(ALL_CONTINUOUS_QUERIES) == len(set(ALL_CONTINUOUS_QUERIES)) == 11
    assert checkpoint_path("normalize_orders", 3) == (
        "s3a://olist-checkpoints/normalize_orders/contract-v3/"
    )
    with pytest.raises(ValueError, match="unknown"):
        checkpoint_path("normalize_unknown", 1)
    with pytest.raises(ValueError, match="isolated"):
        checkpoint_path("normalize_orders", 1, "s3a://olist-lakehouse")
