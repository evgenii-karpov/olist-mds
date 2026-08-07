from __future__ import annotations

import pytest
from scripts.orchestration.compose_profiles import (
    GCP_PROFILE,
    GCP_STREAMING_PROFILE,
    LOCAL_PROFILE,
    LOCAL_STREAMING_PROFILE,
    LakehouseTarget,
    compose_profiles,
    validate_profile_selection,
)


def test_local_and_gcp_profiles_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        validate_profile_selection((LOCAL_PROFILE, GCP_PROFILE))


def test_streaming_profiles_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        validate_profile_selection((LOCAL_STREAMING_PROFILE, GCP_STREAMING_PROFILE))


def test_local_profiles_do_not_imply_streaming() -> None:
    assert compose_profiles(LakehouseTarget.LOCAL) == ("core", LOCAL_PROFILE)


def test_gcp_streaming_is_explicit() -> None:
    assert compose_profiles(LakehouseTarget.GCP, streaming=True) == (
        "core",
        GCP_PROFILE,
        GCP_STREAMING_PROFILE,
    )


def test_streaming_requires_a_contour() -> None:
    with pytest.raises(ValueError, match="requires"):
        validate_profile_selection((LOCAL_STREAMING_PROFILE,))
