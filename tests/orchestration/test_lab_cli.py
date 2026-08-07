from __future__ import annotations

from argparse import Namespace

from scripts import lab


def test_gcp_up_uses_no_streaming_profile(monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    monkeypatch.setattr(
        lab,
        "_gcp_preflight",
        lambda: {
            "checks": {},
            "missing": [],
            "project_id": "test-project",
            "region": "us-central1",
        },
    )

    def fake_run(profiles, arguments, *, timeout):
        calls.append((tuple(profiles), tuple(arguments)))
        return 0, "rendered"

    monkeypatch.setattr(lab, "_run_compose", fake_run)
    result = lab._gcp_up(Namespace(allow_missing_auth=False, build=False, timeout=30.0))

    assert result == 0
    assert calls == [(("core", "lakehouse-gcp"), ("up", "-d"))]


def test_gcp_streaming_start_is_explicitly_blocked_until_drivers_exist(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        lab,
        "_gcp_preflight",
        lambda: {
            "checks": {},
            "missing": [],
            "project_id": "test-project",
            "region": "us-central1",
        },
    )
    result = lab._gcp_streaming(
        Namespace(
            action="start",
            allow_missing_auth=False,
            build=False,
            timeout=30.0,
        )
    )
    assert result == 0
