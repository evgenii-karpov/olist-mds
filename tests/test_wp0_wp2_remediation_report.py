from __future__ import annotations

from pathlib import Path

REPORT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "gcp-bigquery-dual-contour"
    / "WP0-WP2-remediation.md"
)


def test_wp0_wp2_acceptance_report_is_durable_and_has_run_evidence() -> None:
    assert REPORT.is_file()
    report = REPORT.read_text(encoding="utf-8")
    for marker in (
        "Starting commit SHA",
        "Ending commit SHA",
        "Run ID",
        "SHA-256",
        "cleanup",
        "WP3",
    ):
        assert marker in report
