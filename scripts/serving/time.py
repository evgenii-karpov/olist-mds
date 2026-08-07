"""Source wall-clock to UTC instant conversion contract."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_SOURCE_TIME_ZONE = "America/Sao_Paulo"
SOURCE_TIME_ZONE_ENV = "SOURCE_TIME_ZONE"


def configured_source_time_zone(
    environment: Mapping[str, str] | None = None,
) -> str:
    """Return and validate the configured source wall-clock timezone."""

    env = os.environ if environment is None else environment
    value = env.get(SOURCE_TIME_ZONE_ENV, DEFAULT_SOURCE_TIME_ZONE).strip()
    if not value:
        raise ValueError(f"{SOURCE_TIME_ZONE_ENV} must not be empty")
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown {SOURCE_TIME_ZONE_ENV}: {value}") from exc
    return value


def normalize_source_timestamp(
    value: str | date | datetime,
    source_time_zone: str | None = None,
) -> datetime:
    """Interpret naive source values in the configured zone and return UTC."""

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    elif isinstance(value, str):
        raw = value.strip()
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        parsed = datetime.fromisoformat(raw)
    else:  # pragma: no cover - type checker narrows public input
        raise TypeError("source timestamp must be a date, datetime, or ISO string")

    if parsed.tzinfo is None:
        zone_name = (
            configured_source_time_zone()
            if source_time_zone is None
            else configured_source_time_zone({SOURCE_TIME_ZONE_ENV: source_time_zone})
        )
        parsed = parsed.replace(tzinfo=ZoneInfo(zone_name))
    return parsed.astimezone(UTC)
