"""Validated Spark backend configuration with file-only secret inputs."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CATALOG_ALIAS = "lakehouse"
DEFAULT_CATALOG_URI = "http://polaris:8181/api/catalog"
DEFAULT_CATALOG_NAME = "olist_lakehouse"
DEFAULT_GCP_CATALOG_URI = "https://biglake.googleapis.com/iceberg/v1/restcatalog"
DEFAULT_CHECKPOINT_ROOT = "s3a://olist-checkpoints"
DEFAULT_OBJECT_STORE_ENDPOINT = "http://minio:9000"
DEFAULT_OBJECT_STORE_REGION = "us-east-1"
DEFAULT_S3A_CREDENTIAL_PROVIDER = (
    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
)
GCP_FILE_IO = "org.apache.iceberg.gcp.gcs.GCSFileIO"
GCP_AUTH_MANAGER = "org.apache.iceberg.gcp.auth.GoogleAuthManager"
GCP_CHECKPOINT_FILESYSTEM = "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
GCP_CHECKPOINT_ABSTRACT_FILESYSTEM = "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"
DEFAULT_SOURCE_TIME_ZONE = "America/Sao_Paulo"

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


def _source_time_zone(environment: Mapping[str, str]) -> str:
    value = environment.get("SOURCE_TIME_ZONE", DEFAULT_SOURCE_TIME_ZONE).strip()
    if not value:
        raise ConfigurationError("SOURCE_TIME_ZONE must not be empty")
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ConfigurationError(f"unknown SOURCE_TIME_ZONE: {value}") from exc
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


def _validate_gcs_uri(value: str, name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "gs" or not parsed.hostname:
        raise ConfigurationError(f"{name} must be an absolute gs:// URI")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError(
            f"{name} must not contain credentials, query, or fragment"
        )
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]", parsed.hostname):
        raise ConfigurationError(f"{name} contains an invalid bucket name")
    return value.rstrip("/")


def _validate_gcp_warehouse(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"bl", "gs"} or not parsed.netloc:
        raise ConfigurationError(
            "ICEBERG_WAREHOUSE must be a bl:// catalog or gs:// warehouse URI"
        )
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError(
            "ICEBERG_WAREHOUSE must not contain credentials, query, or fragment"
        )
    return value.rstrip("/")


def _validate_adc_path(value: str) -> str:
    path = Path(
        _required(
            {"GOOGLE_APPLICATION_CREDENTIALS": value}, "GOOGLE_APPLICATION_CREDENTIALS"
        )
    )
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ConfigurationError(
            "GOOGLE_APPLICATION_CREDENTIALS must point to a mounted regular file"
        )
    return str(path)


def resolve_backend(environment: Mapping[str, str] | None = None) -> str:
    """Resolve the permanent local/GCP backend selector."""

    env = os.environ if environment is None else environment
    backend = env.get("SPARK_BACKEND") or env.get("SPARK_CONTOUR") or "local"
    backend = backend.strip().lower()
    if backend not in {"local", "gcp"}:
        raise ConfigurationError("SPARK_BACKEND must be exactly local or gcp")
    return backend


def resolve_catalog_alias(environment: Mapping[str, str] | None = None) -> str:
    """Resolve the current alias while keeping the legacy variable usable."""

    env = os.environ if environment is None else environment
    alias = (
        env.get("ICEBERG_SPARK_CATALOG_ALIAS")
        or env.get("ICEBERG_CATALOG_NAME")
        or CATALOG_ALIAS
    )
    if not _SAFE_IDENTIFIER.fullmatch(alias):
        raise ConfigurationError("ICEBERG_SPARK_CATALOG_ALIAS is not a safe identifier")
    return alias


@dataclass(frozen=True)
class SparkCatalogConfig:
    """REST catalog configuration without checkpoint credentials."""

    backend: str
    catalog_uri: str
    catalog_alias: str
    warehouse: str
    file_io_impl: str
    rest_auth_type: str | None
    billing_project_id: str | None
    object_store_endpoint: str
    object_store_region: str
    object_store_path_style: bool
    polaris_client_id: str | None
    polaris_client_secret: str | None

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
        backend: str | None = None,
    ) -> SparkCatalogConfig:
        env = os.environ if environment is None else environment
        selected_backend = resolve_backend(env) if backend is None else backend
        catalog_alias = resolve_catalog_alias(env)

        if selected_backend == "local":
            catalog_uri = _validate_service_url(
                env.get("ICEBERG_CATALOG_URI", DEFAULT_CATALOG_URI),
                "ICEBERG_CATALOG_URI",
            )
            warehouse = env.get("ICEBERG_WAREHOUSE", DEFAULT_CATALOG_NAME)
            if warehouse != DEFAULT_CATALOG_NAME:
                raise ConfigurationError(
                    "local ICEBERG_WAREHOUSE must be olist_lakehouse"
                )
            endpoint = _validate_service_url(
                env.get("OBJECT_STORE_ENDPOINT", DEFAULT_OBJECT_STORE_ENDPOINT),
                "OBJECT_STORE_ENDPOINT",
            )
            region = env.get("OBJECT_STORE_REGION", DEFAULT_OBJECT_STORE_REGION)
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", region):
                raise ConfigurationError("OBJECT_STORE_REGION has invalid syntax")
            client_id = _secret_from_file(env, "POLARIS_SPARK_CLIENT_ID_FILE")
            if ":" in client_id:
                raise ConfigurationError("Polaris client ID must not contain ':'")
            return cls(
                backend=selected_backend,
                catalog_uri=catalog_uri,
                catalog_alias=catalog_alias,
                warehouse=warehouse,
                file_io_impl="org.apache.iceberg.aws.s3.S3FileIO",
                rest_auth_type=None,
                billing_project_id=None,
                object_store_endpoint=endpoint,
                object_store_region=region,
                object_store_path_style=_boolean(env, "OBJECT_STORE_PATH_STYLE", True),
                polaris_client_id=client_id,
                polaris_client_secret=_secret_from_file(
                    env, "POLARIS_SPARK_CLIENT_SECRET_FILE"
                ),
            )

        catalog_uri = _validate_service_url(
            env.get("ICEBERG_CATALOG_URI", DEFAULT_GCP_CATALOG_URI),
            "ICEBERG_CATALOG_URI",
        )
        warehouse = _validate_gcp_warehouse(_required(env, "ICEBERG_WAREHOUSE"))
        billing_project_id = (
            env.get("GCP_LAKEHOUSE_PROJECT_ID")
            or env.get("GCP_PROJECT_ID")
            or env.get("GOOGLE_CLOUD_PROJECT")
        )
        if not billing_project_id or not re.fullmatch(
            r"[a-z][a-z0-9-]{4,28}[a-z0-9]", billing_project_id
        ):
            raise ConfigurationError(
                "GCP_LAKEHOUSE_PROJECT_ID must contain a valid project ID"
            )
        return cls(
            backend=selected_backend,
            catalog_uri=catalog_uri,
            catalog_alias=catalog_alias,
            warehouse=warehouse,
            file_io_impl=GCP_FILE_IO,
            rest_auth_type=GCP_AUTH_MANAGER,
            billing_project_id=billing_project_id,
            object_store_endpoint="",
            object_store_region=env.get("GCP_REGION", "us-east1"),
            object_store_path_style=False,
            polaris_client_id=None,
            polaris_client_secret=None,
        )

    def spark_properties(self) -> dict[str, str]:
        catalog_prefix = f"spark.sql.catalog.{self.catalog_alias}"
        properties = {
            "spark.redaction.regex": _REDACTION_REGEX,
            "spark.sql.redaction.options.regex": _REDACTION_REGEX,
            "spark.sql.extensions": (
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
            ),
            "spark.sql.defaultCatalog": self.catalog_alias,
            catalog_prefix: "org.apache.iceberg.spark.SparkCatalog",
            f"{catalog_prefix}.type": "rest",
            f"{catalog_prefix}.uri": self.catalog_uri,
            f"{catalog_prefix}.warehouse": self.warehouse,
            f"{catalog_prefix}.header.X-Iceberg-Access-Delegation": (
                "vended-credentials"
            ),
            f"{catalog_prefix}.io-impl": self.file_io_impl,
            "spark.sql.session.timeZone": "UTC",
            "spark.sql.shuffle.partitions": "4",
        }
        if self.backend == "local":
            assert self.polaris_client_id is not None
            assert self.polaris_client_secret is not None
            properties.update(
                {
                    f"{catalog_prefix}.credential": (
                        f"{self.polaris_client_id}:{self.polaris_client_secret}"
                    ),
                    f"{catalog_prefix}.scope": "PRINCIPAL_ROLE:ALL",
                    f"{catalog_prefix}.oauth2-server-uri": (
                        f"{self.catalog_uri}/v1/oauth/tokens"
                    ),
                    f"{catalog_prefix}.token-refresh-enabled": "false",
                    f"{catalog_prefix}.client.region": self.object_store_region,
                }
            )
        else:
            assert self.rest_auth_type is not None
            assert self.billing_project_id is not None
            properties.update(
                {
                    f"{catalog_prefix}.rest.auth.type": self.rest_auth_type,
                    f"{catalog_prefix}.header.x-goog-user-project": (
                        self.billing_project_id
                    ),
                }
            )
        return properties


@dataclass(frozen=True)
class SparkPlatformConfig:
    """Complete, validated properties needed by Spark streaming drivers."""

    catalog: SparkCatalogConfig
    checkpoint_root: str
    object_store_credential_provider: str
    checkpoint_access_key: str
    checkpoint_secret_key: str
    adc_path: str | None
    source_time_zone: str

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> SparkPlatformConfig:
        env = os.environ if environment is None else environment
        backend = resolve_backend(env)
        source_time_zone = _source_time_zone(env)
        catalog = SparkCatalogConfig.from_environment(env, backend=backend)
        if backend == "local":
            checkpoint_root = _validate_checkpoint_root(
                env.get("SPARK_CHECKPOINT_ROOT", DEFAULT_CHECKPOINT_ROOT)
            )
            provider = env.get(
                "OBJECT_STORE_CREDENTIAL_PROVIDER", DEFAULT_S3A_CREDENTIAL_PROVIDER
            )
            if provider != DEFAULT_S3A_CREDENTIAL_PROVIDER:
                raise ConfigurationError(
                    "local checkpoint access requires SimpleAWSCredentialsProvider"
                )
            return cls(
                catalog=catalog,
                checkpoint_root=checkpoint_root,
                object_store_credential_provider=provider,
                checkpoint_access_key=_secret_from_file(
                    env, "OBJECT_STORE_ACCESS_KEY_FILE"
                ),
                checkpoint_secret_key=_secret_from_file(
                    env, "OBJECT_STORE_SECRET_KEY_FILE"
                ),
                adc_path=None,
                source_time_zone=source_time_zone,
            )

        checkpoint_bucket = _required(env, "GCP_CHECKPOINT_BUCKET")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]", checkpoint_bucket):
            raise ConfigurationError(
                "GCP_CHECKPOINT_BUCKET contains an invalid bucket name"
            )
        checkpoint_root = _validate_gcs_uri(
            env.get("SPARK_CHECKPOINT_ROOT", f"gs://{checkpoint_bucket}"),
            "SPARK_CHECKPOINT_ROOT",
        )
        if urlsplit(checkpoint_root).hostname != checkpoint_bucket:
            raise ConfigurationError(
                "SPARK_CHECKPOINT_ROOT must stay inside GCP_CHECKPOINT_BUCKET"
            )
        adc_path = _validate_adc_path(_required(env, "GOOGLE_APPLICATION_CREDENTIALS"))
        return cls(
            catalog=catalog,
            checkpoint_root=checkpoint_root,
            object_store_credential_provider="APPLICATION_DEFAULT",
            checkpoint_access_key="",
            checkpoint_secret_key="",
            adc_path=adc_path,
            source_time_zone=source_time_zone,
        )

    def spark_properties(self, mode: str = "streaming") -> dict[str, str]:
        props = self.catalog.spark_properties()
        props["spark.olist.source.time.zone"] = self.source_time_zone
        if mode == "maintenance":
            return props
        if mode != "streaming":
            raise ConfigurationError(f"invalid runtime mode: {mode!r}")

        if self.catalog.backend == "gcp":
            assert self.catalog.billing_project_id is not None
            return {
                **props,
                "spark.hadoop.fs.gs.impl": GCP_CHECKPOINT_FILESYSTEM,
                "spark.hadoop.fs.AbstractFileSystem.gs.impl": (
                    GCP_CHECKPOINT_ABSTRACT_FILESYSTEM
                ),
                "spark.hadoop.fs.gs.auth.type": "APPLICATION_DEFAULT",
                "spark.hadoop.fs.gs.project.id": self.catalog.billing_project_id,
                "spark.hadoop.fs.gs.client.type": "HTTP_API_CLIENT",
                "spark.olist.checkpoint.root": self.checkpoint_root,
            }

        props.update(
            {
                "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                "spark.hadoop.fs.s3a.endpoint": self.catalog.object_store_endpoint,
                "spark.hadoop.fs.s3a.endpoint.region": self.catalog.object_store_region,
                "spark.hadoop.fs.s3a.path.style.access": str(
                    self.catalog.object_store_path_style
                ).lower(),
                "spark.hadoop.fs.s3a.connection.ssl.enabled": str(
                    self.catalog.object_store_endpoint.startswith("https://")
                ).lower(),
                "spark.hadoop.fs.s3a.aws.credentials.provider": (
                    self.object_store_credential_provider
                ),
                "spark.hadoop.fs.s3a.access.key": self.checkpoint_access_key,
                "spark.hadoop.fs.s3a.secret.key": self.checkpoint_secret_key,
                "spark.olist.checkpoint.root": self.checkpoint_root,
            }
        )
        return props
