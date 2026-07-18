#!/usr/bin/env python3
"""Idempotently deploy the versioned local CDC process group through NiFi REST."""

from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

TRANSIENT_PROCESSOR_VALIDATION_MARKERS = (
    "initializing runtime environment",
    "loading processor code",
    "downloading third-party dependencies",
)


class NifiClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.context = ssl._create_unverified_context()
        token_body = urllib.parse.urlencode(
            {"username": username, "password": password}
        ).encode()
        self.token = self.request(
            "POST",
            "/access/token",
            raw_body=token_body,
            content_type="application/x-www-form-urlencoded",
            authenticate=False,
        ).decode()

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        raw_body: bytes | None = None,
        content_type: str = "application/json",
        authenticate: bool = True,
    ) -> Any:
        data = (
            raw_body
            if raw_body is not None
            else (None if body is None else json.dumps(body).encode())
        )
        headers = {"Content-Type": content_type}
        if authenticate:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(
                request, context=self.context, timeout=30
            ) as response:
                payload = response.read()
                if response.headers.get_content_type() == "application/json":
                    return json.loads(payload)
                return payload
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(
                f"NiFi {method} {path} failed ({exc.code}): {detail}"
            ) from exc

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, body: dict[str, Any]) -> Any:
        return self.request("POST", path, body)

    def put(self, path: str, body: dict[str, Any]) -> Any:
        return self.request("PUT", path, body)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)


def wait_for_nifi(url: str, timeout: int) -> None:
    context = ssl._create_unverified_context()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(
                f"{url.rstrip('/')}/access/config", context=context, timeout=5
            )
            return
        except urllib.error.HTTPError as exc:
            # A secured NiFi returns 401/403 before a token is supplied. That
            # still proves Jetty and the REST application are ready for login.
            if exc.code in {400, 401, 403, 405}:
                return
            time.sleep(2)
        except (OSError, urllib.error.URLError):
            time.sleep(2)
    raise TimeoutError("NiFi API did not become ready")


def substitute(value: Any, parameters: dict[str, Any]) -> Any:
    if isinstance(value, str):
        for name, replacement in parameters.items():
            value = value.replace(f"#{{{name}}}", str(replacement))
        return value
    if isinstance(value, list):
        return [substitute(item, parameters) for item in value]
    if isinstance(value, dict):
        return {key: substitute(item, parameters) for key, item in value.items()}
    return value


def type_index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["type"]: item for item in items}


