#!/usr/bin/env python3
"""Exercise bounded local CDC outages and record alert fire/resolve evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = {
    "connect": ("kafka-connect", "CdcConnectorNotRunning"),
    "nifi": ("nifi", "CdcNifiUnavailable"),
    "minio": ("minio", "CdcMinioUnavailable"),
}


def compose(*args: str) -> None:
    subprocess.run(
        ["docker", "compose", "--profile", "realtime-core", *args],
        cwd=ROOT,
        check=True,
    )


def alert_state(prometheus_url: str, alert: str) -> set[str]:
    query = f'ALERTS{{alertname="{alert}"}}'
    url = f"{prometheus_url.rstrip('/')}/api/v1/query?" + urllib.parse.urlencode(
        {"query": query}
    )
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.loads(response.read())
    return {
        item["metric"].get("alertstate", "unknown")
        for item in payload.get("data", {}).get("result", [])
    }


def wait_for_state(
    prometheus_url: str, alert: str, expected: str, timeout_seconds: int
) -> None:
    deadline = time.monotonic() + timeout_seconds
    last: set[str] = set()
    while time.monotonic() < deadline:
        last = alert_state(prometheus_url, alert)
        if expected == "resolved" and not last:
            return
        if expected in last:
            return
        time.sleep(5)
    raise TimeoutError(f"{alert} did not reach {expected}; last states={sorted(last)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--fire-timeout-seconds", type=int, default=240)
    parser.add_argument("--resolve-timeout-seconds", type=int, default=240)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/reports/stage6-failure-injection.json"),
    )
    args = parser.parse_args()
    service, alert = SCENARIOS[args.scenario]
    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "plan",
                    "scenario": args.scenario,
                    "service": service,
                    "expected_alert": alert,
                    "safety": "No volumes are removed and only the named service is stopped.",
                },
                sort_keys=True,
            )
        )
        return 0

    evidence = {
        "scenario": args.scenario,
        "service": service,
        "alert": alert,
        "started_at": datetime.now(UTC).isoformat(),
        "fired": False,
        "resolved": False,
    }
    failure: Exception | None = None
    try:
        compose("stop", service)
        wait_for_state(args.prometheus_url, alert, "firing", args.fire_timeout_seconds)
        evidence["fired"] = True
    except Exception as exc:
        failure = exc
    finally:
        compose("up", "-d", "--wait", service)
    try:
        wait_for_state(
            args.prometheus_url, alert, "resolved", args.resolve_timeout_seconds
        )
        evidence["resolved"] = True
    except Exception as exc:
        failure = failure or exc
    evidence["finished_at"] = datetime.now(UTC).isoformat()
    if failure is not None:
        evidence["error_type"] = type(failure).__name__
        evidence["error"] = str(failure)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
