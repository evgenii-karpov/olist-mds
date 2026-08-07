from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from scripts import lab
from scripts.serving.parity import (
    compare_evidence,
    load_evidence,
    pending_report,
)


def _evidence(contour: str, amount: object = 12) -> dict[str, object]:
    return {
        "contour": contour,
        "run_id": f"{contour}-run-1",
        "boundary": {"orders:0": 7},
        "models": {
            "fact_order_items": {
                "primary_keys": ["order_id", "order_item_id"],
                "numeric_fields": ["amount"],
                "timestamp_fields": ["updated_at"],
                "binary_fields": ["payload"],
                "rows": [
                    {
                        "order_id": "order-1",
                        "order_item_id": 1,
                        "amount": amount,
                        "updated_at": "2026-08-01T16:00:00+04:00",
                        "payload": "base64:AQ==",
                    }
                ],
            }
        },
    }


def test_parity_accepts_documented_representation_differences() -> None:
    local = load_evidence_from_payload(_evidence("local", 12))
    gcp = load_evidence_from_payload(_evidence("gcp", "12.000"))

    report = compare_evidence(local, gcp)

    assert report["status"] == "PASS"
    assert report["difference_count"] == 0
    assert report["models"]["fact_order_items"]["equal"] is True


def test_parity_reports_business_field_mismatch_without_leaking_values() -> None:
    local = load_evidence_from_payload(_evidence("local", 12))
    gcp = load_evidence_from_payload(_evidence("gcp", 13))

    report = compare_evidence(local, gcp)

    assert report["status"] == "FAIL"
    assert report["differences"][0]["category"] == "row"
    serialized = json.dumps(report)
    assert '"amount": 13' not in serialized
    assert '"amount": "13"' not in serialized


def test_duplicate_primary_keys_fail_closed() -> None:
    payload = _evidence("local")
    models = payload["models"]
    assert isinstance(models, dict)
    model = models["fact_order_items"]
    assert isinstance(model, dict)
    rows = model["rows"]
    assert isinstance(rows, list)
    assert isinstance(rows[0], dict)
    rows.append(dict(rows[0]))

    with pytest.raises(ValueError, match="duplicate primary key"):
        load_evidence_from_payload(payload)


def test_pending_report_is_explicitly_blocked() -> None:
    report = pending_report()

    assert report["status"] == "BLOCKED"
    assert report["cloud_execution"] == "PENDING_GCP_ACCESS"
    assert report["sequence"] == ["local", "gcp"]


def test_lab_parity_run_writes_pending_json_and_markdown(
    tmp_path: Path, capsys
) -> None:
    output = tmp_path / "parity"

    result = lab._parity_run(
        Namespace(output=str(output), local_evidence=None, gcp_evidence=None)
    )

    assert result == 0
    assert (
        json.loads((output / "parity.json").read_text(encoding="utf-8"))["status"]
        == "BLOCKED"
    )
    assert (output / "parity.md").is_file()
    assert '"status": "blocked"' in capsys.readouterr().out


def test_lab_parity_run_writes_accepted_report(tmp_path: Path) -> None:
    local_path = tmp_path / "local.json"
    gcp_path = tmp_path / "gcp.json"
    local_path.write_text(json.dumps(_evidence("local", 12)), encoding="utf-8")
    gcp_path.write_text(json.dumps(_evidence("gcp", "12.000")), encoding="utf-8")
    output = tmp_path / "parity"

    result = lab._parity_run(
        Namespace(
            output=str(output),
            local_evidence=str(local_path),
            gcp_evidence=str(gcp_path),
        )
    )

    assert result == 0
    assert (
        json.loads((output / "parity.json").read_text(encoding="utf-8"))["status"]
        == "PASS"
    )


def load_evidence_from_payload(payload: dict[str, object]) -> dict[str, object]:
    """Use the same validation path as the CLI while keeping tests filesystem-free."""

    with TemporaryDirectory() as directory:
        path = Path(directory) / "evidence.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_evidence(path)
