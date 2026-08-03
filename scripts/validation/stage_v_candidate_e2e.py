#!/usr/bin/env python3
"""Stage V Candidate E2E Validation Harness and Gate Orchestrator.

Enforces gates V0-V10 in a single clean-domain run, collects evidence,
verifies invariants, and produces the Stage V validation report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validation.stage_v_probes import (
    ALLOWED_FIXTURES,
    ClickHouseProbe,
    MySQLProbe,
    sanitize_text,
)

EXPECTED_COMPOSE_PROJECT = "olist_stage_v"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_json_payload(output: str) -> dict[str, Any]:
    """Parse one lifecycle command's bounded JSON result."""
    try:
        payload = json.loads(output.strip())
    except json.JSONDecodeError:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def positive_int(value: object) -> bool:
    """Return whether a value can be represented as a strictly positive integer."""

    if not isinstance(value, (int, float, str)):
        return False
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


EXPECTED_SERVING_ENTITIES = frozenset(
    {
        "customers",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "products",
        "sellers",
        "product_category_translation",
    }
)

ADDITIVE_SCHEMA_CHANGED_ENTITIES = frozenset({"customers"})


def valid_serving_target_offsets(value: object) -> bool:
    """Validate target offsets for every serving topic and its partitions."""

    if not isinstance(value, Mapping) or not value:
        return False

    topic_prefix = "olist_cdc.olist_oltp."
    covered_entities: set[str] = set()
    for raw_key, raw_offset in value.items():
        if not isinstance(raw_key, str) or not isinstance(
            raw_offset, (int, float, str)
        ):
            return False
        topic, separator, partition_text = raw_key.rpartition(":")
        if separator != ":" or not partition_text.isdigit():
            return False
        if int(partition_text) < 0:
            return False
        if not topic.startswith(topic_prefix):
            return False
        entity = topic[len(topic_prefix) :]
        if entity not in EXPECTED_SERVING_ENTITIES:
            return False
        try:
            if int(raw_offset) < 0:
                return False
        except (TypeError, ValueError):
            return False
        covered_entities.add(entity)

    return covered_entities == EXPECTED_SERVING_ENTITIES


def valid_additive_snapshot_transition(
    previous_payload: Mapping[str, Any],
    current_payload: Mapping[str, Any],
    changed_entities: frozenset[str] = ADDITIVE_SCHEMA_CHANGED_ENTITIES,
) -> bool:
    """Validate the expected Iceberg snapshot transition for V8.

    The nullable-column fixture targets ``customers``.  Unrelated entities
    must retain the snapshots established by V6, while every affected entity
    must receive a new committed progress row.  Iceberg snapshot IDs are
    opaque, so the assertion checks identity transition rather than numeric
    ordering.  The downstream V8 probes still provide the authoritative proof
    that the nullable event reached Bronze, Silver and serving.
    """

    previous = previous_payload.get("iceberg_snapshot_ids")
    current = current_payload.get("iceberg_snapshot_ids")
    if (
        not isinstance(previous, Mapping)
        or not isinstance(current, Mapping)
        or set(previous) != EXPECTED_SERVING_ENTITIES
        or set(current) != EXPECTED_SERVING_ENTITIES
        or not changed_entities
        or not changed_entities <= EXPECTED_SERVING_ENTITIES
    ):
        return False

    if not all(positive_int(value) for value in previous.values()) or not all(
        positive_int(value) for value in current.values()
    ):
        return False

    return all(
        (
            current[entity] != previous[entity]
            if entity in changed_entities
            else current[entity] == previous[entity]
        )
        for entity in EXPECTED_SERVING_ENTITIES
    )


MANDATORY_GATES = (
    "00-preflight",
    "01-harness-ready",
    "02-clean-bootstrap",
    "03-initial-snapshot",
    "04-crud-and-restart",
    "05-caught-up",
    "06-serving-sync",
    "07-dbt-and-stable-views",
    "08-additive-schema",
    "09-rebuild",
    "10-final",
)

# The assertion registry is part of the acceptance contract.  A generic
# assertion such as ``{"name": "check", "status": "PASS"}`` is not
# evidence: it cannot prove which operation was actually performed.  Keep the
# names explicit so the standalone ``report`` command cannot accept a forged
# summary with invented or missing checks.
REQUIRED_ASSERTIONS: dict[str, tuple[str, ...]] = {
    "00-preflight": (
        "compose_project_name_check",
        "endpoint_provenance",
        "source_tree_identity",
        "pre_commit_check",
        "uv_lock_check",
        "python_tests_check",
        "scala_sbt_build_check",
    ),
    "01-harness-ready": tuple(
        [
            *(f"fixture_{name}_exists" for name in sorted(ALLOWED_FIXTURES)),
            "oracle_file_exists",
        ]
    ),
    "02-clean-bootstrap": ("lab_reset", "lab_bootstrap_seed"),
    "03-initial-snapshot": (
        "start_streaming",
        "start_serving_observer",
        "initial_snapshot_caught_up",
        "initial_snapshot_exact_oracle",
    ),
    "04-crud-and-restart": (
        "stop_spark_streaming",
        "execute_crud_fixtures",
        "start_spark_streaming_recovery",
    ),
    "05-caught-up": (
        "crud_caught_up",
        "post_crud_exact_oracle",
        "restart_freshness",
    ),
    "06-serving-sync": (
        "start_serving",
        "sync_serving_crud",
        "sync_serving_crud_repeat_noop",
    ),
    "07-dbt-and-stable-views": (
        "serving_static_validation",
        "dbt_and_stable_views_validation",
    ),
    "08-additive-schema": (
        "execute_nullable_schema_fixtures",
        "mysql_nullable_source_contract",
        "schema_evolution_caught_up",
        "additive_schema_publish",
        "nullable_avro_bronze_silver_serving_propagation",
        "post_schema_exact_oracle",
        "post_schema_candidate_dbt_and_stable_parity",
    ),
    "09-rebuild": (
        "rebuild_serving_from_iceberg",
        "rebuild_iceberg_current_gold_and_dbt_parity",
    ),
    "10-final": (
        "final_rebuild_current_and_gold_parity",
        "final_independent_control_plane_check",
        "final_serving_status_check",
    ),
}

ALLOWED_ASSERTION_STATUSES = frozenset({"PASS", "FAIL", "ERROR", "SKIPPED"})

EXPECTED_ENDPOINTS = {
    "COMPOSE_FILE": str(ROOT / "compose.yaml"),
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_HOST_PORT": "3306",
    "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9092",
    "KAFKA_CONNECT_URL": "http://127.0.0.1:8083",
    "APICURIO_REGISTRY_URL": "http://127.0.0.1:8081/apis/registry/v3",
    "APICURIO_CCOMPAT_URL": "http://127.0.0.1:8081/apis/ccompat/v7",
    "CLICKHOUSE_HOST": "127.0.0.1",
    "CLICKHOUSE_PORT": "8123",
    "AIRFLOW_URL": "http://127.0.0.1:8080",
}
ORACLE_PATH = ROOT / "tests" / "stage_v" / "oracles" / "initial_counts.json"


def _expected_assertion_names(gate_name: str) -> tuple[str, ...]:
    return REQUIRED_ASSERTIONS.get(gate_name, ())


def _status_list(value: object) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return list(value)


