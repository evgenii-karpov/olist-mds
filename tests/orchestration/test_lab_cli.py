from __future__ import annotations

from argparse import Namespace

from scripts import lab


def test_gcp_preflight_accepts_compose_project_and_adc_source(
    monkeypatch, tmp_path
) -> None:
    adc_file = tmp_path / "spark-adc.json"
    adc_file.write_text("{}", encoding="utf-8")
    for variable in (
        "GCP_PROJECT_ID",
        "TF_VAR_project_id",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("GCP_LAKEHOUSE_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCP_REGION", "us-central1")
    monkeypatch.setenv("GCP_SPARK_ADC_SOURCE_FILE", str(adc_file))

    result = lab._gcp_preflight()

    assert result["project_id"] == "test-project"
    assert result["region"] == "us-central1"
    assert result["adc_path"] == str(adc_file)
    assert isinstance(result["checks"], dict)
    assert result["checks"]["adc_file"] is True


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


def test_gcp_streaming_start_uses_the_dedicated_streaming_profile(monkeypatch) -> None:
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
    calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []

    def fake_run(profiles, arguments, *, timeout):
        calls.append((tuple(profiles), tuple(arguments)))
        return 0, "started"

    monkeypatch.setattr(lab, "_run_compose", fake_run)
    result = lab._gcp_streaming(
        Namespace(
            action="start",
            allow_missing_auth=False,
            build=False,
            timeout=30.0,
        )
    )
    assert result == 0
    assert calls == [
        (
            ("core", "lakehouse-gcp", "streaming-gcp"),
            ("up", "-d"),
        )
    ]
