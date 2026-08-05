"""Validate a live Kafka broker against the fixed CDC topic manifest."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(__file__).with_name("topics.json")
ACCEPTED_BROKER_DEFAULTS = {"min.insync.replicas": "1"}
TOPIC_LINE = re.compile(
    r"^Topic:\s+(?P<name>\S+)\s+TopicId:.*PartitionCount:\s+"
    r"(?P<partitions>\d+)\s+ReplicationFactor:\s+(?P<replication>\d+)"
)


@dataclass(frozen=True)
class TopicState:
    name: str
    partitions: int
    replication_factor: int
    config: dict[str, str]


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("auto_create_topics") is not False:
        raise ValueError("topic manifest must require disabled auto topic creation")
    topics = manifest.get("topics")
    if not isinstance(topics, list) or len(topics) != 15:
        raise ValueError("topic manifest must contain exactly 15 topics")
    names = [topic.get("name") for topic in topics if isinstance(topic, dict)]
    if len(names) != len(topics) or len(set(names)) != len(names):
        raise ValueError("topic manifest names must be unique strings")
    dangerous = manifest.get("dangerous_unmanifested_configs")
    if (
        not isinstance(dangerous, list)
        or not dangerous
        or not all(isinstance(item, str) and item for item in dangerous)
        or len(dangerous) != len(set(dangerous))
    ):
        raise ValueError(
            "dangerous_unmanifested_configs must be a unique non-empty string array"
        )
    declared_config_keys = {
        key
        for topic in topics
        if isinstance(topic, dict) and isinstance(topic.get("config"), dict)
        for key in topic["config"]
    }
    if not declared_config_keys.issubset(set(dangerous)):
        raise ValueError("every declared topic config must be drift-protected")
    return manifest


def parse_describe(output: str) -> dict[str, TopicState]:
    states: dict[str, TopicState] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        match = TOPIC_LINE.match(line)
        if match is None:
            continue
        config_text = line.split("Configs:", maxsplit=1)[1].strip()
        config: dict[str, str] = {}
        for item in config_text.split(","):
            key, separator, value = item.partition("=")
            if separator:
                config[key.strip()] = value.strip()
        name = match.group("name")
        states[name] = TopicState(
            name=name,
            partitions=int(match.group("partitions")),
            replication_factor=int(match.group("replication")),
            config=config,
        )
    return states


def validate_states(
    manifest: dict[str, Any], states: dict[str, TopicState]
) -> list[str]:
    errors: list[str] = []
    expected_names = {topic["name"] for topic in manifest["topics"]}
    actual_names = set(states)
    for name in sorted(expected_names - actual_names):
        errors.append(f"missing topic: {name}")
    for name in sorted(actual_names - expected_names):
        if name.startswith("olist_cdc") or name.startswith("olist_connect"):
            errors.append(f"unexpected managed topic: {name}")

    expected_replication = int(manifest["replication_factor"])
    dangerous_configs = set(manifest["dangerous_unmanifested_configs"])
    for topic in manifest["topics"]:
        state = states.get(topic["name"])
        if state is None:
            continue
        if state.partitions != topic["partitions"]:
            errors.append(
                f"{state.name}: partitions={state.partitions}, "
                f"expected={topic['partitions']}"
            )
        if state.replication_factor != expected_replication:
            errors.append(
                f"{state.name}: replication_factor={state.replication_factor}, "
                f"expected={expected_replication}"
            )
        for key, expected in topic["config"].items():
            actual = state.config.get(key)
            if actual != expected:
                errors.append(f"{state.name}: {key}={actual!r}, expected={expected!r}")
        for key in sorted(set(state.config) & dangerous_configs - set(topic["config"])):
            if ACCEPTED_BROKER_DEFAULTS.get(key) == state.config[key]:
                continue
            errors.append(
                f"{state.name}: dangerous unmanifested override {key}="
                f"{state.config[key]!r}"
            )
    return errors


def describe_topics(bootstrap_server: str, kafka_topics: Path) -> str:
    completed = subprocess.run(
        [
            str(kafka_topics),
            "--bootstrap-server",
            bootstrap_server,
            "--describe",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.stdout


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-server", default="kafka:29092")
    parser.add_argument(
        "--kafka-topics",
        type=Path,
        default=Path("/opt/kafka/bin/kafka-topics.sh"),
    )
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = load_manifest(args.manifest)
    states = parse_describe(describe_topics(args.bootstrap_server, args.kafka_topics))
    errors = validate_states(manifest, states)
    if errors:
        print("Kafka topic contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Kafka topic contract is valid: 15 topics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
