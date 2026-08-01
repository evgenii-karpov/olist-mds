"""Idempotently configure Apicurio and the secret-bearing MySQL connector.

The connector JSON committed to Git intentionally has no password property.
This module reads the Docker secret at the last responsible moment, keeps it in
memory, and submits it only to Kafka Connect. Diagnostic text is redacted at
both the structured-value and exception-body boundaries.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

CONNECTOR_NAME = "olist-mysql-cdc"
CONNECTOR_PATH = Path(__file__).with_name("olist-mysql-cdc.json")
REGISTRY_CONTRACT_PATH = Path(__file__).with_name("apicurio-contract.json")
DEFAULT_CONNECT_URL = "http://kafka-connect:8083"
DEFAULT_PASSWORD_FILE = Path("/run/secrets/mysql_cdc_reader_password")
_SENSITIVE_KEY = re.compile(
    r"(?:password|passwd|secret|token|credential|authorization)", re.IGNORECASE
)
_JSON_SECRET = re.compile(
    r'(?i)("[^"\\]*(?:password|passwd|secret|token|credential)[^"\\]*"\s*:\s*)'
    r'("(?:\\.|[^"\\])*"|[^,}\s]+)'
)


class BootstrapError(RuntimeError):
    """A redacted, operator-safe bootstrap failure."""


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: Any | None


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        expected: frozenset[int] = frozenset({200}),
        sensitive_values: Sequence[str] = (),
    ) -> HttpResponse: ...


def redact(value: Any) -> Any:
    """Return a deep copy with credential-shaped keys replaced."""

    if isinstance(value, Mapping):
        return {
            str(key): "<redacted>" if _SENSITIVE_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


def redact_text(text: str, sensitive_values: Sequence[str] = ()) -> str:
    sanitized = text
    variants: set[str] = set()
    for secret in sensitive_values:
        if not secret:
            continue
        variants.add(secret)
        variants.add(json.dumps(secret, ensure_ascii=False)[1:-1])
        variants.add(json.dumps(secret, ensure_ascii=True)[1:-1])
    for variant in sorted(variants, key=len, reverse=True):
        sanitized = sanitized.replace(variant, "<redacted>")
    return _JSON_SECRET.sub(r'\1"<redacted>"', sanitized)


class JsonHttpClient:
    """Small urllib client whose errors never expose submitted secrets."""

    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("HTTP base URL must start with http:// or https://")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        expected: frozenset[int] = frozenset({200}),
        sensitive_values: Sequence[str] = (),
    ) -> HttpResponse:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}/{path.lstrip('/')}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                status = response.status
                raw_body = response.read()
        except HTTPError as exc:
            try:
                raw_error = exc.read().decode("utf-8", errors="replace")
            finally:
                exc.close()
            if exc.code in expected:
                return HttpResponse(exc.code, _parse_json(raw_error))
            message = f"{method} {path} returned HTTP {exc.code}"
            if not sensitive_values:
                safe_body = redact_text(raw_error)
                message += f": {safe_body[:1000]}"
            raise BootstrapError(message) from None
        except URLError as exc:
            safe_reason = redact_text(str(exc.reason), sensitive_values)
            raise BootstrapError(f"{method} {path} failed: {safe_reason}") from None

        if status not in expected:
            message = f"{method} {path} returned HTTP {status}"
            if not sensitive_values:
                safe_body = redact_text(raw_body.decode("utf-8", errors="replace"))
                message += f": {safe_body[:1000]}"
            raise BootstrapError(message)
        parsed = _parse_json(raw_body.decode("utf-8", errors="replace"))
        return HttpResponse(status, parsed)


def _parse_json(text: str) -> Any | None:
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"cannot load contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BootstrapError(f"contract {path} must contain a JSON object")
    return value


def read_password(path: Path) -> str:
    """Read exactly one non-empty line without normalizing password spaces."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BootstrapError(f"cannot read password file {path}: {exc}") from exc
    password = text.rstrip("\r\n")
    if not password:
        raise BootstrapError(f"password file {path} is empty")
    if "\n" in password or "\r" in password:
        raise BootstrapError(f"password file {path} must contain exactly one line")
    return password


def render_connector_payload(
    template: Mapping[str, Any], password: str
) -> dict[str, Any]:
    if template.get("name") != CONNECTOR_NAME:
        raise BootstrapError(f"connector template name must be {CONNECTOR_NAME!r}")
    raw_config = template.get("config")
    if not isinstance(raw_config, Mapping):
        raise BootstrapError("connector template config must be an object")
    if any(_SENSITIVE_KEY.search(str(key)) for key in raw_config):
        raise BootstrapError(
            "connector template must not contain credential properties"
        )
    config = {str(key): str(value) for key, value in raw_config.items()}
    config["database.password"] = password
    return {"name": CONNECTOR_NAME, "config": config}