def resolve_type(
    requested: str, available: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    if requested in available:
        return available[requested]
    matches = [
        item for name, item in available.items() if name.rsplit(".", 1)[-1] == requested
    ]
    if len(matches) != 1:
        raise ValueError(
            f"NiFi type {requested!r} resolved to {len(matches)} candidates"
        )
    return matches[0]


def configure_service(
    client: NifiClient,
    group_id: str,
    definition: dict[str, Any],
    available: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    metadata = resolve_type(definition["type"], available)
    entity = client.post(
        f"/process-groups/{group_id}/controller-services",
        {
            "revision": {"version": 0},
            "component": {
                "name": definition["name"],
                "type": metadata["type"],
                "bundle": metadata["bundle"],
            },
        },
    )
    return client.put(
        f"/controller-services/{entity['id']}",
        {
            "revision": entity["revision"],
            "component": {
                "id": entity["id"],
                "name": definition["name"],
                "properties": definition.get("properties", {}),
            },
        },
    )


def configure_processor(
    client: NifiClient,
    group_id: str,
    definition: dict[str, Any],
    available: dict[str, dict[str, Any]],
    service_ids: dict[str, str],
) -> dict[str, Any]:
    metadata = resolve_type(definition["type"], available)
    entity = client.post(
        f"/process-groups/{group_id}/processors",
        {
            "revision": {"version": 0},
            "component": {
                "name": definition["name"],
                "type": metadata["type"],
                "bundle": metadata["bundle"],
                "position": {"x": definition.get("x", 0), "y": definition.get("y", 0)},
            },
        },
    )
    properties = {
        key: (
            service_ids[value.removeprefix("@service:")]
            if isinstance(value, str) and value.startswith("@service:")
            else value
        )
        for key, value in definition.get("properties", {}).items()
    }
    return client.put(
        f"/processors/{entity['id']}",
        {
            "revision": entity["revision"],
            "component": {
                "id": entity["id"],
                "name": definition["name"],
                "config": {
                    "properties": properties,
                    "schedulingStrategy": "TIMER_DRIVEN",
                    "schedulingPeriod": "1 sec",
                    "concurrentlySchedulableTaskCount": 1,
                    "penaltyDuration": "30 sec",
                    "yieldDuration": "1 sec",
                    "bulletinLevel": "WARN",
                    "autoTerminatedRelationships": definition.get("auto_terminate", []),
                },
            },
        },
    )


def deploy(client: NifiClient, flow: dict[str, Any], parameters: dict[str, Any]) -> str:
    root = client.get("/flow/process-groups/root")["processGroupFlow"]
    existing = [
        entity
        for entity in root["flow"].get("processGroups", [])
        if entity["component"]["name"] == flow["name"]
    ]
    reuse_existing = False
    if existing:
        group_id = existing[0]["id"]
        current = client.get(f"/flow/process-groups/{group_id}")["processGroupFlow"][
            "flow"
        ]
        expected = {item["name"] for item in flow["processors"]}
        actual = {item["component"]["name"] for item in current.get("processors", [])}
        if actual == expected:
            current_services = client.get(
                f"/flow/process-groups/{group_id}/controller-services"
            )["controllerServices"]
            services = {item["component"]["name"]: item for item in current_services}
            processors = {
                item["component"]["name"]: item
                for item in current.get("processors", [])
            }
            expected_services = {item["name"] for item in flow["controller_services"]}
            reuse_existing = set(services) == expected_services
        if not reuse_existing:
            revision = existing[0]["revision"]
            query = urllib.parse.urlencode(
                {"version": revision["version"], "clientId": "olist-cdc-bootstrap"}
            )
            client.delete(f"/process-groups/{group_id}?{query}")

    if not reuse_existing:
        group = client.post(
            f"/process-groups/{root['id']}/process-groups",
            {
                "revision": {"version": 0},
                "component": {
                    "name": flow["name"],
                    "comments": "Version-controlled Olist CDC landing and normalization flow.",
                    "position": {"x": 0, "y": 0},
                },
            },
        )
        group_id = group["id"]
        controller_types = type_index(
            client.get("/flow/controller-service-types")["controllerServiceTypes"]
        )
        processor_types = type_index(
            client.get("/flow/processor-types")["processorTypes"]
        )

        services = {}
        for definition in flow["controller_services"]:
            entity = configure_service(client, group_id, definition, controller_types)
            services[definition["name"]] = entity
        service_ids = {name: entity["id"] for name, entity in services.items()}

        processors = {}
        for definition in flow["processors"]:
            entity = configure_processor(
                client, group_id, definition, processor_types, service_ids
            )
            processors[definition["name"]] = entity

        for source_name, relationship, destination_name in flow["connections"]:
            source_id = processors[source_name]["id"]
            destination_id = processors[destination_name]["id"]
            client.post(
                f"/process-groups/{group_id}/connections",
                {
                    "revision": {"version": 0},
                    "component": {
                        "name": f"{source_name} [{relationship}] to {destination_name}",
                        "source": {
                            "id": source_id,
                            "groupId": group_id,
                            "type": "PROCESSOR",
                        },
                        "destination": {
                            "id": destination_id,
                            "groupId": group_id,
                            "type": "PROCESSOR",
                        },
                        "selectedRelationships": [relationship],
                        "flowFileExpiration": "0 sec",
                        "backPressureObjectThreshold": int(
                            parameters["backpressure_object_threshold"]
                        ),
                        "backPressureDataSizeThreshold": parameters[
                            "backpressure_data_size_threshold"
                        ],
                    },
                },
            )

    for entity in services.values():
        current = client.get(f"/controller-services/{entity['id']}")
        if current["component"]["state"] != "ENABLED":
            client.put(
                f"/controller-services/{entity['id']}/run-status",
                {"revision": current["revision"], "state": "ENABLED"},
            )
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        states = [
            client.get(f"/controller-services/{entity['id']}")["component"]["state"]
            for entity in services.values()
        ]
        if all(state == "ENABLED" for state in states):
            break
        if any(state == "DISABLED" for state in states):
            time.sleep(2)
        else:
            time.sleep(1)
    else:
        raise TimeoutError(f"controller services did not enable: {states}")

    deadline = time.monotonic() + 180
    while True:
        invalid: dict[str, list[str]] = {}
        initializing = False
        for name, entity in processors.items():
            current = client.get(f"/processors/{entity['id']}")
            errors = current["component"].get("validationErrors") or []
            if errors:
                invalid[name] = errors
                initializing = initializing or all(
                    any(
                        marker in error.lower()
                        for marker in TRANSIENT_PROCESSOR_VALIDATION_MARKERS
                    )
                    for error in errors
                )
        if not invalid:
            break
        if not initializing or time.monotonic() >= deadline:
            raise RuntimeError(
                f"invalid NiFi processors: {json.dumps(invalid, indent=2)}"
            )
        time.sleep(2)

    for entity in processors.values():
        current = client.get(f"/processors/{entity['id']}")
        if current["component"]["state"] != "RUNNING":
            client.put(
                f"/processors/{entity['id']}/run-status",
                {"revision": current["revision"], "state": "RUNNING"},
            )
    return group_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://nifi:8443/nifi-api")
    parser.add_argument("--username", default="nifi-admin")
    parser.add_argument(
        "--password-file", type=Path, default=Path("/run/secrets/nifi_admin_password")
    )
    parser.add_argument(
        "--flow", type=Path, default=Path("/opt/olist/flow/olist-cdc-v1.json")
    )
    parser.add_argument(
        "--parameters",
        type=Path,
        default=Path("/opt/olist/parameters/local.template.json"),
    )
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wait_for_nifi(args.url, args.timeout)
    password = args.password_file.read_text(encoding="utf-8").strip()
    client = NifiClient(args.url, args.username, password)
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    flow = substitute(json.loads(args.flow.read_text(encoding="utf-8")), parameters)
    group_id = deploy(client, flow, parameters)
    print(
        json.dumps(
            {"process_group": flow["name"], "id": group_id, "status": "deployed"}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