def validate_acceptance_summary(summary_data: object) -> list[str]:
    """Return every reason a persisted summary cannot be accepted."""

    errors: list[str] = []
    if not isinstance(summary_data, dict):
        return ["summary is not a JSON object"]

    if summary_data.get("overall_status") != "PASS":
        errors.append(
            f"overall_status is {summary_data.get('overall_status')!r}, expected 'PASS'"
        )

    gates = summary_data.get("gates")
    if not isinstance(gates, dict):
        return [*errors, "gates is not a JSON object"]

    if not isinstance(summary_data.get("run_id"), str) or not summary_data.get(
        "run_id"
    ):
        errors.append("summary has no non-empty run_id")

    declared_gates = summary_data.get("mandatory_gates")
    if declared_gates != list(MANDATORY_GATES):
        errors.append("mandatory_gates does not match the V0-V10 registry")

    actual_gate_names = sorted(str(name) for name in gates)
    expected_gate_names = sorted(MANDATORY_GATES)
    if actual_gate_names != expected_gate_names:
        missing = sorted(set(MANDATORY_GATES) - set(gates))
        extra = sorted(set(gates) - set(MANDATORY_GATES))
        if missing:
            errors.append(f"summary is missing gate keys: {missing!r}")
        if extra:
            errors.append(f"summary has unexpected gate keys: {extra!r}")

    actual_missing_gates = [gate for gate in MANDATORY_GATES if gate not in gates]
    actual_failed_gates = [
        gate
        for gate in MANDATORY_GATES
        if not isinstance(gates.get(gate), dict) or gates[gate].get("status") != "PASS"
    ]
    declared_missing = _status_list(summary_data.get("missing_gates"))
    declared_failed = _status_list(summary_data.get("failed_or_skipped_gates"))
    if declared_missing != actual_missing_gates:
        errors.append(
            "summary missing_gates does not match gate evidence: "
            f"declared={declared_missing!r}, actual={actual_missing_gates!r}"
        )
    if declared_failed != actual_failed_gates:
        errors.append(
            "summary failed_or_skipped_gates does not match gate evidence: "
            f"declared={declared_failed!r}, actual={actual_failed_gates!r}"
        )

    cleanup_is_pass = (
        isinstance(summary_data.get("runtime_cleanup"), dict)
        and summary_data["runtime_cleanup"].get("status") == "PASS"
    )
    expected_overall = (
        "PASS"
        if not actual_missing_gates and not actual_failed_gates and cleanup_is_pass
        else "FAIL"
    )
    if summary_data.get("overall_status") != expected_overall:
        errors.append(
            "overall_status does not match gate evidence: "
            f"declared={summary_data.get('overall_status')!r}, expected={expected_overall!r}"
        )

    cleanup = summary_data.get("runtime_cleanup")
    if not isinstance(cleanup, dict) or cleanup.get("status") != "PASS":
        errors.append("runtime_cleanup is not recorded as PASS")

    for gate_name in MANDATORY_GATES:
        gate_info = gates.get(gate_name)
        if not isinstance(gate_info, dict):
            errors.append(f"missing evidence for mandatory gate {gate_name}")
            continue
        if gate_info.get("gate") != gate_name:
            errors.append(
                f"gate {gate_name} has mismatched gate field {gate_info.get('gate')!r}"
            )
        if gate_info.get("status") != "PASS":
            errors.append(
                f"gate {gate_name} has status {gate_info.get('status')!r}, expected 'PASS'"
            )
        assertions = gate_info.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"gate {gate_name} has no assertion evidence")
            continue
        expected_assertions = set(_expected_assertion_names(gate_name))
        actual_assertions: list[str] = []
        for index, assertion in enumerate(assertions):
            if not isinstance(assertion, dict):
                errors.append(f"gate {gate_name} assertion {index} is not an object")
                continue
            name = assertion.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"gate {gate_name} assertion {index} has no name")
            else:
                actual_assertions.append(name)
            assertion_status = assertion.get("status")
            if assertion_status not in ALLOWED_ASSERTION_STATUSES:
                errors.append(
                    f"gate {gate_name} assertion {index} has invalid status "
                    f"{assertion_status!r}"
                )
            elif assertion_status != "PASS":
                errors.append(
                    f"gate {gate_name} assertion {index} has status "
                    f"{assertion_status!r}"
                )
        duplicate_assertions = sorted(
            name for name in set(actual_assertions) if actual_assertions.count(name) > 1
        )
        if duplicate_assertions:
            errors.append(
                f"gate {gate_name} has duplicate assertions: {duplicate_assertions!r}"
            )
        if set(actual_assertions) != expected_assertions:
            missing_assertions = sorted(expected_assertions - set(actual_assertions))
            extra_assertions = sorted(set(actual_assertions) - expected_assertions)
            if missing_assertions:
                errors.append(
                    f"gate {gate_name} is missing required assertions: {missing_assertions!r}"
                )
            if extra_assertions:
                errors.append(
                    f"gate {gate_name} has unexpected assertions: {extra_assertions!r}"
                )

    return errors


