"""Prove registry-side BACKWARD_TRANSITIVE enforcement on an isolated subject."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid


def post_schema(base_url: str, subject: str, schema: dict[str, object]) -> int:
    encoded = urllib.parse.quote(subject, safe="")
    body = json.dumps(
        {"schemaType": "AVRO", "schema": json.dumps(schema, separators=(",", ":"))}
    ).encode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/apis/ccompat/v7/subjects/{encoded}/versions",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()
            return response.status
    except urllib.error.HTTPError as exc:
        exc.read()
        return exc.code


def schema(fields: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": "record",
        "name": "CompatibilityProbe",
        "namespace": "io.olist.stage2",
        "fields": fields,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry-url", default="http://localhost:8081")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subject = f"olist-stage2-compatibility-{uuid.uuid4()}"
    v1 = schema([{"name": "entity_id", "type": "string"}])
    v2 = schema(
        [
            {"name": "entity_id", "type": "string"},
            {"name": "note", "type": ["null", "string"], "default": None},
        ]
    )
    incompatible = schema(
        [
            {"name": "entity_id", "type": "int"},
            {"name": "note", "type": ["null", "string"], "default": None},
        ]
    )
    statuses = {
        "initial": post_schema(args.registry_url, subject, v1),
        "compatible_nullable_default": post_schema(args.registry_url, subject, v2),
        "incompatible_type": post_schema(args.registry_url, subject, incompatible),
    }
    if statuses["initial"] not in {200, 201}:
        print(f"Initial schema registration failed: {statuses}", file=sys.stderr)
        return 1
    if statuses["compatible_nullable_default"] not in {200, 201}:
        print(f"Compatible schema was rejected: {statuses}", file=sys.stderr)
        return 1
    if statuses["incompatible_type"] not in {409, 422}:
        print(f"Incompatible schema was not rejected: {statuses}", file=sys.stderr)
        return 1
    print(json.dumps({"subject": subject, "statuses": statuses}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
