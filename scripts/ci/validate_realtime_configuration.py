"""Validate Phase 0 realtime configuration contracts without live services."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERSION_MANIFEST = PROJECT_ROOT / "streaming" / "runtime-versions.json"
POLICY_FILE = PROJECT_ROOT / "streaming" / "schemas" / "compatibility-policy.json"
TOPIC_MANIFEST = PROJECT_ROOT / "streaming" / "kafka" / "topics.json"
CONNECTOR_TEMPLATE = PROJECT_ROOT / "streaming" / "connect" / "olist-postgres-cdc.json"

REQUIRED_COMPONENTS = {
    "airflow",
    "kafka",
    "debezium_connect",
    "nifi",
    "apicurio_registry",
    "prometheus",
    "alertmanager",
    "grafana",
    "alloy",
    "loki",
    "node_exporter",
    "postgres_exporter",
    "statsd_exporter",
    "cadvisor",
}

REQUIRED_DIRECTORIES = (
    "infra/oltp",
    "infra/postgres/realtime",
    "infra/redshift/realtime",
    "infra/aws/realtime",
    "streaming/kafka",
    "streaming/connect",
    "streaming/nifi",
    "streaming/schemas",
    "observability/prometheus",
    "observability/grafana",
    "observability/alertmanager",
    "observability/alloy",
    "observability/loki",
    "scripts/simulation",
    "scripts/cdc",
)


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot load JSON contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON contract must contain an object: {path}")
    return value


def validate_version_manifest(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("runtime-versions.json schema_version must be 1")

    components = manifest.get("components")
    if not isinstance(components, dict):
        return [*errors, "runtime-versions.json components must be an object"]

    missing = sorted(REQUIRED_COMPONENTS - set(components))
    if missing:
        errors.append(f"runtime-versions.json is missing: {', '.join(missing)}")

    for name, component in components.items():
        if not isinstance(component, dict):
            errors.append(f"component {name!r} must be an object")
            continue
        version = component.get("version")
        image = component.get("image")
        if not isinstance(version, str) or not version.strip():
            errors.append(f"component {name!r} has no exact version")
        if not isinstance(image, str) or ":" not in image:
            errors.append(f"component {name!r} has no tagged image")
        elif image.rsplit(":", maxsplit=1)[1].lower() in {"latest", "stable"}:
            errors.append(f"component {name!r} uses a floating image tag: {image}")
    return errors


def validate_policy(policy: dict[str, object]) -> list[str]:
    expected = {
        "format": "AVRO",
        "compatibility": "BACKWARD_TRANSITIVE",
        "file_layout": "<subject>/v<positive-integer>.avsc",
    }
    return [
        f"compatibility policy {key!r} must be {value!r}"
        for key, value in expected.items()
        if policy.get(key) != value
    ]


def validate_stage2_contracts() -> list[str]:
    errors: list[str] = []
    topics = load_json(TOPIC_MANIFEST).get("topics")
    if not isinstance(topics, list):
        errors.append("topics.json topics must be an array")
    else:
        names = [topic.get("name") for topic in topics if isinstance(topic, dict)]
        if len(names) != len(topics) or len(names) != len(set(names)):
            errors.append("topics.json topic names must be present and unique")

    connector = load_json(CONNECTOR_TEMPLATE)
    config = connector.get("config")
    if connector.get("name") != "olist-postgres-cdc" or not isinstance(config, dict):
        return [*errors, "connector template has an invalid name or config"]
    expected = {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "plugin.name": "pgoutput",
        "tasks.max": "1",
        "topic.prefix": "olist_cdc",
        "slot.name": "olist_cdc_slot",
        "publication.name": "olist_cdc_publication",
        "publication.autocreate.mode": "disabled",
        "snapshot.mode": "initial",
        "topic.heartbeat.prefix": "olist_cdc.heartbeat",
        "schema.history.internal.kafka.topic": "olist_cdc.schema_history",
        "database.password": "${OLTP_CDC_READER_PASSWORD}",
    }
    errors.extend(
        f"connector config {key!r} must be {value!r}"
        for key, value in expected.items()
        if config.get(key) != value
    )
    return errors


def main() -> int:
    errors = validate_version_manifest(load_json(VERSION_MANIFEST))
    errors.extend(validate_policy(load_json(POLICY_FILE)))
    errors.extend(validate_stage2_contracts())
    for relative_path in REQUIRED_DIRECTORIES:
        if not (PROJECT_ROOT / relative_path).is_dir():
            errors.append(f"required directory is missing: {relative_path}")

    if errors:
        print("Realtime configuration validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Realtime configuration scaffolding is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
