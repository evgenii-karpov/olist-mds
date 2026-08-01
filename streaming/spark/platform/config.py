"""Validated Spark/Polaris configuration with file-only secret inputs."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

CATALOG_ALIAS = "lakehouse"
DEFAULT_CATALOG_URI = "http://polaris:8181/api/catalog"
DEFAULT_CATALOG_NAME = "olist_lakehouse"
DEFAULT_CHECKPOINT_ROOT = "s3a://olist-checkpoints"
DEFAULT_OBJECT_STORE_ENDPOINT = "http://minio:9000"
DEFAULT_OBJECT_STORE_REGION = "us-east-1"
DEFAULT_S3A_CREDENTIAL_PROVIDER = (
    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
)

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_REDACTION_REGEX = r"(?i)secret|password|token|access[.]?key|credential"


class ConfigurationError(ValueError):
    """Raised before Spark starts when the platform contract is invalid."""


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "")
    if not value:
        raise ConfigurationError(f"required configuration {name} is not set")
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ConfigurationError(
            f"configuration {name} contains a forbidden control byte"
        )
    return value


def _boolean(environment: Mapping[str, str], name: str, default: bool) -> bool:
    raw = environment.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ConfigurationError(f"{name} must be exactly true or false")


def _secret_from_file(environment: Mapping[str, str], name: str) -> str:
    path_text = _required(environment, name)
    path = Path(path_text)
    try:
        stat = path.stat()
    except OSError as exc:
        raise ConfigurationError(
            f"cannot read secret file configured by {name}"
        ) from exc
    if not path.is_file() or stat.st_size > 65536:
        raise ConfigurationError(f"secret file configured by {name} is invalid")
    try:
        value = path.read_text(encoding="utf-8").rstrip("\r\n")
    except (OSError, UnicodeError) as exc:
        raise ConfigurationError(
            f"cannot read secret file configured by {name}"
        ) from exc
    if not value or any(character in value for character in ("\n", "\r", "\x00")):
        raise ConfigurationError(
            f"secret file configured by {name} has invalid content"
        )
    return value


def _validate_service_url(value: str, name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ConfigurationError(f"{name} must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError(
            f"{name} must not contain credentials, query, or fragment"
        )
    return value.rstrip("/")


def _validate_checkpoint_root(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "s3a" or parsed.netloc != "olist-checkpoints":
        raise ConfigurationError(
            "SPARK_CHECKPOINT_ROOT must use the isolated s3a://olist-checkpoints bucket"
        )
    if parsed.query or parsed.fragment:
        raise ConfigurationError(
            "SPARK_CHECKPOINT_ROOT must not contain query or fragment"
        )
    return value.rstrip("/")


@dataclass(frozen=True)
class SparkPlatformConfig:
    """Complete, validated properties needed by Spark lakehouse drivers."""

    catalog_uri: str
    catalog_name: str
    warehouse: str
    checkpoint_root: str
    object_store_endpoint: str
    object_store_region: str
    object_store_path_style: bool
    object_store_credential_provider: str
    polaris_client_id: str
    polaris_client_secret: str
    checkpoint_access_key: str
    checkpoint_secret_key: str

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> SparkPlatformConfig:
        env = os.environ if environment is None else environment
        catalog_uri = _validate_service_url(
            env.get("ICEBERG_CATALOG_URI", DEFAULT_CATALOG_URI),
            "ICEBERG_CATALOG_URI",
        )
        catalog_name = env.get("ICEBERG_CATALOG_NAME", DEFAULT_CATALOG_NAME)
        warehouse = env.get("ICEBERG_WAREHOUSE", DEFAULT_CATALOG_NAME)
        if catalog_name != DEFAULT_CATALOG_NAME or warehouse != DEFAULT_CATALOG_NAME:
            raise ConfigurationError(
                "ICEBERG_CATALOG_NAME and ICEBERG_WAREHOUSE must both be olist_lakehouse"
            )
        if not _SAFE_IDENTIFIER.fullmatch(catalog_name):
            raise ConfigurationError("ICEBERG_CATALOG_NAME is not a safe identifier")

        checkpoint_root = _validate_checkpoint_root(
            env.get("SPARK_CHECKPOINT_ROOT", DEFAULT_CHECKPOINT_ROOT)
        )
        endpoint = _validate_service_url(
            env.get("OBJECT_STORE_ENDPOINT", DEFAULT_OBJECT_STORE_ENDPOINT),
            "OBJECT_STORE_ENDPOINT",
        )
        region = env.get("OBJECT_STORE_REGION", DEFAULT_OBJECT_STORE_REGION)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", region):
            raise ConfigurationError("OBJECT_STORE_REGION has invalid syntax")
        provider = env.get(
            "OBJECT_STORE_CREDENTIAL_PROVIDER", DEFAULT_S3A_CREDENTIAL_PROVIDER
        )
        if provider != DEFAULT_S3A_CREDENTIAL_PROVIDER:
            raise ConfigurationError(
                "local checkpoint access requires SimpleAWSCredentialsProvider"
            )

        client_id = _secret_from_file(env, "POLARIS_SPARK_CLIENT_ID_FILE")
        if ":" in client_id:
            raise ConfigurationError("Polaris client ID must not contain ':'")

        return cls(
            catalog_uri=catalog_uri,
            catalog_name=catalog_name,
            warehouse=warehouse,
            checkpoint_root=checkpoint_root,
            object_store_endpoint=endpoint,
            object_store_region=region,
            object_store_path_style=_boolean(env, "OBJECT_STORE_PATH_STYLE", True),
            object_store_credential_provider=provider,
            polaris_client_id=client_id,
            polaris_client_secret=_secret_from_file(
                env, "POLARIS_SPARK_CLIENT_SECRET_FILE"
            ),
            checkpoint_access_key=_secret_from_file(
                env, "OBJECT_STORE_ACCESS_KEY_FILE"
            ),
            checkpoint_secret_key=_secret_from_file(
                env, "OBJECT_STORE_SECRET_KEY_FILE"
            ),
        )

    def spark_properties(self) -> dict[str, str]:
        """Return deterministic Spark properties; the caller must keep them secret."""

        catalog_prefix = f"spark.sql.catalog.{CATALOG_ALIAS}"
        return {
            "spark.redaction.regex": _REDACTION_REGEX,
            "spark.sql.redaction.options.regex": _REDACTION_REGEX,
            "spark.sql.extensions": (
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
            ),
            catalog_prefix: "org.apache.iceberg.spark.SparkCatalog",
            f"{catalog_prefix}.type": "rest",
            f"{catalog_prefix}.uri": self.catalog_uri,
            f"{catalog_prefix}.warehouse": self.warehouse,
            f"{catalog_prefix}.credential": (
                f"{self.polaris_client_id}:{self.polaris_client_secret}"
            ),
            f"{catalog_prefix}.scope": "PRINCIPAL_ROLE:ALL",
            f"{catalog_prefix}.oauth2-server-uri": (
                f"{self.catalog_uri}/v1/oauth/tokens"
            ),
            f"{catalog_prefix}.header.X-Iceberg-Access-Delegation": (
                "vended-credentials"
            ),
            f"{catalog_prefix}.token-refresh-enabled": "false",
            f"{catalog_prefix}.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
            f"{catalog_prefix}.client.region": self.object_store_region,
            "spark.sql.session.timeZone": "UTC",
            "spark.sql.shuffle.partitions": "4",
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.hadoop.fs.s3a.endpoint": self.object_store_endpoint,
            "spark.hadoop.fs.s3a.endpoint.region": self.object_store_region,
            "spark.hadoop.fs.s3a.path.style.access": str(
                self.object_store_path_style
            ).lower(),
            "spark.hadoop.fs.s3a.connection.ssl.enabled": str(
                self.object_store_endpoint.startswith("https://")
            ).lower(),
            "spark.hadoop.fs.s3a.aws.credentials.provider": (
                self.object_store_credential_provider
            ),
            "spark.hadoop.fs.s3a.access.key": self.checkpoint_access_key,
            "spark.hadoop.fs.s3a.secret.key": self.checkpoint_secret_key,
            "spark.olist.checkpoint.root": self.checkpoint_root,
        }
