"""Static validation for the versioned Phase 3 NiFi flow and CDC schemas."""

from __future__ import annotations

import json
from pathlib import Path

from fastavro import parse_schema

ROOT = Path(__file__).resolve().parents[2]
FLOW_PATH = ROOT / "streaming/nifi/flow/olist-cdc-v1.json"
PARAMETERS_PATH = ROOT / "streaming/nifi/parameters/local.template.json"
SCHEMA_ROOT = ROOT / "streaming/schemas"

TABLES = {
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
}
REQUIRED_METADATA = {
    "_event_id",
    "_op",
    "_source_ts",
    "_source_lsn",
    "_tx_id",
    "_tx_order",
    "_topic",
    "_partition",
    "_offset",
    "_kafka_ts",
    "_key_schema_id",
    "_schema_id",
    "_nifi_written_at",
}
COVERAGE_REQUIRED = {
    "contract_version",
    "flow_version",
    "kind",
    "table",
    "topic",
    "partition",
    "consumed_offset_ranges",
    "business_event_offset_ranges",
    "tombstone_offset_ranges",
    "consumed_row_count",
    "business_event_count",
    "tombstone_count",
    "closed_at",
    "landing_manifest",
    "landing_object",
}


def main() -> int:
    errors: list[str] = []
    flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
    parameters = json.loads(PARAMETERS_PATH.read_text(encoding="utf-8"))
    processors = {item["name"]: item for item in flow["processors"]}
    services = {item["name"]: item for item in flow["controller_services"]}

    required_processors = {
        "Consume Olist CDC",
        "Build Landing Avro",
        "Build Normalized Avro",
        "Merge Landing",
        "Merge Normalized",
        "Convert Normalized to Parquet",
        "Put Landing Immutable",
        "Put Normalized Immutable",
        "Build DLQ Envelope",
        "Put Quarantine Immutable",
        "Publish Table DLQ",
    }
    if missing := required_processors - set(processors):
        errors.append(f"missing processors: {', '.join(sorted(missing))}")
    if set(services) != {
        "kafka-connection",
        "avro-reader",
        "avro-writer",
        "parquet-writer",
    }:
        errors.append("controller service set is incomplete")

    consume = processors["Consume Olist CDC"]["properties"]
    if consume.get("Commit Offsets") != "true":
        errors.append(
            "ConsumeKafka must commit after durable NiFi repository acceptance"
        )
    if consume.get("Key Attribute Encoding") != "hex":
        errors.append("Kafka keys must be preserved as hex-encoded bytes")
    topics = {item.rsplit(".", 1)[-1] for item in consume["Topics"].split(",")}
    if topics != TABLES:
        errors.append("ConsumeKafka topic set does not match the CDC table contract")

    for name in ("Merge Landing", "Merge Normalized"):
        properties = processors[name]["properties"]
        if properties.get("Max Bin Age") != "#{max_bin_age}":
            errors.append(f"{name} does not use the bounded bin-age parameter")
        if properties.get("Maximum Bin Size") != "#{maximum_bin_size}":
            errors.append(f"{name} does not enforce maximum bin size")

    names = set(processors)
    for source, _relationship, destination in flow["connections"]:
        if source not in names or destination not in names:
            errors.append(
                f"connection references an unknown processor: {source} -> {destination}"
            )

    serialized = json.dumps(flow).lower()
    if any(
        secret in serialized for secret in ("password=", "secret_key", "minioadmin123")
    ):
        errors.append("flow contains a plaintext secret")
    if parameters.get("max_bin_age") != "45 sec":
        errors.append(
            "local max bin age must leave upload time inside the 60-second SLO"
        )

    for table in sorted(TABLES):
        path = SCHEMA_ROOT / "normalized" / table / "v1.avsc"
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            parse_schema(schema)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid schema for {table}: {exc}")
            continue
        fields = {field["name"] for field in schema["fields"]}
        if missing := REQUIRED_METADATA - fields:
            errors.append(
                f"{table} schema missing metadata: {', '.join(sorted(missing))}"
            )
    try:
        parse_schema(
            json.loads(
                (SCHEMA_ROOT / "cdc-landing/v1.avsc").read_text(encoding="utf-8")
            )
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid landing schema: {exc}")

    try:
        coverage_schema = json.loads(
            (SCHEMA_ROOT / "cdc-coverage/v1.schema.json").read_text(encoding="utf-8")
        )
        if coverage_schema.get("$schema") != (
            "https://json-schema.org/draft/2020-12/schema"
        ):
            errors.append("coverage schema must use JSON Schema draft 2020-12")
        if set(coverage_schema.get("required", [])) != COVERAGE_REQUIRED:
            errors.append("coverage schema required fields do not match the v1 contract")
        properties = coverage_schema.get("properties", {})
        if properties.get("contract_version", {}).get("const") != 1:
            errors.append("coverage contract_version must be fixed at 1")
        if properties.get("kind", {}).get("const") != "coverage":
            errors.append("coverage kind must be fixed at coverage")
        if properties.get("consumed_offset_ranges", {}).get("$ref") != (
            "#/$defs/nonEmptyRanges"
        ):
            errors.append("coverage consumed ranges must be non-empty")
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        errors.append(f"invalid coverage schema: {exc}")

    describe_source = (ROOT / "streaming/nifi/python/DescribeAvroBatch.py").read_text(
        encoding="utf-8"
    )
    put_source = (
        ROOT / "streaming/nifi/python/PutImmutableS3Object.py"
    ).read_text(encoding="utf-8")
    for attribute in (
        "cdc.coverage.key",
        "cdc.business_offset_ranges",
        "cdc.tombstone_offset_ranges",
    ):
        if attribute not in describe_source:
            errors.append(f"DescribeAvroBatch does not publish {attribute}")
    for field in ("landing_manifest", "landing_object", "coverage_key"):
        if field not in put_source:
            errors.append(f"immutable S3 writer does not publish coverage {field}")

    if errors:
        print("NiFi flow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("NiFi flow, parameters, typed CDC schemas, and coverage contract are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
