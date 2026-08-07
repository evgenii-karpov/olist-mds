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


def test_gcp_serving_run_is_explicitly_blocked_without_cloud_execution(capsys) -> None:
    result = lab._gcp_serving(Namespace(sync_run_seq=7))

    assert result == 0
    output = capsys.readouterr().out
    assert '"command": "gcp serving run"' in output
    assert '"cloud_execution": "PENDING_GCP_ACCESS"' in output
    assert '"dag_id": "olist_gcp_serving"' in output


def test_gcp_destructive_commands_require_force(capsys) -> None:
    result = lab._gcp_destructive(Namespace(action="destroy", force=False))

    assert result == 0
    output = capsys.readouterr().out
    assert '"status": "blocked"' in output
    assert "requires --force" in output
    assert "state bucket is excluded" in output


def test_gcp_operator_command_surface_is_registered() -> None:
    command_lines = (
        ("gcp", "serving", "run", "--sync-run-seq", "7"),
        ("gcp", "inventory"),
        ("gcp", "reset-data", "--force"),
        ("gcp", "destroy", "--force"),
    )

    for command_line in command_lines:
        parsed = lab._build_parser().parse_args(command_line)
        assert callable(parsed.func)
