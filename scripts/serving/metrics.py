"""Read-only Prometheus exporter for serving metrics."""

from __future__ import annotations

import logging

from scripts.serving.control import ServingControlRepository

logger = logging.getLogger(__name__)


def collect_serving_metrics() -> str:
    """Collect serving metrics in Prometheus text exposition format."""
    lines: list[str] = []

    try:
        state = ServingControlRepository.get_runtime_state()
        last_seq = state.get("last_published_sync_run_seq", 0)
        lines.append(
            "# HELP olist_serving_last_published_sync_run_seq Monotonic published sequence number"
        )
        lines.append("# TYPE olist_serving_last_published_sync_run_seq counter")
        lines.append(f"olist_serving_last_published_sync_run_seq {last_seq}")

        has_lease = 1 if state.get("lease_owner_id") else 0
        lines.append(
            "# HELP olist_serving_active_lease Flag indicating active mutation lease"
        )
        lines.append("# TYPE olist_serving_active_lease gauge")
        lines.append(f"olist_serving_active_lease {has_lease}")
    except Exception as exc:
        logger.warning("Error fetching serving control state for metrics: %s", exc)

    return "\n".join(lines) + "\n"