_TRANSITIONAL_STATES = frozenset({"PAUSED", "UNASSIGNED", "RESTARTING"})


def _safe_status_diagnostic(status: Any, sensitive_values: Sequence[str]) -> str:
    try:
        rendered = json.dumps(redact(status), sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        rendered = repr(redact(status))
    return redact_text(rendered, sensitive_values)[:1000]


def wait_for_connector_running(
    client: HttpTransport,
    *,
    password: str,
    timeout_seconds: float,
    poll_interval_seconds: float = 0.5,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Wait until the connector and its sole task 0 are both RUNNING."""

    if timeout_seconds < 0:
        raise ValueError("connector readiness timeout must be non-negative")
    if poll_interval_seconds <= 0:
        raise ValueError("connector readiness poll interval must be positive")
    encoded_name = quote(CONNECTOR_NAME, safe="")
    deadline = monotonic() + timeout_seconds
    last_status: Any = None

    while True:
        response = client.request(
            "GET",
            f"connectors/{encoded_name}/status",
            expected=frozenset({200, 404}),
            sensitive_values=(password,),
        )
        if response.status == 404:
            now = monotonic()
            if now >= deadline:
                raise BootstrapError(
                    f"timed out waiting for {CONNECTOR_NAME} status endpoint"
                )
            sleep(min(poll_interval_seconds, deadline - now))
            continue
        last_status = response.body
        if not isinstance(last_status, Mapping):
            raise BootstrapError(
                f"{CONNECTOR_NAME} returned a non-object status response"
            )

        connector = last_status.get("connector")
        connector_state = (
            connector.get("state") if isinstance(connector, Mapping) else None
        )
        raw_tasks = last_status.get("tasks")
        if not isinstance(raw_tasks, list):
            raise BootstrapError(f"{CONNECTOR_NAME} returned a non-array tasks status")
        tasks = [task for task in raw_tasks if isinstance(task, Mapping)]
        if len(tasks) != len(raw_tasks):
            raise BootstrapError(f"{CONNECTOR_NAME} returned a malformed task status")

        failed_components: list[str] = []
        if connector_state == "FAILED":
            failed_components.append("connector")
        for task in tasks:
            if task.get("state") == "FAILED":
                failed_components.append(f"task-{task.get('id', 'unknown')}")
        if failed_components:
            diagnostic = _safe_status_diagnostic(last_status, (password,))
            raise BootstrapError(
                f"{CONNECTOR_NAME} FAILED components: "
                f"{', '.join(failed_components)}; status={diagnostic}"
            )

        task_zero = next((task for task in tasks if task.get("id") == 0), None)
        if (
            connector_state == "RUNNING"
            and len(tasks) == 1
            and task_zero is not None
            and task_zero.get("state") == "RUNNING"
        ):
            return

        known_connector_state = connector_state in _TRANSITIONAL_STATES | {"RUNNING"}
        known_task_states = all(
            task.get("state") in _TRANSITIONAL_STATES | {"RUNNING"} for task in tasks
        )
        known_task_ids = all(task.get("id") == 0 for task in tasks)
        if not known_connector_state or not known_task_states or not known_task_ids:
            diagnostic = _safe_status_diagnostic(last_status, (password,))
            raise BootstrapError(
                f"{CONNECTOR_NAME} returned an unexpected readiness status: "
                f"{diagnostic}"
            )

        now = monotonic()
        if now >= deadline:
            diagnostic = _safe_status_diagnostic(last_status, (password,))
            raise BootstrapError(
                f"timed out waiting for {CONNECTOR_NAME} connector and task 0 "
                f"to reach RUNNING; last_status={diagnostic}"
            )
        sleep(min(poll_interval_seconds, deadline - now))


def ensure_registry(client: HttpTransport, contract: Mapping[str, Any]) -> str:
    group_id = str(contract.get("group_id", ""))
    if not group_id or group_id == "default":
        raise BootstrapError("registry contract requires a non-reserved group_id")
    encoded_group = quote(group_id, safe="")
    group_response = client.request(
        "GET", f"groups/{encoded_group}", expected=frozenset({200, 404})
    )
    if group_response.status == 404:
        client.request(
            "POST",
            "groups",
            {
                "groupId": group_id,
                "description": str(contract.get("description", "")),
            },
            expected=frozenset({200, 204, 409}),
        )

    rule = contract.get("compatibility_rule")
    if not isinstance(rule, Mapping):
        raise BootstrapError("registry contract compatibility_rule must be an object")
    if (
        rule.get("ruleType") != "COMPATIBILITY"
        or rule.get("config") != "BACKWARD_TRANSITIVE"
    ):
        raise BootstrapError(
            "registry compatibility rule must be COMPATIBILITY=BACKWARD_TRANSITIVE"
        )
    rule_path = f"groups/{encoded_group}/rules/COMPATIBILITY"
    rule_response = client.request("GET", rule_path, expected=frozenset({200, 404}))
    desired_rule = {
        "ruleType": "COMPATIBILITY",
        "config": "BACKWARD_TRANSITIVE",
    }
    if rule_response.status == 404:
        client.request(
            "POST",
            f"groups/{encoded_group}/rules",
            desired_rule,
            expected=frozenset({200, 204, 409}),
        )
        return "created"
    if (
        not isinstance(rule_response.body, Mapping)
        or rule_response.body.get("config") != "BACKWARD_TRANSITIVE"
    ):
        client.request("PUT", rule_path, desired_rule, expected=frozenset({200, 204}))
        return "updated"
    return "unchanged"


def ensure_connector(
    client: HttpTransport,
    payload: Mapping[str, Any],
    *,
    readiness_timeout_seconds: float = 30.0,
    readiness_poll_interval_seconds: float = 0.5,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    config = payload.get("config")
    if not isinstance(config, Mapping):
        raise BootstrapError("rendered connector config must be an object")
    password = str(config.get("database.password", ""))
    encoded_name = quote(CONNECTOR_NAME, safe="")
    existing = client.request(
        "GET",
        f"connectors/{encoded_name}/config",
        expected=frozenset({200, 404}),
        sensitive_values=(password,),
    )
    if existing.status == 404:
        client.request(
            "POST",
            "connectors",
            payload,
            expected=frozenset({200, 201}),
            sensitive_values=(password,),
        )
        result = "created"
    else:
        existing_config = existing.body
        if not isinstance(existing_config, Mapping):
            raise BootstrapError("Kafka Connect returned a non-object connector config")
        normalized_existing = {
            str(key): str(value)
            for key, value in existing_config.items()
            if key != "database.password"
        }
        normalized_desired = {str(key): str(value) for key, value in config.items()}
        normalized_desired.pop("database.password", None)
        if normalized_existing != normalized_desired:
            raise BootstrapError(
                f"{CONNECTOR_NAME} configuration drift detected; immutable bootstrap "
                "will not PUT a secret-bearing replacement"
            )
        result = "unchanged"

    wait_for_connector_running(
        client,
        password=password,
        timeout_seconds=readiness_timeout_seconds,
        poll_interval_seconds=readiness_poll_interval_seconds,
        monotonic=monotonic,
        sleep=sleep,
    )
    return result


def bootstrap(
    *,
    password_file: Path,
    connect_url: str = DEFAULT_CONNECT_URL,
    connector_path: Path = CONNECTOR_PATH,
    registry_contract_path: Path = REGISTRY_CONTRACT_PATH,
    registry_url: str | None = None,
    timeout_seconds: float = 15.0,
) -> dict[str, str]:
    registry_contract = load_json_object(registry_contract_path)
    effective_registry_url = registry_url or str(registry_contract["api_base_url"])
    registry_result = ensure_registry(
        JsonHttpClient(effective_registry_url, timeout_seconds), registry_contract
    )
    password = read_password(password_file)
    payload = render_connector_payload(load_json_object(connector_path), password)
    connector_result = ensure_connector(
        JsonHttpClient(connect_url, timeout_seconds),
        payload,
        readiness_timeout_seconds=timeout_seconds,
    )
    return {"registry": registry_result, "connector": connector_result}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap Apicurio policy and olist-mysql-cdc safely"
    )
    parser.add_argument("--password-file", type=Path, default=DEFAULT_PASSWORD_FILE)
    parser.add_argument("--connect-url", default=DEFAULT_CONNECT_URL)
    parser.add_argument("--registry-url")
    parser.add_argument("--connector", type=Path, default=CONNECTOR_PATH)
    parser.add_argument(
        "--registry-contract", type=Path, default=REGISTRY_CONTRACT_PATH
    )
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = bootstrap(
            password_file=args.password_file,
            connect_url=args.connect_url,
            connector_path=args.connector,
            registry_contract_path=args.registry_contract,
            registry_url=args.registry_url,
            timeout_seconds=args.timeout_seconds,
        )
    except BootstrapError as exc:
        print(f"CDC bootstrap failed: {redact_text(str(exc))}", file=sys.stderr)
        return 1
    print(
        "CDC bootstrap complete: "
        f"registry={result['registry']}, connector={result['connector']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
