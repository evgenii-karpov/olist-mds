#!/usr/bin/env python
"""Fetch a single plaintext secret from AWS Secrets Manager."""

from __future__ import annotations

import argparse
import json
import sys

import boto3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a secret string from AWS Secrets Manager."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="Secret name or ARN to fetch from AWS Secrets Manager.",
    )
    parser.add_argument(
        "--json-key",
        help="Optional JSON key to extract when SecretString contains an object.",
    )
    return parser.parse_args()


def resolve_secret_value(secret_string: str, json_key: str | None) -> str:
    if not json_key:
        return secret_string

    payload = json.loads(secret_string)
    if not isinstance(payload, dict):
        raise ValueError("SecretString must be a JSON object when --json-key is used")
    if json_key not in payload:
        raise KeyError(f"JSON key {json_key!r} not found in secret payload")

    value = payload[json_key]
    if isinstance(value, str):
        return value
    return json.dumps(value, separators=(",", ":"))


def main() -> int:
    args = parse_args()
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=args.secret_id)
    secret_string = response.get("SecretString")
    if secret_string is None:
        raise ValueError("Only SecretString secrets are supported")

    sys.stdout.write(resolve_secret_value(secret_string, args.json_key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
