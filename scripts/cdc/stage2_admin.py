"""Finite administration and validation commands for the local CDC stack."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOPIC_MANIFEST = PROJECT_ROOT / "streaming" / "kafka" / "topics.json"
CONNECTOR_TEMPLATE = PROJECT_ROOT / "streaming" / "connect" / "olist-postgres-cdc.json"


def request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    accepted: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        status = exc.code
    if status not in accepted:
        raise RuntimeError(f"{method} {url} returned HTTP {status}")
    if not payload:
        return status, None
    return status, json.loads(payload)


def wait_http(url: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            request_json(url)
            return
        except (OSError, RuntimeError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def configure_registry(registry_url: str) -> None:
    base = registry_url.rstrip("/")
    wait_http(f"{base}/apis/registry/v3/system/info", 120)
    rule_url = f"{base}/apis/registry/v3/admin/rules/COMPATIBILITY"
    status, _ = request_json(rule_url, accepted=(200, 404))
    body = {"ruleType": "COMPATIBILITY", "config": "BACKWARD_TRANSITIVE"}
    if status == 404:
        request_json(
            f"{base}/apis/registry/v3/admin/rules",
            method="POST",
            body=body,
            accepted=(204,),
        )
    else:
        request_json(
            rule_url,
            method="PUT",
            body=body,
            accepted=(200, 204),
        )
    _, rule = request_json(rule_url)
    if rule.get("config") != "BACKWARD_TRANSITIVE":
        raise RuntimeError(f"Unexpected registry compatibility rule: {rule}")
    print("Registry global compatibility is BACKWARD_TRANSITIVE.")


def render_connector(password_file: Path) -> dict[str, Any]:
    password = password_file.read_text(encoding="utf-8").strip()
    if not password:
        raise ValueError("CDC password file is empty")
    template = json.loads(CONNECTOR_TEMPLATE.read_text(encoding="utf-8"))
    config = template["config"]
    if config["database.password"] != "${OLTP_CDC_READER_PASSWORD}":
        raise ValueError("connector template password placeholder is missing")
    config["database.password"] = password
    return template


def connector_is_running(status: dict[str, Any]) -> bool:
    connector_state = status.get("connector", {}).get("state")
    task_states = [task.get("state") for task in status.get("tasks", [])]
    return connector_state == "RUNNING" and task_states == ["RUNNING"]


def connector_has_failed(status: dict[str, Any]) -> bool:
    connector_state = status.get("connector", {}).get("state")
    task_states = [task.get("state") for task in status.get("tasks", [])]
    return connector_state == "FAILED" or "FAILED" in task_states


def connector_status(
    connect_url: str, *, require_running: bool = True
) -> dict[str, Any]:
    _, status = request_json(
        f"{connect_url.rstrip('/')}/connectors/olist-postgres-cdc/status"
    )
    connector_state = status.get("connector", {}).get("state")
    task_states = [task.get("state") for task in status.get("tasks", [])]
    healthy = connector_is_running(status)
    if require_running and not healthy:
        raise RuntimeError(
            f"Connector is not fully running: connector={connector_state}, "
            f"tasks={task_states}"
        )
    return status


def wait_connector_status(
    connect_url: str,
    *,
    expected: str,
    timeout: float = 120,
    poll_interval: float = 2,
) -> dict[str, Any]:
    predicates = {
        "RUNNING": connector_is_running,
        "FAILED": connector_has_failed,
    }
    if expected not in predicates:
        raise ValueError(f"Unsupported connector state: {expected}")

    deadline = time.monotonic() + timeout
    last_status: dict[str, Any] | None = None
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            last_status = connector_status(connect_url, require_running=False)
            last_error = None
            if predicates[expected](last_status):
                return last_status
        except (OSError, RuntimeError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(poll_interval)

    details = f"last_status={last_status!r}"
    if last_error is not None:
        details += f", last_error={last_error}"
    raise RuntimeError(
        f"Timed out waiting for connector and task state {expected}: {details}"
    )


def register_connector(connect_url: str, password_file: Path) -> None:
    base = connect_url.rstrip("/")
    wait_http(f"{base}/connector-plugins", 120)
    _, plugins = request_json(f"{base}/connector-plugins")
    classes = {plugin.get("class") for plugin in plugins}
    required = "io.debezium.connector.postgresql.PostgresConnector"
    if required not in classes:
        raise RuntimeError(f"Required connector plugin is absent: {required}")

    rendered = render_connector(password_file)
    name = rendered["name"]
    config = rendered["config"]
    status, existing = request_json(
        f"{base}/connectors/{name}/config", accepted=(200, 404)
    )
    if status == 404:
        request_json(
            f"{base}/connectors",
            method="POST",
            body=rendered,
            accepted=(201,),
        )
        action = "created"
    elif {key: value for key, value in existing.items() if key != "name"} == config:
        action = "unchanged"
    else:
        request_json(
            f"{base}/connectors/{name}/config",
            method="PUT",
            body=config,
            accepted=(200,),
        )
        action = "updated"

    wait_connector_status(base, expected="RUNNING")
    print(f"Connector {name} {action} and RUNNING.")


def restart_failed_connector(connect_url: str) -> None:
    base = connect_url.rstrip("/")
    wait_http(f"{base}/connectors", 120)
    request_json(
        f"{base}/connectors/olist-postgres-cdc/restart"
        "?includeTasks=true&onlyFailed=true",
        method="POST",
        accepted=(200, 202, 204),
    )
    wait_connector_status(base, expected="RUNNING")
    print("Connector olist-postgres-cdc failed tasks restarted and RUNNING.")


def kafka_command(*args: str) -> str:
    command = [
        "docker",
        "compose",
        "--profile",
        "realtime-core",
        "exec",
        "-T",
        "kafka",
        "/opt/kafka/bin/kafka-topics.sh",
        "--bootstrap-server",
        "kafka:29092",
        *args,
    ]
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse_topic_description(value: str) -> tuple[int, int, dict[str, str]]:
    header = next(line for line in value.splitlines() if "PartitionCount:" in line)
    fields = [part.strip() for part in header.split("\t")]
    properties: dict[str, str] = {}
    for field in fields:
        if ":" in field:
            key, raw = field.split(":", 1)
            properties[key.strip()] = raw.strip()
    configs = dict(
        item.split("=", 1)
        for item in properties.get("Configs", "").split(",")
        if "=" in item
    )
    return (
        int(properties["PartitionCount"]),
        int(properties["ReplicationFactor"]),
        configs,
    )


def validate_topics() -> None:
    manifest = json.loads(TOPIC_MANIFEST.read_text(encoding="utf-8"))
    expected_names = {topic["name"] for topic in manifest["topics"]}
    actual_names = set(kafka_command("--list").split())
    unexpected_source = sorted(
        name
        for name in actual_names - expected_names
        if name.startswith("olist_cdc.public.")
    )
    unexpected_heartbeat = sorted(
        name
        for name in actual_names - expected_names
        if name.startswith("olist_cdc.heartbeat")
    )
    errors: list[str] = []
    if unexpected_source:
        errors.append(f"unexpected source topics: {unexpected_source}")
    if unexpected_heartbeat:
        errors.append(f"unexpected heartbeat topics: {unexpected_heartbeat}")
    for topic in manifest["topics"]:
        name = topic["name"]
        if name not in actual_names:
            errors.append(f"missing topic {name}")
            continue
        partitions, replication, configs = parse_topic_description(
            kafka_command("--describe", "--topic", name)
        )
        checks = {
            "partitions": (partitions, topic["partitions"]),
            "replication_factor": (replication, topic["replication_factor"]),
            "cleanup.policy": (configs.get("cleanup.policy"), topic["cleanup_policy"]),
            "retention.ms": (configs.get("retention.ms"), str(topic["retention_ms"])),
        }
        errors.extend(
            f"{name} {field}: actual={actual!r}, expected={expected!r}"
            for field, (actual, expected) in checks.items()
            if actual != expected
        )
    if errors:
        raise RuntimeError("Topic validation failed:\n- " + "\n- ".join(errors))
    print(f"Validated {len(expected_names)} explicit Kafka topics.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    registry = commands.add_parser("configure-registry")
    registry.add_argument("--url", default="http://localhost:8081")
    register = commands.add_parser("register-connector")
    register.add_argument("--url", default="http://localhost:8083")
    register.add_argument(
        "--password-file",
        type=Path,
        default=Path(
            os.environ.get(
                "OLTP_CDC_READER_PASSWORD_FILE",
                "docker/secrets/dev/postgres_password.txt",
            )
        ),
    )
    status = commands.add_parser("connector-status")
    status.add_argument("--url", default="http://localhost:8083")
    wait_running = commands.add_parser("wait-connector-running")
    wait_running.add_argument("--url", default="http://localhost:8083")
    wait_running.add_argument("--timeout", type=float, default=120)
    wait_failed = commands.add_parser("wait-connector-failed")
    wait_failed.add_argument("--url", default="http://localhost:8083")
    wait_failed.add_argument("--timeout", type=float, default=120)
    restart = commands.add_parser("restart-failed")
    restart.add_argument("--url", default="http://localhost:8083")
    commands.add_parser("validate-topics")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "configure-registry":
            configure_registry(args.url)
        elif args.command == "register-connector":
            register_connector(args.url, args.password_file)
        elif args.command == "connector-status":
            print(json.dumps(connector_status(args.url), indent=2, sort_keys=True))
        elif args.command == "wait-connector-running":
            status = wait_connector_status(
                args.url, expected="RUNNING", timeout=args.timeout
            )
            print(json.dumps(status, indent=2, sort_keys=True))
        elif args.command == "wait-connector-failed":
            status = wait_connector_status(
                args.url, expected="FAILED", timeout=args.timeout
            )
            print(json.dumps(status, indent=2, sort_keys=True))
        elif args.command == "restart-failed":
            restart_failed_connector(args.url)
        elif args.command == "validate-topics":
            validate_topics()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Stage 2 administration failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