def verify_evidence_directory(evidence_dir: Path, summary_data: object) -> list[str]:
    """Verify that summary, per-gate raw evidence and checksums agree.

    ``report`` must be a read-only consumer of evidence.  Re-generating a
    checksum file at report time would make a modified report appear valid, so
    this function only verifies the persisted checksum manifest.
    """

    errors = validate_acceptance_summary(summary_data)
    if not evidence_dir.is_dir():
        return [*errors, f"evidence directory does not exist: {evidence_dir}"]

    checksum_path = evidence_dir / "checksums.json"
    if not checksum_path.is_file():
        return [*errors, "checksums.json is missing"]
    try:
        checksums = json.loads(checksum_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"checksums.json is unreadable: {exc}"]
    if not isinstance(checksums, dict) or not all(
        isinstance(path, str) and isinstance(value, str)
        for path, value in checksums.items()
    ):
        errors.append("checksums.json must be an object of relative path to SHA-256")
        checksums = {}

    actual_files: dict[str, str] = {}
    for path in sorted(evidence_dir.glob("**/*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(evidence_dir)).replace("\\", "/")
        if relative not in {"checksums.json", "summary.json"}:
            actual_files[relative] = sha256_file(path)
    if set(checksums) != set(actual_files):
        errors.append(
            "checksums.json file set does not match evidence: "
            f"missing={sorted(set(actual_files) - set(checksums))!r}, "
            f"extra={sorted(set(checksums) - set(actual_files))!r}"
        )
    for relative, digest in actual_files.items():
        if checksums.get(relative) != digest:
            errors.append(f"evidence checksum mismatch: {relative}")

    if isinstance(summary_data, dict):
        gates = summary_data.get("gates")
        if isinstance(gates, dict):
            for gate_name in MANDATORY_GATES:
                raw_path = evidence_dir / gate_name / "summary.json"
                if not raw_path.is_file():
                    errors.append(f"raw gate summary is missing: {gate_name}")
                    continue
                try:
                    raw_gate = json.loads(raw_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(
                        f"raw gate summary is unreadable ({gate_name}): {exc}"
                    )
                    continue
                if raw_gate != gates.get(gate_name):
                    errors.append(f"summary/gate raw evidence mismatch: {gate_name}")
    return errors


class StageVOrchestrator:
    """Orchestrates gates V0-V10 for Stage V E2E validation."""

    def __init__(self, run_id: str, evidence_dir: Path) -> None:
        self.run_id = run_id
        self.execution_token = uuid.uuid4().hex[:12]
        self.evidence_dir = evidence_dir
        self.start_time = datetime.now(UTC).isoformat()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.gate_results: dict[str, dict[str, Any]] = {}
        self._command_log: list[list[str]] = []
        self._command_results: list[dict[str, Any]] = []
        self._last_logged_command_index = 0
        self.oracle: dict[str, Any] = {}
        self.runtime_cleanup: dict[str, Any] = {"status": "NOT_RUN"}

    def dag_run_id(self, label: str) -> str:
        """Return a unique Airflow run ID for this harness execution."""

        return f"{self.run_id}_{label}_{self.execution_token}"

    def log_gate(
        self,
        gate_name: str,
        status: str,
        duration: float,
        assertions: list[dict[str, Any]],
        details: dict[str, Any] | None = None,
        command: list[list[str]] | None = None,
    ) -> None:
        gate_dir = self.evidence_dir / gate_name
        gate_dir.mkdir(parents=True, exist_ok=True)

        commands = command or self._command_log[self._last_logged_command_index :]
        command_results = self._command_results[self._last_logged_command_index :]
        self._last_logged_command_index = len(self._command_log)

        gate_summary = {
            "gate": gate_name,
            "status": status,
            "duration_seconds": round(duration, 3),
            "timestamp": datetime.now(UTC).isoformat(),
            "command": commands,
            "command_results": command_results,
            "assertions": assertions,
            "details": details or {},
        }

        summary_file = gate_dir / "summary.json"
        summary_file.write_text(
            json.dumps(gate_summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        self.gate_results[gate_name] = gate_summary

    def run_cmd(
        self,
        args: list[str],
        cwd: Path = ROOT,
        env: dict[str, str] | None = None,
        timeout: float = 3600.0,
    ) -> tuple[int, str, str]:
        current_env = os.environ.copy()
        current_env["COMPOSE_PROJECT_NAME"] = EXPECTED_COMPOSE_PROJECT
        current_env.setdefault("COMPOSE_FILE", str(ROOT / "compose.yaml"))
        for name, value in EXPECTED_ENDPOINTS.items():
            current_env.setdefault(name, value)
        if env:
            current_env.update(env)
        current_env["COMPOSE_PROJECT_NAME"] = EXPECTED_COMPOSE_PROJECT
        current_env["COMPOSE_FILE"] = str(ROOT / "compose.yaml")
        existing_python_path = current_env.get("PYTHONPATH")
        python_path_parts = [
            item for item in (existing_python_path or "").split(os.pathsep) if item
        ]
        if str(ROOT) not in python_path_parts:
            python_path_parts.insert(0, str(ROOT))
        current_env["PYTHONPATH"] = os.pathsep.join(python_path_parts)

        self._command_log.append(list(args))
        started = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(
                args,
                cwd=cwd,
                env=current_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            exit_code = proc.returncode
            stdout = sanitize_text(proc.stdout or "")
            stderr = sanitize_text(proc.stderr or "")
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exit_code = 124
            stdout = sanitize_text(
                (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            )
            stderr = sanitize_text(
                (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            )
            stderr = f"command timed out after {timeout:g}s" + (
                f"; {stderr}" if stderr else ""
            )
        except OSError as exc:
            exit_code = 127
            stdout = ""
            stderr = sanitize_text(str(exc))

        # Keep raw command evidence bounded.  The exit code, timeout marker and
        # complete command remain available even when a compiler emits a large
        # log; the full process output is not allowed to exhaust evidence RAM.
        self._command_results.append(
            {
                "args": list(args),
                "exit_code": exit_code,
                "timed_out": timed_out,
                "duration_seconds": round(time.monotonic() - started, 3),
                "stdout": stdout[-12000:],
                "stderr": stderr[-12000:],
            }
        )
        return exit_code, stdout, stderr

    def _capture_source_tree_identity(self) -> dict[str, Any]:
        """Capture HEAD plus dirty-tree contents without claiming a clean tree."""

        sha_code, head, sha_err = self.run_cmd(["git", "rev-parse", "HEAD"])
        status_code, status, status_err = self.run_cmd(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"]
        )
        diff_code, diff, diff_err = self.run_cmd(
            ["git", "diff", "--binary", "HEAD", "--"]
        )
        untracked_code, untracked, untracked_err = self.run_cmd(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"]
        )
        digest = hashlib.sha256()
        digest.update(head.strip().encode("utf-8"))
        digest.update(b"\0")
        digest.update(status.encode("utf-8"))
        digest.update(b"\0")
        digest.update(diff.encode("utf-8"))
        for raw_path in untracked.split("\0"):
            if not raw_path:
                continue
            path = ROOT / raw_path
            digest.update(b"\0untracked\0")
            digest.update(raw_path.encode("utf-8"))
            try:
                digest.update(path.read_bytes())
            except OSError:
                digest.update(b"<unreadable>")
        changed_paths = [line[3:] for line in status.splitlines() if len(line) >= 4]
        return {
            "head": head.strip() if sha_code == 0 else None,
            "dirty": bool(status.strip()) if status_code == 0 else None,
            "changed_paths": changed_paths,
            "worktree_digest": digest.hexdigest()
            if all(
                code == 0 for code in (sha_code, status_code, diff_code, untracked_code)
            )
            else None,
            "captured_after_pre_commit": True,
            "commands_ok": all(
                code == 0 for code in (sha_code, status_code, diff_code, untracked_code)
            ),
            "diagnostics": sanitize_text(
                " ".join(
                    item
                    for item in (sha_err, status_err, diff_err, untracked_err)
                    if item
                )
            )[-2000:],
        }

    def clear_evidence(self) -> None:
        """Remove only children of the explicitly supplied evidence directory."""

        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        for child in self.evidence_dir.iterdir():
            if child.is_symlink() or not child.is_dir():
                child.unlink()
            else:
                shutil.rmtree(child)

    def load_oracle(self) -> dict[str, Any]:
        try:
            payload = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Stage V oracle is unreadable: {ORACLE_PATH}: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise RuntimeError("Stage V oracle must be a JSON object")
        self.oracle = payload
        return payload

    def cleanup_runtime(self) -> bool:
        """Stop only this harness's Compose project after a successful run."""

        code, stdout, stderr = self.run_cmd(
            ["uv", "run", "python", "scripts/cdc/local_lab.py", "down"],
            timeout=300.0,
        )
        payload = parse_json_payload(stdout)
        self.runtime_cleanup = {
            "status": "PASS"
            if code == 0 and payload.get("status") == "ready"
            else "FAIL",
            "exit_code": code,
            "command": [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "down",
            ],
            "result": payload or stdout.strip(),
            "stderr": stderr[-4000:],
            "scoped_to": EXPECTED_COMPOSE_PROJECT,
        }
        (self.evidence_dir / "runtime_cleanup.json").write_text(
            json.dumps(self.runtime_cleanup, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return self.runtime_cleanup["status"] == "PASS"

    def preserve_runtime_for_diagnostics(self, result: Mapping[str, Any]) -> None:
        """Keep a failed run alive so container logs remain available."""

        self.runtime_cleanup = {
            "status": "SKIPPED",
            "reason": "E2E_FAILED_RUNTIME_PRESERVED_FOR_DIAGNOSTICS",
            "failed_gate": result.get("gate"),
            "scoped_to": EXPECTED_COMPOSE_PROJECT,
            "diagnostic_command": [
                "docker",
                "compose",
                "--project-name",
                EXPECTED_COMPOSE_PROJECT,
                "logs",
            ],
        }
        (self.evidence_dir / "runtime_cleanup.json").write_text(
            json.dumps(self.runtime_cleanup, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def prepare(self) -> dict[str, Any]:
        """Execute Gates V0 and V1 (Read-only preflight and harness readiness)."""
        t0 = time.time()
        assertions = []

        # Check exact compose project name environment variable if set or required
        project = os.environ.get("COMPOSE_PROJECT_NAME", EXPECTED_COMPOSE_PROJECT)
        if project and project != EXPECTED_COMPOSE_PROJECT:
            assertions.append(
                {
                    "name": "compose_project_name_check",
                    "status": "FAIL",
                    "detail": f"Expected COMPOSE_PROJECT_NAME={EXPECTED_COMPOSE_PROJECT}, got {project!r}",
                }
            )
            self.log_gate("00-preflight", "FAIL", time.time() - t0, assertions)
            return {"status": "FAIL", "reason": "INVALID_COMPOSE_PROJECT"}

        assertions.append(
            {
                "name": "compose_project_name_check",
                "status": "PASS",
                "detail": f"COMPOSE_PROJECT_NAME={EXPECTED_COMPOSE_PROJECT}",
            }
        )

        endpoint_mismatches = {
            name: {
                "expected": expected,
                "actual": os.environ.get(name, expected),
            }
            for name, expected in EXPECTED_ENDPOINTS.items()
            if os.environ.get(name, expected) != expected
        }
        assertions.append(
            {
                "name": "endpoint_provenance",
                "status": "PASS" if not endpoint_mismatches else "FAIL",
                "detail": {
                    "expected": EXPECTED_ENDPOINTS,
                    "mismatches": endpoint_mismatches,
                },
            }
        )

        # Check pre-commit
        pc_code, _, _ = self.run_cmd(["uv", "run", "pre-commit", "run", "--all-files"])
        assertions.append(
            {
                "name": "pre_commit_check",
                "status": "PASS" if pc_code == 0 else "FAIL",
                "detail": "All pre-commit hooks passed cleanly",
            }
        )

        # Gate V0 checks.  A dirty tree is allowed for this candidate run, but
        # its identity must be captured honestly; a bare HEAD SHA is not
        # sufficient when pre-commit or the candidate itself changed files.
        source_identity = self._capture_source_tree_identity()
        assertions.append(
            {
                "name": "source_tree_identity",
                "status": "PASS"
                if source_identity.get("commands_ok")
                and source_identity.get("head")
                and source_identity.get("worktree_digest")
                else "FAIL",
                "detail": source_identity,
            }
        )

        # Check uv lock
        uv_code, _, _ = self.run_cmd(["uv", "lock", "--check"])
        assertions.append(
            {
                "name": "uv_lock_check",
                "status": "PASS" if uv_code == 0 else "FAIL",
                "detail": "uv.lock is consistent",
            }
        )

        # Run python test suite
        pytest_code, _, _ = self.run_cmd(
            [
                "uv",
                "run",
                "pytest",
                "tests/cdc_contracts",
                "tests/lakehouse_platform",
                "tests/mysql",
                "tests/dbt_clickhouse",
                "tests/serving",
                "tests/stage_v",
            ]
        )
        assertions.append(
            {
                "name": "python_tests_check",
                "status": "PASS" if pytest_code == 0 else "FAIL",
                "detail": "Python test suites passed",
            }
        )

        # Check Scala Docker build
        scala_code, _, _ = self.run_cmd(
            [
                "docker",
                "build",
                "--target",
                "scala-builder",
                "-f",
                "docker/spark/Dockerfile",
                ".",
            ]
        )
        assertions.append(
            {
                "name": "scala_sbt_build_check",
                "status": "PASS" if scala_code == 0 else "FAIL",
                "detail": "Scala sbt scalafmtCheckAll and test suite passed",
            }
        )

        v0_status = "PASS" if all(a["status"] == "PASS" for a in assertions) else "FAIL"
        self.log_gate("00-preflight", v0_status, time.time() - t0, assertions)
        if v0_status != "PASS":
            return {"status": "FAIL", "gate": "00-preflight"}

        # Gate V1: Harness readiness
        t1 = time.time()
        v1_assertions = []
        for fix_name, fix_path in ALLOWED_FIXTURES.items():
            exists = fix_path.exists()
            v1_assertions.append(
                {
                    "name": f"fixture_{fix_name}_exists",
                    "status": "PASS" if exists else "FAIL",
                    "detail": str(fix_path),
                }
            )

        oracle_path = ORACLE_PATH
        oracle_valid = False
        oracle_detail: object = str(oracle_path)
        try:
            oracle = self.load_oracle()
            required_phases = {"initial_snapshot", "post_crud", "post_schema"}
            oracle_valid = required_phases.issubset(oracle)
            oracle_detail = {
                "path": str(oracle_path),
                "sha256": sha256_file(oracle_path) if oracle_path.is_file() else None,
                "phases": sorted(oracle),
            }
        except RuntimeError as exc:
            oracle_detail = sanitize_text(str(exc))
        v1_assertions.append(
            {
                "name": "oracle_file_exists",
                "status": "PASS" if oracle_path.exists() and oracle_valid else "FAIL",
                "detail": oracle_detail,
            }
        )

        v1_status = (
            "PASS" if all(a["status"] == "PASS" for a in v1_assertions) else "FAIL"
        )
        self.log_gate("01-harness-ready", v1_status, time.time() - t1, v1_assertions)
        if v1_status != "PASS":
            return {"status": "FAIL", "gate": "01-harness-ready"}

        return {"status": "PASS", "run_id": self.run_id}

    def run_e2e_acceptance(self) -> dict[str, Any]:
        """Execute Gates V2-V10 in sequence with strict fail-fast."""
        prep_res = self.prepare()
        if prep_res.get("status") != "PASS":
            return prep_res

        # Gate V2: 02-clean-bootstrap
        t2 = time.time()
        v2_assertions = []
        reset_code, reset_out, _ = self.run_cmd(
            ["uv", "run", "python", "scripts/cdc/local_lab.py", "reset", "--yes"]
        )
        v2_assertions.append(
            {
                "name": "lab_reset",
                "status": "PASS" if reset_code == 0 else "FAIL",
                "detail": reset_out.strip() or "Clean reset executed",
            }
        )
        if reset_code != 0:
            self.log_gate("02-clean-bootstrap", "FAIL", time.time() - t2, v2_assertions)
            return {"status": "FAIL", "gate": "02-clean-bootstrap"}

        boot_code, boot_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "bootstrap",
                "--run-id",
                self.dag_run_id("seed"),
                "--random-seed",
                "20260801",
            ]
        )
        v2_assertions.append(
            {
                "name": "lab_bootstrap_seed",
                "status": "PASS" if boot_code == 0 else "FAIL",
                "detail": boot_out.strip() or "Bootstrap completed",
            }
        )
        v2_status = (
            "PASS" if all(a["status"] == "PASS" for a in v2_assertions) else "FAIL"
        )
        self.log_gate("02-clean-bootstrap", v2_status, time.time() - t2, v2_assertions)
        if v2_status != "PASS":
            return {"status": "FAIL", "gate": "02-clean-bootstrap"}

        # Gate V3: 03-initial-snapshot
        t3 = time.time()
        v3_assertions = []
        stream_code, stream_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "start-streaming",
                "--wait-ready",
                "--timeout",
                "600",
            ]
        )
        v3_assertions.append(
            {
                "name": "start_streaming",
                "status": "PASS" if stream_code == 0 else "FAIL",
                "detail": stream_out.strip() or "Spark streaming services started",
            }
        )
        if stream_code != 0:
            self.log_gate(
                "03-initial-snapshot", "FAIL", time.time() - t3, v3_assertions
            )
            return {"status": "FAIL", "gate": "03-initial-snapshot"}

        observer_code, observer_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "start-serving-observer",
            ]
        )
        v3_assertions.append(
            {
                "name": "start_serving_observer",
                "status": "PASS" if observer_code == 0 else "FAIL",
                "detail": observer_out.strip() or "ClickHouse serving observer started",
            }
        )
        if observer_code != 0:
            self.log_gate(
                "03-initial-snapshot", "FAIL", time.time() - t3, v3_assertions
            )
            return {"status": "FAIL", "gate": "03-initial-snapshot"}

        wait1_code, wait1_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "wait-caught-up",
                "--timeout",
                "1200",
            ]
        )
        v3_assertions.append(
            {
                "name": "initial_snapshot_caught_up",
                "status": "PASS" if wait1_code == 0 else "FAIL",
                "detail": wait1_out.strip() or "Initial snapshot caught up",
            }
        )
        if wait1_code != 0:
            self.log_gate(
                "03-initial-snapshot", "FAIL", time.time() - t3, v3_assertions
            )
            return {"status": "FAIL", "gate": "03-initial-snapshot"}
        try:
            initial_oracle = ClickHouseProbe().inspect_stage_counts(
                "initial_snapshot",
                self.oracle["initial_snapshot"],
                MySQLProbe(),
            )
            initial_oracle_status = "PASS"
            initial_oracle_detail: object = initial_oracle
        except Exception as exc:
            initial_oracle_status = "FAIL"
            initial_oracle_detail = sanitize_text(str(exc))
        v3_assertions.append(
            {
                "name": "initial_snapshot_exact_oracle",
                "status": initial_oracle_status,
                "detail": initial_oracle_detail,
            }
        )
        v3_status = (
            "PASS" if all(a["status"] == "PASS" for a in v3_assertions) else "FAIL"
        )
        self.log_gate("03-initial-snapshot", v3_status, time.time() - t3, v3_assertions)
        if v3_status != "PASS":
            return {"status": "FAIL", "gate": "03-initial-snapshot"}

        # Gate V4: 04-crud-and-restart
        t4 = time.time()
        v4_assertions = []
        stop_code, stop_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "stop-streaming",
            ]
        )
        v4_assertions.append(
            {
                "name": "stop_spark_streaming",
                "status": "PASS" if stop_code == 0 else "FAIL",
                "detail": stop_out.strip() or "Spark streaming stopped",
            }
        )
        if stop_code != 0:
            self.log_gate(
                "04-crud-and-restart", "FAIL", time.time() - t4, v4_assertions
            )
            return {"status": "FAIL", "gate": "04-crud-and-restart"}

        probe = MySQLProbe()
        try:
            res_ins = probe.execute_fixture("insert.sql")
            res_upd = probe.execute_fixture("update.sql")
            res_del = probe.execute_fixture("delete.sql")
        except Exception as exc:
            v4_assertions.append(
                {
                    "name": "execute_crud_fixtures",
                    "status": "FAIL",
                    "detail": sanitize_text(str(exc)),
                }
            )
            self.log_gate(
                "04-crud-and-restart", "FAIL", time.time() - t4, v4_assertions
            )
            return {"status": "FAIL", "gate": "04-crud-and-restart"}
        v4_assertions.append(
            {
                "name": "execute_crud_fixtures",
                "status": "PASS",
                "detail": f"Executed insert ({res_ins['statements_count']} statements), update ({res_upd['statements_count']} statements), delete ({res_del['statements_count']} statements)",
            }
        )

        start_code, start_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "start-streaming",
                "--wait-ready",
                "--timeout",
                "600",
            ]
        )
        v4_assertions.append(
            {
                "name": "start_spark_streaming_recovery",
                "status": "PASS" if start_code == 0 else "FAIL",
                "detail": start_out.strip() or "Spark streaming restarted",
            }
        )
        restart_payload = parse_json_payload(start_out)
        v4_status = (
            "PASS" if all(a["status"] == "PASS" for a in v4_assertions) else "FAIL"
        )
        self.log_gate("04-crud-and-restart", v4_status, time.time() - t4, v4_assertions)
        if v4_status != "PASS":
            return {"status": "FAIL", "gate": "04-crud-and-restart"}

        # Gate V5: 05-caught-up
        t5 = time.time()
        v5_assertions = []
        wait2_code, wait2_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "wait-caught-up",
                "--timeout",
                "1200",
            ]
        )
        v5_assertions.append(
            {
                "name": "crud_caught_up",
                "status": "PASS" if wait2_code == 0 else "FAIL",
                "detail": wait2_out.strip() or "CRUD changes processed and caught up",
            }
        )
        if wait2_code != 0:
            self.log_gate("05-caught-up", "FAIL", time.time() - t5, v5_assertions)
            return {"status": "FAIL", "gate": "05-caught-up"}
        try:
            post_crud_oracle = ClickHouseProbe().inspect_stage_counts(
                "post_crud",
                self.oracle["post_crud"],
                operation_expected=self.oracle["crud_delta"],
            )
            post_crud_status = "PASS"
            post_crud_detail: object = post_crud_oracle
        except Exception as exc:
            post_crud_status = "FAIL"
            post_crud_detail = sanitize_text(str(exc))
        v5_assertions.append(
            {
                "name": "post_crud_exact_oracle",
                "status": post_crud_status,
                "detail": post_crud_detail,
            }
        )
        new_query_ids = restart_payload.get("new_query_ids")
        old_query_ids = restart_payload.get("old_query_ids")
        restart_fresh = (
            restart_payload.get("status") == "ready"
            and restart_payload.get("freshness_verified") is True
            and isinstance(old_query_ids, dict)
            and isinstance(new_query_ids, dict)
            and set(old_query_ids) == {"bronze", "silver"}
            and set(new_query_ids) == {"bronze", "silver"}
            and restart_payload.get("freshness_basis")
            == "status_updated_at_after_restart_barrier"
        )
        v5_assertions.append(
            {
                "name": "restart_freshness",
                "status": "PASS" if restart_fresh else "FAIL",
                "detail": restart_payload
                or start_out.strip()
                or "Restart freshness was not proven",
            }
        )
        v5_status = (
            "PASS" if all(a["status"] == "PASS" for a in v5_assertions) else "FAIL"
        )
        self.log_gate("05-caught-up", v5_status, time.time() - t5, v5_assertions)
        if v5_status != "PASS":
            return {"status": "FAIL", "gate": "05-caught-up"}

        # Gate V6: 06-serving-sync
        t6 = time.time()
        v6_assertions = []
        serving_code, serving_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "start-serving",
                "--build",
                "--timeout",
                "1800",
            ]
        )
        v6_assertions.append(
            {
                "name": "start_serving",
                "status": "PASS" if serving_code == 0 else "FAIL",
                "detail": serving_out.strip()
                or "Serving services started and became healthy",
            }
        )
        if serving_code != 0:
            self.log_gate(
                "06-serving-sync",
                "FAIL",
                time.time() - t6,
                v6_assertions,
            )
            return {"status": "FAIL", "gate": "06-serving-sync"}

        sync1_code, sync1_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "sync-serving",
                "--run-id",
                self.dag_run_id("crud_publish"),
                "--timeout",
                "1800",
            ]
        )
        sync1_payload = parse_json_payload(sync1_out)

        expected_entity_names = set(EXPECTED_SERVING_ENTITIES)

        def entity_count_mapping(
            payload: Mapping[str, Any], field: str
        ) -> dict[str, int] | None:
            raw_counts = payload.get(field)
            if (
                not isinstance(raw_counts, dict)
                or set(raw_counts) != expected_entity_names
            ):
                return None
            counts: dict[str, int] = {}
            for entity, value in raw_counts.items():
                if not isinstance(value, (int, float, str)):
                    return None
                try:
                    counts[str(entity)] = int(value)
                except (TypeError, ValueError):
                    return None
            return counts

        def entity_count_parity(payload: Mapping[str, Any]) -> bool:
            expected = entity_count_mapping(payload, "expected_entity_counts")
            materialized = entity_count_mapping(payload, "materialized_entity_counts")
            return (
                expected is not None
                and materialized is not None
                and expected == materialized
                and all(value > 0 for value in expected.values())
            )

        def zero_entity_counts(payload: Mapping[str, Any]) -> bool:
            expected = entity_count_mapping(payload, "expected_entity_counts")
            materialized = entity_count_mapping(payload, "materialized_entity_counts")
            return (
                expected is not None
                and materialized is not None
                and expected == materialized
                and all(value == 0 for value in expected.values())
            )

        def snapshot_ids_valid(payload: Mapping[str, Any]) -> bool:
            snapshots = payload.get("iceberg_snapshot_ids")
            return (
                isinstance(snapshots, dict)
                and set(snapshots) == expected_entity_names
                and all(positive_int(value) for value in snapshots.values())
            )

        def target_offsets_valid(payload: Mapping[str, Any]) -> bool:
            return valid_serving_target_offsets(payload.get("target_offsets"))

        sync1_entity_parity = entity_count_parity(sync1_payload)

        sync1_valid = (
            sync1_code == 0
            and sync1_payload.get("status") == "succeeded"
            and sync1_payload.get("sync_run_status") == "SUCCEEDED"
            and sync1_payload.get("is_noop") is False
            and positive_int(sync1_payload.get("sync_run_seq"))
            and isinstance(sync1_payload.get("sync_run_id"), str)
            and bool(sync1_payload.get("sync_run_id"))
            and isinstance(sync1_payload.get("target_transaction_id"), str)
            and bool(sync1_payload.get("target_transaction_id"))
            and target_offsets_valid(sync1_payload)
            and snapshot_ids_valid(sync1_payload)
            and positive_int(sync1_payload.get("expected_event_count"))
            and positive_int(sync1_payload.get("materialized_event_count"))
            and int(sync1_payload.get("expected_event_count", 0))
            == int(sync1_payload.get("materialized_event_count", 0))
            and sync1_entity_parity
            and isinstance(sync1_payload.get("dbt_result"), dict)
            and sync1_payload.get("dbt_result", {}).get("success") is True
        )
        v6_assertions.append(
            {
                "name": "sync_serving_crud",
                "status": "PASS" if sync1_valid else "FAIL",
                "detail": sync1_out.strip()
                or "First CRUD serving sync was not a non-NOOP publication",
            }
        )
        if not sync1_valid:
            self.log_gate("06-serving-sync", "FAIL", time.time() - t6, v6_assertions)
            return {"status": "FAIL", "gate": "06-serving-sync"}

        sync_repeat_code, sync_repeat_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "sync-serving",
                "--run-id",
                self.dag_run_id("crud_repeat"),
                "--timeout",
                "1800",
            ]
        )
        sync_repeat_payload = parse_json_payload(sync_repeat_out)
        repeat_entity_counts_zero = zero_entity_counts(sync_repeat_payload)
        repeat_valid = (
            sync_repeat_code == 0
            and sync_repeat_payload.get("status") == "succeeded"
            and sync_repeat_payload.get("sync_run_status") == "NOOP"
            and sync_repeat_payload.get("is_noop") is True
            and sync_repeat_payload.get("target_transaction_id")
            == sync1_payload.get("target_transaction_id")
            and sync_repeat_payload.get("iceberg_snapshot_ids")
            == sync1_payload.get("iceberg_snapshot_ids")
            and sync_repeat_payload.get("target_offsets") == {}
            and snapshot_ids_valid(sync_repeat_payload)
            and positive_int(sync_repeat_payload.get("sync_run_seq"))
            and sync_repeat_payload.get("sync_run_seq")
            != sync1_payload.get("sync_run_seq")
            and isinstance(sync_repeat_payload.get("sync_run_id"), str)
            and bool(sync_repeat_payload.get("sync_run_id"))
            and sync_repeat_payload.get("sync_run_id")
            != sync1_payload.get("sync_run_id")
            and int(sync_repeat_payload.get("expected_event_count") or 0) == 0
            and int(sync_repeat_payload.get("materialized_event_count") or 0) == 0
            and repeat_entity_counts_zero
        )
        v6_assertions.append(
            {
                "name": "sync_serving_crud_repeat_noop",
                "status": "PASS" if repeat_valid else "FAIL",
                "detail": sync_repeat_out.strip()
                or "Repeated CRUD serving sync was not an authoritative NOOP",
            }
        )
        v6_status = (
            "PASS" if all(a["status"] == "PASS" for a in v6_assertions) else "FAIL"
        )
        self.log_gate("06-serving-sync", v6_status, time.time() - t6, v6_assertions)
        if v6_status != "PASS":
            return {"status": "FAIL", "gate": "06-serving-sync"}

        # Gate V7: 07-dbt-and-stable-views
        t7 = time.time()
        v7_assertions = []
        val_serving_code, val_serving_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "validate",
                "--scope",
                "serving",
            ]
        )
        v7_assertions.append(
            {
                "name": "serving_static_validation",
                "status": "PASS" if val_serving_code == 0 else "FAIL",
                "detail": val_serving_out.strip() or "Static serving validation passed",
            }
        )
        if val_serving_code != 0:
            self.log_gate(
                "07-dbt-and-stable-views", "FAIL", time.time() - t7, v7_assertions
            )
            return {"status": "FAIL", "gate": "07-dbt-and-stable-views"}

        live_serving_code, live_serving_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "validate-serving",
                "--sync-run-seq",
                str(sync1_payload.get("sync_run_seq", "")),
                "--sync-run-id",
                str(sync1_payload.get("sync_run_id", "")),
            ]
        )
        live_serving_payload = parse_json_payload(live_serving_out)
        live_serving_valid = (
            live_serving_code == 0 and live_serving_payload.get("status") == "ready"
        )
        v7_assertions.append(
            {
                "name": "dbt_and_stable_views_validation",
                "status": "PASS" if live_serving_valid else "FAIL",
                "detail": live_serving_payload
                or live_serving_out.strip()
                or "Candidate dbt build evidence and stable views verified",
            }
        )
        v7_status = (
            "PASS" if all(a["status"] == "PASS" for a in v7_assertions) else "FAIL"
        )
        self.log_gate(
            "07-dbt-and-stable-views", v7_status, time.time() - t7, v7_assertions
        )
        if v7_status != "PASS":
            return {"status": "FAIL", "gate": "07-dbt-and-stable-views"}

        # Gate V8: 08-additive-schema
        t8 = time.time()
        v8_assertions = []
        try:
            res_add = probe.execute_fixture("add_nullable_column.sql")
            res_evt = probe.execute_fixture("emit_nullable_event.sql")
        except Exception as exc:
            v8_assertions.append(
                {
                    "name": "execute_nullable_schema_fixtures",
                    "status": "FAIL",
                    "detail": sanitize_text(str(exc)),
                }
            )
            self.log_gate("08-additive-schema", "FAIL", time.time() - t8, v8_assertions)
            return {"status": "FAIL", "gate": "08-additive-schema"}

        fixtures_valid = all(
            result.get("status") == "EXECUTED"
            and positive_int(result.get("statements_count"))
            for result in (res_add, res_evt)
        )
        v8_assertions.append(
            {
                "name": "execute_nullable_schema_fixtures",
                "status": "PASS" if fixtures_valid else "FAIL",
                "detail": {
                    "add_column": res_add,
                    "emit_event": res_evt,
                },
            }
        )
        if not fixtures_valid:
            self.log_gate("08-additive-schema", "FAIL", time.time() - t8, v8_assertions)
            return {"status": "FAIL", "gate": "08-additive-schema"}

        try:
            source_schema_evidence = probe.inspect_nullable_event(
                "wave2_customer_001", "sao paulo stage v"
            )
            source_schema_status = "PASS"
            source_schema_detail: object = source_schema_evidence
        except Exception as exc:
            source_schema_status = "FAIL"
            source_schema_detail = sanitize_text(str(exc))
        v8_assertions.append(
            {
                "name": "mysql_nullable_source_contract",
                "status": source_schema_status,
                "detail": source_schema_detail,
            }
        )
        if source_schema_status != "PASS":
            self.log_gate("08-additive-schema", "FAIL", time.time() - t8, v8_assertions)
            return {"status": "FAIL", "gate": "08-additive-schema"}
        wait3_code, wait3_out, wait3_err = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "wait-caught-up",
                "--timeout",
                "1200",
            ]
        )
        v8_assertions.append(
            {
                "name": "schema_evolution_caught_up",
                "status": "PASS" if wait3_code == 0 else "FAIL",
                "detail": wait3_out.strip()
                or wait3_err.strip()
                or "Additive schema event caught up",
            }
        )
        if wait3_code != 0:
            self.log_gate("08-additive-schema", "FAIL", time.time() - t8, v8_assertions)
            return {"status": "FAIL", "gate": "08-additive-schema"}
        sync2_code, sync2_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "sync-serving",
                "--run-id",
                self.dag_run_id("schema_publish"),
                "--timeout",
                "1800",
            ]
        )
        sync2_payload = parse_json_payload(sync2_out)
        sync2_entity_parity = entity_count_parity(sync2_payload)
        sync2_valid = (
            sync2_code == 0
            and sync2_payload.get("status") == "succeeded"
            and sync2_payload.get("sync_run_status") == "SUCCEEDED"
            and sync2_payload.get("is_noop") is False
            and positive_int(sync2_payload.get("sync_run_seq"))
            and isinstance(sync2_payload.get("sync_run_id"), str)
            and bool(sync2_payload.get("sync_run_id"))
            and sync2_payload.get("sync_run_seq") != sync1_payload.get("sync_run_seq")
            and sync2_payload.get("sync_run_id") != sync1_payload.get("sync_run_id")
            and positive_int(sync2_payload.get("expected_event_count"))
            and positive_int(sync2_payload.get("materialized_event_count"))
            and int(sync2_payload.get("expected_event_count", 0))
            == int(sync2_payload.get("materialized_event_count", 0))
            and isinstance(sync2_payload.get("target_transaction_id"), str)
            and bool(sync2_payload.get("target_transaction_id"))
            and target_offsets_valid(sync2_payload)
            and snapshot_ids_valid(sync2_payload)
            and valid_additive_snapshot_transition(sync1_payload, sync2_payload)
            and sync2_entity_parity
            and isinstance(sync2_payload.get("dbt_result"), dict)
            and sync2_payload.get("dbt_result", {}).get("success") is True
        )
        v8_assertions.append(
            {
                "name": "additive_schema_publish",
                "status": "PASS" if sync2_valid else "FAIL",
                "detail": sync2_out.strip()
                or f"Nullable column added ({res_add['fixture']}) and published ({res_evt['fixture']})",
            }
        )

        if sync2_valid:
            try:
                clickhouse_schema_evidence = ClickHouseProbe().inspect_nullable_event(
                    "wave2_customer_001", "sao paulo stage v"
                )
                clickhouse_schema_status = "PASS"
                clickhouse_schema_detail: object = clickhouse_schema_evidence
            except Exception as exc:
                clickhouse_schema_status = "FAIL"
                clickhouse_schema_detail = sanitize_text(str(exc))
        else:
            clickhouse_schema_status = "FAIL"
            clickhouse_schema_detail = "Skipped Bronze/Silver/serving probe because schema publish was not valid"
        v8_assertions.append(
            {
                "name": "nullable_avro_bronze_silver_serving_propagation",
                "status": clickhouse_schema_status,
                "detail": clickhouse_schema_detail,
            }
        )

        if sync2_valid:
            try:
                post_schema_oracle = ClickHouseProbe().inspect_stage_counts(
                    "post_schema", self.oracle["post_schema"]
                )
                post_schema_oracle_status = "PASS"
                post_schema_oracle_detail: object = post_schema_oracle
            except Exception as exc:
                post_schema_oracle_status = "FAIL"
                post_schema_oracle_detail = sanitize_text(str(exc))
        else:
            post_schema_oracle_status = "FAIL"
            post_schema_oracle_detail = (
                "Skipped post-schema exact oracle because publish was invalid"
            )
        v8_assertions.append(
            {
                "name": "post_schema_exact_oracle",
                "status": post_schema_oracle_status,
                "detail": post_schema_oracle_detail,
            }
        )

        if sync2_valid:
            schema_validation_code, schema_validation_out, schema_validation_err = (
                self.run_cmd(
                    [
                        "uv",
                        "run",
                        "python",
                        "scripts/cdc/local_lab.py",
                        "validate-serving",
                        "--sync-run-seq",
                        str(sync2_payload.get("sync_run_seq", "")),
                        "--sync-run-id",
                        str(sync2_payload.get("sync_run_id", "")),
                    ]
                )
            )
            schema_validation_payload = parse_json_payload(schema_validation_out)
            schema_validation_valid = (
                schema_validation_code == 0
                and schema_validation_payload.get("status") == "ready"
            )
            schema_validation_detail: object = (
                schema_validation_payload
                or schema_validation_out.strip()
                or schema_validation_err.strip()
            )
        else:
            schema_validation_valid = False
            schema_validation_detail = "Skipped post-schema serving validation because schema publish was not valid"
        v8_assertions.append(
            {
                "name": "post_schema_candidate_dbt_and_stable_parity",
                "status": "PASS" if schema_validation_valid else "FAIL",
                "detail": schema_validation_detail,
            }
        )
        v8_status = (
            "PASS" if all(a["status"] == "PASS" for a in v8_assertions) else "FAIL"
        )
        self.log_gate("08-additive-schema", v8_status, time.time() - t8, v8_assertions)
        if v8_status != "PASS":
            return {"status": "FAIL", "gate": "08-additive-schema"}

        # Gate V9: 09-rebuild
        t9 = time.time()
        v9_assertions = []
        rebuild_code, rebuild_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "rebuild-serving",
                "--yes",
                "--run-id",
                self.dag_run_id("rebuild"),
                "--timeout",
                "5400",
            ],
            timeout=6000.0,
        )
        rebuild_payload = parse_json_payload(rebuild_out)
        rebuild_basic_valid = (
            rebuild_code == 0
            and rebuild_payload.get("status") == "succeeded"
            and positive_int(rebuild_payload.get("sync_run_seq"))
            and isinstance(rebuild_payload.get("sync_run_id"), str)
            and bool(rebuild_payload.get("sync_run_id"))
            and positive_int(rebuild_payload.get("expected_event_count"))
            and positive_int(rebuild_payload.get("materialized_event_count"))
            and int(rebuild_payload.get("expected_event_count", 0))
            == int(rebuild_payload.get("materialized_event_count", 0))
            and isinstance(rebuild_payload.get("iceberg_snapshot_ids"), dict)
            and set(rebuild_payload.get("iceberg_snapshot_ids", {}))
            == {
                "customers",
                "orders",
                "order_items",
                "order_payments",
                "order_reviews",
                "products",
                "sellers",
                "product_category_translation",
            }
        )
        v9_assertions.append(
            {
                "name": "rebuild_serving_from_iceberg",
                "status": "PASS" if rebuild_basic_valid else "FAIL",
                "detail": rebuild_payload
                or rebuild_out.strip()
                or "ClickHouse rebuilt strictly from Iceberg",
            }
        )
        if rebuild_basic_valid:
            rebuild_validation_code, rebuild_validation_out, rebuild_validation_err = (
                self.run_cmd(
                    [
                        "uv",
                        "run",
                        "python",
                        "scripts/cdc/local_lab.py",
                        "validate-rebuild",
                        "--sync-run-seq",
                        str(rebuild_payload.get("sync_run_seq", "")),
                        "--sync-run-id",
                        str(rebuild_payload.get("sync_run_id", "")),
                    ]
                )
            )
            rebuild_validation_payload = parse_json_payload(rebuild_validation_out)
            rebuild_validation_valid = (
                rebuild_validation_code == 0
                and rebuild_validation_payload.get("status") == "ready"
            )
            rebuild_validation_detail: object = (
                rebuild_validation_payload
                or rebuild_validation_out.strip()
                or rebuild_validation_err.strip()
            )
        else:
            rebuild_validation_valid = False
            rebuild_validation_detail = "Skipped post-rebuild parity validation because rebuild evidence was invalid"
        v9_assertions.append(
            {
                "name": "rebuild_iceberg_current_gold_and_dbt_parity",
                "status": "PASS" if rebuild_validation_valid else "FAIL",
                "detail": rebuild_validation_detail,
            }
        )
        v9_status = (
            "PASS" if all(a["status"] == "PASS" for a in v9_assertions) else "FAIL"
        )
        self.log_gate("09-rebuild", v9_status, time.time() - t9, v9_assertions)
        if v9_status != "PASS":
            return {"status": "FAIL", "gate": "09-rebuild"}

        # Gate V10: 10-final
        t10 = time.time()
        v10_assertions = []
        if rebuild_basic_valid:
            final_parity_code, final_parity_out, final_parity_err = self.run_cmd(
                [
                    "uv",
                    "run",
                    "python",
                    "scripts/cdc/local_lab.py",
                    "validate-rebuild",
                    "--sync-run-seq",
                    str(rebuild_payload.get("sync_run_seq", "")),
                    "--sync-run-id",
                    str(rebuild_payload.get("sync_run_id", "")),
                ]
            )
            final_parity_payload = parse_json_payload(final_parity_out)
            final_parity_valid = (
                final_parity_code == 0 and final_parity_payload.get("status") == "ready"
            )
            final_parity_detail: object = (
                final_parity_payload
                or final_parity_out.strip()
                or final_parity_err.strip()
            )
        else:
            final_parity_valid = False
            final_parity_detail = (
                "Skipped final parity validation because rebuild evidence was invalid"
            )
        v10_assertions.append(
            {
                "name": "final_rebuild_current_and_gold_parity",
                "status": "PASS" if final_parity_valid else "FAIL",
                "detail": final_parity_detail,
            }
        )
        if rebuild_basic_valid:
            final_control_code, final_control_out, final_control_err = self.run_cmd(
                [
                    "uv",
                    "run",
                    "python",
                    "scripts/cdc/local_lab.py",
                    "validate-final",
                    "--sync-run-seq",
                    str(rebuild_payload.get("sync_run_seq", "")),
                    "--sync-run-id",
                    str(rebuild_payload.get("sync_run_id", "")),
                ]
            )
            final_control_payload = parse_json_payload(final_control_out)
            final_control_valid = (
                final_control_code == 0
                and final_control_payload.get("status") == "ready"
            )
            final_control_detail: object = (
                final_control_payload
                or final_control_out.strip()
                or final_control_err.strip()
            )
        else:
            final_control_valid = False
            final_control_detail = "Skipped final control-plane validation because rebuild evidence was invalid"
        v10_assertions.append(
            {
                "name": "final_independent_control_plane_check",
                "status": "PASS" if final_control_valid else "FAIL",
                "detail": final_control_detail,
            }
        )
        status_code, status_out, _ = self.run_cmd(
            [
                "uv",
                "run",
                "python",
                "scripts/cdc/local_lab.py",
                "status",
                "--require",
                "serving",
            ]
        )
        status_payload = parse_json_payload(status_out)
        status_valid = status_code == 0 and status_payload.get("status") == "ready"
        v10_assertions.append(
            {
                "name": "final_serving_status_check",
                "status": "PASS" if status_valid else "FAIL",
                "detail": status_payload or status_out.strip() or "Final status ready",
            }
        )
        v10_status = (
            "PASS" if all(a["status"] == "PASS" for a in v10_assertions) else "FAIL"
        )
        self.log_gate("10-final", v10_status, time.time() - t10, v10_assertions)
        if v10_status != "PASS":
            return {"status": "FAIL", "gate": "10-final"}

        return {"status": "PASS", "run_id": self.run_id}

    def generate_checksums(self) -> dict[str, str]:
        """Compute SHA-256 for all evidence files and write checksums.json."""
        checksums: dict[str, str] = {}
        for p in sorted(self.evidence_dir.glob("**/*")):
            if not p.is_file():
                continue
            rel_path = str(p.relative_to(self.evidence_dir)).replace("\\", "/")
            if rel_path not in ("checksums.json", "summary.json"):
                checksums[rel_path] = sha256_file(p)

        (self.evidence_dir / "checksums.json").write_text(
            json.dumps(checksums, indent=2, sort_keys=True), encoding="utf-8"
        )
        return checksums

    def generate_manifests_and_checksums(self) -> dict[str, str]:
        """Write checksums.json and the manifest summary.json."""
        checksums = self.generate_checksums()

        missing_gates = [g for g in MANDATORY_GATES if g not in self.gate_results]
        failed_or_skipped = [
            g for g, res in self.gate_results.items() if res.get("status") != "PASS"
        ]

        overall_status = (
            "PASS"
            if not missing_gates
            and not failed_or_skipped
            and self.runtime_cleanup.get("status") == "PASS"
            else "FAIL"
        )

        summary = {
            "run_id": self.run_id,
            "overall_status": overall_status,
            "started_at": self.start_time,
            "finished_at": datetime.now(UTC).isoformat(),
            "compose_project": EXPECTED_COMPOSE_PROJECT,
            "mandatory_gates": list(MANDATORY_GATES),
            "missing_gates": missing_gates,
            "failed_or_skipped_gates": failed_or_skipped,
            "gates": self.gate_results,
            "runtime_cleanup": self.runtime_cleanup,
        }

        (self.evidence_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )

        return checksums

    def write_report(self) -> Path:
        """Create final Stage V validation report in docs/reports/mysql-spark-iceberg-stage-v-validation.md."""
        report_path = (
            ROOT / "docs" / "reports" / "mysql-spark-iceberg-stage-v-validation.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        summary_file = self.evidence_dir / "summary.json"
        summary_data = (
            json.loads(summary_file.read_text(encoding="utf-8"))
            if summary_file.exists()
            else {}
        )

        overall = summary_data.get("overall_status", "UNKNOWN")
        started = summary_data.get("started_at", "N/A")
        finished = summary_data.get("finished_at", "N/A")
        gates = summary_data.get("gates", {})
        if not isinstance(gates, dict):
            gates = {}
        passed_gate_count = sum(
            1
            for gate_name in MANDATORY_GATES
            if isinstance(gates.get(gate_name), dict)
            and gates[gate_name].get("status") == "PASS"
        )
        evidence_assertions = {
            gate_name: gates.get(gate_name, {"status": "MISSING"})
            for gate_name in MANDATORY_GATES
        }
        evidence_json = json.dumps(
            {
                "mandatory_gates": list(MANDATORY_GATES),
                "passed_gate_count": passed_gate_count,
                "gate_count": len(MANDATORY_GATES),
                "gates": evidence_assertions,
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        report_accepted = not verify_evidence_directory(self.evidence_dir, summary_data)

        report_content = f"""# Stage V Candidate E2E Validation Report

- **Status**: `{overall}`
- **Run ID**: `{self.run_id}`
- **Compose Project**: `{EXPECTED_COMPOSE_PROJECT}`
- **Started At**: `{started}`
- **Finished At**: `{finished}`

---

## 1. Final Verdict

Stage V validation completed with status `{overall}`.

{"All mandatory gates passed in a single clean-domain run." if report_accepted else "Validation evidence is not accepted."}

- **Stage L Authorization**: {"`AUTHORIZED` (allowed to proceed to Stage L)" if report_accepted else "`FORBIDDEN` (Stage L blocked)"}

---

## 2. Gate Execution Results (V0 - V10)

| Gate | Name | Status | Duration (s) |
| --- | --- | --- | ---: |
"""
        for gate_name, raw_gate_info in gates.items():
            gate_info = raw_gate_info if isinstance(raw_gate_info, dict) else {}
            status = gate_info.get("status", "N/A")
            duration = gate_info.get("duration_seconds", 0)
            report_content += (
                f"| `{gate_name}` | {gate_name} | `{status}` | {duration} |\n"
            )

        report_content += f"""
---

## 3. Evidence-Derived Assertions

The following machine-readable block is rendered directly from the persisted
gate summaries. Counts, IDs, command output and parity details are not
reconstructed from static claims.

- **Passed mandatory gates**: `{passed_gate_count}/{len(MANDATORY_GATES)}`

```json
{evidence_json}
```

---

## 4. Evidence Artifacts

Raw evidence persisted in `data/stage-v-evidence/{self.run_id}/`.
"""
        report_path.write_text(report_content, encoding="utf-8")
        return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage V Candidate E2E Validation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # prepare
    prep_parser = subparsers.add_parser("prepare")
    prep_parser.add_argument("--run-id", required=True)
    prep_parser.add_argument("--evidence-dir", required=True, type=Path)

    # run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--evidence-dir", required=True, type=Path)
    run_parser.add_argument("--confirm-reset", action="store_true", required=True)

    # report
    rep_parser = subparsers.add_parser("report")
    rep_parser.add_argument("--evidence-dir", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "prepare":
        orchestrator = StageVOrchestrator(args.run_id, args.evidence_dir)
        res = orchestrator.prepare()
        orchestrator.generate_manifests_and_checksums()
        print(json.dumps(res, indent=2))
        sys.exit(0 if res.get("status") == "PASS" else 1)

    elif args.command == "run":
        if not args.confirm_reset:
            print(
                json.dumps(
                    {"status": "FAIL", "reason": "--confirm-reset required for run"},
                    indent=2,
                )
            )
            sys.exit(1)

        orchestrator = StageVOrchestrator(args.run_id, args.evidence_dir)
        orchestrator.clear_evidence()
        try:
            res = orchestrator.run_e2e_acceptance()
        except Exception as exc:
            res = {
                "status": "ERROR",
                "reason": "UNHANDLED_EXCEPTION",
                "error": sanitize_text(str(exc)),
            }

        # A successful run has complete machine-readable evidence, so its
        # disposable Compose project can be stopped.  A failed run is kept
        # alive deliberately: container logs are part of the next diagnostic
        # step and removing the containers would destroy that context.
        if res.get("status") == "PASS":
            cleanup_ok = orchestrator.cleanup_runtime()
            if not cleanup_ok:
                res = {
                    "status": "FAIL",
                    "reason": "RUNTIME_CLEANUP_FAILED",
                    "gate": res.get("gate") or "10-final",
                }
        else:
            orchestrator.preserve_runtime_for_diagnostics(res)

        # Preserve an honest partial manifest on failure.  The summary derives
        # its verdict from the gates actually recorded above and therefore
        # cannot turn an interrupted run into a successful declaration.
        orchestrator.generate_manifests_and_checksums()
        summary_path = args.evidence_dir / "summary.json"
        summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
        acceptance_errors = verify_evidence_directory(args.evidence_dir, summary_data)
        if res.get("status") != "PASS" or acceptance_errors:
            print(
                json.dumps(
                    {
                        "status": "FAIL",
                        "reason": "RUN_FAILED",
                        "gate": res.get("gate"),
                        "error": res.get("error"),
                        "acceptance_errors": acceptance_errors,
                    },
                    indent=2,
                )
            )
            sys.exit(1)

        report_path = orchestrator.write_report()
        print(
            json.dumps(
                {"status": "PASS", "run_id": args.run_id, "report": str(report_path)},
                indent=2,
            )
        )
        sys.exit(0)

    elif args.command == "report":
        evidence_dir = args.evidence_dir
        summary_path = evidence_dir / "summary.json"
        if not summary_path.exists():
            print(
                json.dumps({"status": "FAIL", "reason": "SUMMARY_NOT_FOUND"}, indent=2)
            )
            sys.exit(1)

        summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
        run_id = summary_data.get("run_id", "unknown")
        orchestrator = StageVOrchestrator(run_id, evidence_dir)
        acceptance_errors = verify_evidence_directory(evidence_dir, summary_data)
        report_path = orchestrator.write_report()
        if acceptance_errors:
            print(
                json.dumps(
                    {
                        "status": "FAIL",
                        "reason": "SUMMARY_NOT_ACCEPTED",
                        "report": str(report_path),
                        "errors": acceptance_errors,
                    },
                    indent=2,
                )
            )
            sys.exit(1)

        print(json.dumps({"status": "PASS", "report": str(report_path)}, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
