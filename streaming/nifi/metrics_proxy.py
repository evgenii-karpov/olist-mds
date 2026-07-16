#!/usr/bin/env python3
"""Expose authenticated NiFi Prometheus metrics to the private Compose network."""

from __future__ import annotations

import argparse
import ssl
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class NifiMetrics:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.context = ssl._create_unverified_context()
        self.token = ""
        self.token_time = 0.0

    def _authenticate(self) -> None:
        body = urllib.parse.urlencode(
            {"username": self.username, "password": self.password}
        ).encode()
        request = urllib.request.Request(
            f"{self.url}/access/token",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(
            request, context=self.context, timeout=10
        ) as response:
            self.token = response.read().decode()
        self.token_time = time.monotonic()

    def scrape(self) -> bytes:
        if not self.token or time.monotonic() - self.token_time > 600:
            self._authenticate()
        request = urllib.request.Request(
            f"{self.url}/flow/metrics/prometheus",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            with urllib.request.urlopen(
                request, context=self.context, timeout=15
            ) as response:
                body = response.read()
        except Exception:
            self.token = ""
            raise
        return b"olist_nifi_metrics_proxy_up 1\n" + body


def handler(metrics: NifiMetrics):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in {"/metrics", "/-/healthy"}:
                self.send_error(404)
                return
            try:
                body = b"ok\n" if self.path == "/-/healthy" else metrics.scrape()
                self.send_response(200)
            except Exception:
                body = b"olist_nifi_metrics_proxy_up 0\n"
                self.send_response(503)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://nifi:8443/nifi-api")
    parser.add_argument("--username", default="nifi-admin")
    parser.add_argument(
        "--password-file", type=Path, default=Path("/run/secrets/nifi_admin_password")
    )
    parser.add_argument("--port", type=int, default=9105)
    args = parser.parse_args()
    metrics = NifiMetrics(
        args.url, args.username, args.password_file.read_text(encoding="utf-8").strip()
    )
    ThreadingHTTPServer(("0.0.0.0", args.port), handler(metrics)).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
