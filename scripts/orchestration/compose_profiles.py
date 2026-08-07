"""Compose profile contracts for the local and GCP contours."""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum

CORE_PROFILE = "core"
LOCAL_PROFILE = "lakehouse-local"
GCP_PROFILE = "lakehouse-gcp"
LOCAL_STREAMING_PROFILE = "streaming"
GCP_STREAMING_PROFILE = "streaming-gcp"

# Compatibility aliases remain accepted by scripts/cdc/local_lab.py and the
# existing local runbooks until those callers are migrated to lab.py.
LEGACY_PLATFORM_PROFILE = "platform"
LEGACY_SERVING_PROFILE = "serving"


class LakehouseTarget(StrEnum):
    """Mutually exclusive lakehouse contours."""

    LOCAL = "local"
    GCP = "gcp"


def validate_profile_selection(profiles: Iterable[str]) -> tuple[str, ...]:
    """Validate and normalize a Compose profile selection."""

    selected = tuple(
        dict.fromkeys(profile.strip() for profile in profiles if profile.strip())
    )
    if LOCAL_PROFILE in selected and GCP_PROFILE in selected:
        raise ValueError(
            "lakehouse-local and lakehouse-gcp are mutually exclusive Compose profiles"
        )
    if LOCAL_STREAMING_PROFILE in selected and GCP_STREAMING_PROFILE in selected:
        raise ValueError("local and GCP streaming profiles are mutually exclusive")
    if GCP_PROFILE in selected and any(
        profile in selected
        for profile in (LEGACY_PLATFORM_PROFILE, LEGACY_SERVING_PROFILE)
    ):
        raise ValueError(
            "legacy local profiles cannot be combined with the lakehouse-gcp profile"
        )
    if GCP_STREAMING_PROFILE in selected and GCP_PROFILE not in selected:
        raise ValueError("streaming-gcp requires the lakehouse-gcp profile")
    if LOCAL_STREAMING_PROFILE in selected and not (
        LOCAL_PROFILE in selected or LEGACY_PLATFORM_PROFILE in selected
    ):
        raise ValueError("streaming requires the local lakehouse profile")
    return selected


def compose_profiles(
    target: LakehouseTarget | str,
    *,
    streaming: bool = False,
) -> tuple[str, ...]:
    """Return the canonical Compose profile set for one contour."""

    try:
        normalized_target = LakehouseTarget(target)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unknown lakehouse target: {target!r}") from exc
    lakehouse_profile = (
        LOCAL_PROFILE if normalized_target is LakehouseTarget.LOCAL else GCP_PROFILE
    )
    profiles = [CORE_PROFILE, lakehouse_profile]
    if streaming:
        profiles.append(
            LOCAL_STREAMING_PROFILE
            if normalized_target is LakehouseTarget.LOCAL
            else GCP_STREAMING_PROFILE
        )
    return validate_profile_selection(profiles)
