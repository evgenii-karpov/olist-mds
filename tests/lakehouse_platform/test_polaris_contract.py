from __future__ import annotations

import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POLARIS_DIRECTORY = REPOSITORY_ROOT / "infra" / "polaris"
APPROVED_POLARIS_1_6_GRANTS = {
    "CATALOG_READ_PROPERTIES",
    "NAMESPACE_LIST",
    "NAMESPACE_READ_PROPERTIES",
    "TABLE_CREATE",
    "TABLE_LIST",
    "TABLE_READ_PROPERTIES",
    "TABLE_WRITE_PROPERTIES",
    "TABLE_READ_DATA",
    "TABLE_WRITE_DATA",
}


def _read(relative_path: str) -> str:
    return (POLARIS_DIRECTORY / relative_path).read_text(encoding="utf-8")


def _policy(relative_path: str) -> dict[str, object]:
    return json.loads(_read(relative_path))


def _policy_resources(policy: dict[str, object]) -> set[str]:
    resources: set[str] = set()
    for statement in policy["Statement"]:  # type: ignore[index]
        resources.update(statement["Resource"])  # type: ignore[index]
    return resources


def _expected_rbac() -> dict[str, object]:
    return json.loads(_read("bootstrap/expected-rbac.json"))


def _setup_role_privileges(setup: str, catalog_role: str) -> set[str]:
    match = re.search(
        rf"^      {re.escape(catalog_role)}:\n"
        r".*?^        privileges:\n"
        r"          catalog:\n"
        r"(?P<privileges>(?:            - [A-Z0-9_]+\n)+)",
        setup,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing catalog privileges for {catalog_role}"
    return set(re.findall(r"^            - ([A-Z0-9_]+)$", match["privileges"], re.M))


def test_polaris_images_and_cli_are_pinned_to_1_6_0() -> None:
    assert "apache/polaris:1.6.0" in _read("server/Dockerfile")
    assert "apache/polaris-admin-tool:1.6.0" in _read("admin/Dockerfile")
    bootstrap_dockerfile = _read("bootstrap/Dockerfile")
    assert "python:3.12.12-alpine3.22" in bootstrap_dockerfile
    assert "ARG POLARIS_VERSION=1.6.0" in bootstrap_dockerfile
    assert '"apache-polaris==${POLARIS_VERSION}"' in bootstrap_dockerfile
    assert "apache-polaris>=" not in bootstrap_dockerfile


def test_setup_declares_the_exact_catalog_storage_and_namespaces() -> None:
    setup = _read("bootstrap/setup.yaml")

    assert "name: olist_lakehouse" in setup
    assert "default_base_location: s3://olist-lakehouse/warehouse" in setup
    assert "allowed_locations:\n      - s3://olist-lakehouse/warehouse" in setup
    assert "endpoint: http://minio:9000" in setup
    assert "endpoint_internal: http://minio:9000" in setup
    assert "sts_endpoint: http://minio:9000" in setup
    assert "region: us-east-1" in setup
    assert "sts_unavailable" not in setup
    assert "kms_unavailable: true" in setup
    assert "path_style_access: true" in setup
    assert setup.count("      - bronze") == 1
    assert setup.count("      - silver") == 1
    assert setup.count("      - reference") == 1
    assert setup.count("      - audit") == 1
    assert "gold" not in setup


def test_setup_declares_separate_principals_roles_and_least_privilege_grants() -> None:
    setup = _read("bootstrap/setup.yaml")
    expected_rbac = _expected_rbac()
    principals = expected_rbac["principals"]
    assert isinstance(principals, dict)

    for principal in principals:
        assert f"  {principal}:" in setup
    for contract in principals.values():
        assert isinstance(contract, dict)
        principal_role = contract["principal_role"]
        catalog_role = contract["catalog_role"]
        privileges = contract["catalog_privileges"]
        assert isinstance(principal_role, str)
        assert isinstance(catalog_role, str)
        assert isinstance(privileges, list)
        assert principal_role in setup
        assert _setup_role_privileges(setup, catalog_role) == set(privileges)
        assert set(privileges) <= APPROVED_POLARIS_1_6_GRANTS

    forbidden_fragments = (
        "DROP",
        "FULL_METADATA",
        "MANAGE_ACCESS",
        "CATALOG_MANAGE_CONTENT",
    )
    assert all(fragment not in setup for fragment in forbidden_fragments)

    clickhouse = principals["clickhouse_reader"]
    spark = principals["spark_writer"]
    airflow = principals["airflow_maintenance"]
    assert isinstance(clickhouse, dict)
    assert isinstance(spark, dict)
    assert isinstance(airflow, dict)
    assert set(clickhouse["catalog_privileges"]) == {
        "CATALOG_READ_PROPERTIES",
        "NAMESPACE_LIST",
        "NAMESPACE_READ_PROPERTIES",
        "TABLE_LIST",
        "TABLE_READ_PROPERTIES",
        "TABLE_READ_DATA",
    }
    assert "TABLE_CREATE" in spark["catalog_privileges"]
    assert "TABLE_CREATE" not in airflow["catalog_privileges"]


def test_bootstrap_is_idempotent_and_credentials_fail_closed() -> None:
    bootstrap = _read("bootstrap/bootstrap.sh")

    assert "polaris_cli setup apply" in bootstrap
    assert "Polaris DB contains" in bootstrap
    assert "credential volume contains" in bootstrap
    assert "partial credentials" in bootstrap
    assert "full reset required" in bootstrap
    assert "chmod 0600" in bootstrap
    assert "ensure_principal spark_writer polaris-spark" in bootstrap
    assert "ensure_principal clickhouse_reader polaris-clickhouse" in bootstrap
    assert "ensure_principal airflow_maintenance polaris-airflow" in bootstrap
    assert "POLARIS_RBAC_CONTRACT_FILE" in bootstrap
    assert "catalog-roles list --catalog" in bootstrap
    assert "principal-roles list --principal" in bootstrap
    assert "polaris_cli privileges list" in bootstrap
    assert "runtime authentication/authorization smoke failed" in bootstrap
    assert 'catalogs get "${catalog}"' in bootstrap
    assert 'namespaces get --catalog "${catalog}"' in bootstrap
    assert "--client-secret" not in bootstrap
    assert bootstrap.index(
        'polaris_cli setup apply "${setup_file}"'
    ) < bootstrap.rindex("\nverify_rbac_contract\n")

    bootstrap_dockerfile = _read("bootstrap/Dockerfile")
    assert "expected-rbac.json /opt/olist/polaris/expected-rbac.json" in (
        bootstrap_dockerfile
    )

    preparer = _read("credentials/prepare.sh")
    assert "bootstrap-admin-client-id" in preparer
    assert "bootstrap-admin-client-secret" in preparer
    assert "partial Polaris credential pair" in preparer
    assert "chmod 0600" in preparer
    assert "od -An -N32 -tx1 /dev/urandom" in preparer


def test_polaris_uses_relational_jdbc_and_file_sourced_credentials() -> None:
    properties = _read("server/application.properties")
    server = _read("server/start.sh")
    admin = _read("admin/bootstrap-jdbc.sh")
    postgres = _read("postgres/010_create_polaris_database.sh")

    assert "polaris.persistence.type=relational-jdbc" in properties
    assert "polaris.persistence.relational.jdbc.database-type=postgresql" in properties
    assert "polaris.authentication.type=internal" in properties
    assert "ALLOW_INSECURE_STORAGE_TYPES" in properties
    assert "jdbc:postgresql://platform-postgres:5432/polaris" in server
    assert "POLARIS_ROOT_CLIENT_SECRET_FILE" in server
    assert "POLARIS_WAREHOUSE_SECRET_KEY_FILE" in server
    assert "POLARIS_BOOTSTRAP_CREDENTIALS" in server
    assert "--credentials-file" in admin
    assert "--realm=POLARIS" not in admin
    assert "chmod 0600" in admin
    assert "bootstrap" in admin
    assert "CREATE DATABASE" in postgres
    assert "ALTER ROLE" in postgres
    assert "POLARIS_DB_PASSWORD_FILE" in postgres


def test_minio_policies_physically_isolate_warehouse_and_checkpoints() -> None:
    warehouse = _policy("minio/warehouse-policy.json")
    checkpoints = _policy("minio/checkpoints-policy.json")
    warehouse_resources = _policy_resources(warehouse)
    checkpoint_resources = _policy_resources(checkpoints)

    assert warehouse_resources == {
        "arn:aws:s3:::olist-lakehouse",
        "arn:aws:s3:::olist-lakehouse/warehouse/*",
    }
    assert checkpoint_resources == {
        "arn:aws:s3:::olist-checkpoints",
        "arn:aws:s3:::olist-checkpoints/*",
    }
    assert not any("olist-checkpoints" in value for value in warehouse_resources)
    assert not any("olist-lakehouse" in value for value in checkpoint_resources)
    warehouse_listing = warehouse["Statement"][0]  # type: ignore[index]
    assert warehouse_listing["Condition"]["StringLike"]["s3:prefix"] == [  # type: ignore[index]
        "warehouse",
        "warehouse/*",
    ]


def test_minio_initializer_creates_both_buckets_and_private_credentials() -> None:
    initializer = _read("minio/init.sh")

    assert "mc mb --ignore-existing olist/olist-lakehouse" in initializer
    assert "mc mb --ignore-existing olist/olist-checkpoints" in initializer
    assert "mc anonymous set none olist/olist-lakehouse" in initializer
    assert "mc anonymous set none olist/olist-checkpoints" in initializer
    assert "ensure_identity polaris-warehouse" in initializer
    assert "olist-lakehouse/warehouse" in initializer
    assert "ensure_identity spark-checkpoints" in initializer
    assert "chmod 0600" in initializer
    assert "full reset required" in initializer
