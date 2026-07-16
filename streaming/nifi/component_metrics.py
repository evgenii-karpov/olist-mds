#!/usr/bin/env python3
"""Low-cardinality health exporter for Connect and its Debezium task."""

from __future__ import annotations

import argparse
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        value = json.loads(response.read())
    return value if isinstance(value, dict) else {}


def render(connect_url: str, connector: str) -> bytes:
    lines = []
    try:
        status = fetch_json(f"{connect_url.rstrip('/')}/connectors/{connector}/status")
        connector_up = status.get("connector", {}).get("state") == "RUNNING"
        tasks = status.get("tasks") or []
        task_up = bool(tasks) and all(task.get("state") == "RUNNING" for task in tasks)
        lines.extend(
            [
                "olist_connect_rest_up 1",
                f'olist_connect_connector_running{{connector="{connector}"}} {int(connector_up)}',
                f'olist_connect_tasks_running{{connector="{connector}"}} {int(task_up)}',
                f'olist_connect_task_count{{connector="{connector}"}} {len(tasks)}',
            ]
        )
    except Exception:
        lines.append("olist_connect_rest_up 0")
    return ("\n".join(lines) + "\n").encode()


def handler(connect_url: str, connector: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in {"/metrics", "/-/healthy"}:
                self.send_error(404)
                return
            body = (
                b"ok\n" if self.path == "/-/healthy" else render(connect_url, connector)
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connect-url", default="http://kafka-connect:8083")
    parser.add_argument("--connector", default="olist-postgres-cdc")
    parser.add_argument("--port", type=int, default=9106)
    args = parser.parse_args()
    ThreadingHTTPServer(
        ("0.0.0.0", args.port), handler(args.connect_url, args.connector)
    ).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
