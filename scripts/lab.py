"""Normative local/GCP/parity lifecycle command surface.

The legacy ``scripts/cdc/local_lab.py`` remains available for compatibility,
but new target-scoped operations enter through this module. GCP commands
perform local preflight checks before invoking Docker, Terraform, or future
cloud tooling; importing this module never contacts a cloud API.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.cdc import local_lab
from scripts.gcp.cost_evidence import (
    load_cost_evidence,
    pending_cost_report,
    write_cost_report,
)
from scripts.gcp.migrations import (
    list_migrations,
    migration_manifest,
    render_migration,
)
from scripts.gcp.vertical_slice import (
    DEFAULT_BRIDGE_DATASET,
    build_probe_plan,
    validate_probe_plan,
    write_probe_plan,
)
from scripts.orchestration.compose_profiles import (
    LakehouseTarget,
    compose_profiles,
    validate_profile_selection,
)
from scripts.serving.parity import (
    DEFAULT_OUTPUT_DIR as DEFAULT_PARITY_OUTPUT_DIR,
)
from scripts.serving.parity import (
    compare_evidence_files,
    pending_report,
    read_report,
    write_report,
)


def _emit(command: str, status: str, **fields: object) -> int:
    payload = {"command": command, **fields, "status": status}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
    return 0 if status in {"ready", "accepted", "blocked"} else 1


def _legacy(arguments: Sequence[str]) -> int:
    return int(local_lab.main(arguments))


def _compose_command(profiles: Sequence[str], arguments: Sequence[str]) -> list[str]:
    selected = validate_profile_selection(profiles)
    command = ["docker", "compose"]
    for profile in selected:
        command.extend(("--profile", profile))
    command.extend(arguments)
    return command


def _run_compose(
    profiles: Sequence[str],
    arguments: Sequence[str],
    *,
    timeout: float = 300.0,
) -> tuple[int, str]:
    command = _compose_command(profiles, arguments)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    output = (completed.stderr or completed.stdout or "").strip()
    return completed.returncode, output[-4000:]


def _gcp_preflight() -> dict[str, object]:
    project = (
        os.environ.get("GCP_LAKEHOUSE_PROJECT_ID", "").strip()
        or os.environ.get("GCP_PROJECT_ID", "").strip()
        or os.environ.get("TF_VAR_" + "project_id", "").strip()
    )
    region = (
        os.environ.get("GCP_REGION", "").strip()
        or os.environ.get("TF_VAR_" + "region", "").strip()
    )
    adc_path = (
        os.environ.get("GCP_SPARK_ADC_SOURCE_FILE", "").strip()
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    )
    resolved_adc_path = Path(adc_path)
    if adc_path and not resolved_adc_path.is_absolute():
        resolved_adc_path = ROOT / resolved_adc_path
    adc_available = bool(adc_path) and resolved_adc_path.is_file()
    checks = {
        "project_id": bool(project),
        "region": bool(region),
        "adc_file": adc_available,
        "terraform": shutil.which("terraform") is not None,
        "gcloud": shutil.which("gcloud") is not None,
    }
    missing = [name for name, passed in checks.items() if not passed]
    return {
        "checks": checks,
        "missing": missing,
        "project_id": project or None,
        "region": region or None,
        "adc_path": adc_path or None,
    }


def _gcp_preflight_command(_: argparse.Namespace) -> int:
    result = _gcp_preflight()
    return _emit(
        "gcp preflight",
        "ready" if not result["missing"] else "blocked",
        **result,
    )


def _gcp_up(args: argparse.Namespace) -> int:
    preflight = _gcp_preflight()
    missing = preflight["missing"]
    if isinstance(missing, list) and missing and not args.allow_missing_auth:
        return _emit(
            "gcp up",
            "blocked",
            reason=(
                "GCP preflight is incomplete; use --allow-missing-auth only "
                "for local profile rendering"
            ),
            **preflight,
        )
    profiles = compose_profiles(LakehouseTarget.GCP)
    code, output = _run_compose(
        profiles,
        ["up", "-d", *(["--build"] if args.build else [])],
        timeout=args.timeout,
    )
    return _emit(
        "gcp up",
        "ready" if code == 0 else "failed",
        profiles=list(profiles),
        output=output,
        streaming_started=False,
        preflight=preflight,
    )


def _gcp_down(args: argparse.Namespace) -> int:
    profiles = compose_profiles(LakehouseTarget.GCP)
    code, output = _run_compose(
        profiles, ["down", "--remove-orphans"], timeout=args.timeout
    )
    return _emit(
        "gcp down",
        "ready" if code == 0 else "failed",
        profiles=list(profiles),
        output=output,
    )


def _gcp_streaming(args: argparse.Namespace) -> int:
    profiles = compose_profiles(LakehouseTarget.GCP, streaming=True)
    if args.action == "status":
        code, output = _run_compose(profiles, ["ps", "--all"], timeout=60)
        return _emit(
            "gcp streaming status",
            "ready" if code == 0 else "failed",
            profiles=list(profiles),
            output=output,
        )
    if args.action == "stop":
        code, output = _run_compose(profiles, ["stop"], timeout=args.timeout)
        return _emit(
            "gcp streaming stop",
            "ready" if code == 0 else "failed",
            profiles=list(profiles),
            output=output,
        )

    preflight = _gcp_preflight()
    missing = preflight["missing"]
    if isinstance(missing, list) and missing and not args.allow_missing_auth:
        return _emit(
            "gcp streaming start",
            "blocked",
            reason="GCP preflight is incomplete",
            **preflight,
        )
    code, output = _run_compose(
        profiles,
        ["up", "-d", *(["--build"] if args.build else [])],
        timeout=args.timeout,
    )
    return _emit(
        "gcp streaming start",
        "ready" if code == 0 else "failed",
        profiles=list(profiles),
        output=output,
        streaming_started=code == 0,
        preflight=preflight,
    )


def _gcp_vertical_slice(args: argparse.Namespace) -> int:
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    if args.action == "report":
        if not output.is_file():
            return _emit(
                "gcp vertical-slice report",
                "blocked",
                reason=f"probe plan does not exist: {output}",
            )
        try:
            plan = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return _emit("gcp vertical-slice report", "failed", error=str(exc))
        errors = validate_probe_plan(plan)
        return _emit(
            "gcp vertical-slice report",
            "blocked" if errors or plan.get("cloud_execution") != "READY" else "ready",
            plan_path=str(output),
            errors=errors,
            cloud_execution=plan.get("cloud_execution"),
            decision=None,
        )

    preflight = _gcp_preflight()
    project_id = args.project_id or preflight.get("project_id")
    catalog_id = args.catalog_id or os.environ.get("GCP_LAKEHOUSE_CATALOG_ID", "")
    if not project_id or not catalog_id:
        return _emit(
            "gcp vertical-slice run",
            "blocked",
            reason="project_id and catalog_id are required to render the plan",
            preflight=preflight,
        )
    try:
        plan = build_probe_plan(
            str(project_id),
            str(catalog_id),
            args.bridge_dataset,
        )
        write_probe_plan(output, plan)
    except (OSError, ValueError) as exc:
        return _emit("gcp vertical-slice run", "failed", error=str(exc))

    missing = preflight["missing"]
    if isinstance(missing, list) and missing and not args.allow_missing_auth:
        return _emit(
            "gcp vertical-slice run",
            "blocked",
            reason="probe plan written; GCP preflight is incomplete",
            plan_path=str(output),
            preflight=preflight,
            cloud_execution=plan["cloud_execution"],
        )
    return _emit(
        "gcp vertical-slice run",
        "blocked",
        reason=(
            "probe plan is ready, but the cloud execution and manual decision "
            "require a real GCP run"
        ),
        plan_path=str(output),
        preflight=preflight,
        cloud_execution=plan["cloud_execution"],
    )


def _gcp_migrate(args: argparse.Namespace) -> int:
    try:
        migrations = list_migrations()
    except (OSError, ValueError) as exc:
        return _emit("gcp migrate", "failed", error=str(exc))

    if args.action == "status":
        return _emit(
            "gcp migrate status",
            "ready",
            migrations=migration_manifest(),
            cloud_execution="NOT_RUN",
        )

    project_id = args.project_id or os.environ.get("GCP_PROJECT_ID", "")
    catalog_id = args.catalog_id or os.environ.get("GCP_LAKEHOUSE_CATALOG_ID", "")
    if not project_id or not catalog_id:
        return _emit(
            f"gcp migrate {args.action}",
            "blocked",
            reason="project_id and catalog_id are required",
        )

    if args.action == "render":
        output = Path(args.output)
        if not output.is_absolute():
            output = ROOT / output
        try:
            output.mkdir(parents=True, exist_ok=True)
            rendered_paths: list[str] = []
            for migration in migrations:
                target = output / migration.path.name
                target.write_text(
                    render_migration(migration, project_id, catalog_id),
                    encoding="utf-8",
                )
                rendered_paths.append(str(target))
            (output / "manifest.json").write_text(
                json.dumps(
                    {
                        "project_id": project_id,
                        "catalog_id": catalog_id,
                        "migrations": migration_manifest(),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError) as exc:
            return _emit("gcp migrate render", "failed", error=str(exc))
        return _emit(
            "gcp migrate render",
            "accepted",
            output=str(output),
            rendered_paths=rendered_paths,
            cloud_execution="NOT_RUN",
        )

    preflight = _gcp_preflight()
    missing = preflight["missing"]
    if isinstance(missing, list) and missing and not args.allow_missing_auth:
        return _emit(
            "gcp migrate apply",
            "blocked",
            reason="GCP preflight is incomplete",
            preflight=preflight,
        )
    return _emit(
        "gcp migrate apply",
        "blocked",
        reason="cloud migration execution requires a real GCP run",
        preflight=preflight,
        migrations=migration_manifest(),
    )


def _gcp_cost_report(args: argparse.Namespace) -> int:
    output_dir = _resolve_repo_path(args.output)
    try:
        if args.input:
            report = load_cost_evidence(_resolve_repo_path(args.input))
        else:
            report = pending_cost_report()
        json_path, markdown_path = write_cost_report(output_dir, report)
    except (OSError, ValueError) as exc:
        return _emit("gcp cost report", "failed", error=str(exc))
    status = str(report.get("status", "UNKNOWN"))
    command_status = {
        "BLOCKED": "blocked",
        "PASS": "accepted",
        "RECORDED": "accepted",
    }.get(status, "failed")
    return _emit(
        "gcp cost report",
        command_status,
        evidence_status=status,
        cloud_execution=report.get("cloud_execution"),
        report_json=str(json_path),
        report_markdown=str(markdown_path),
    )


def _gcp_serving(args: argparse.Namespace) -> int:
    preflight = _gcp_preflight()
    sync_run_seq = getattr(args, "sync_run_seq", None)
    if sync_run_seq is not None and sync_run_seq < 1:
        return _emit(
            "gcp serving run",
            "failed",
            reason="sync_run_seq must be positive",
        )
    return _emit(
        "gcp serving run",
        "blocked",
        reason="cloud Airflow execution requires GCP credentials and a real run",
        dag_id="olist_gcp_serving",
        sync_run_seq=sync_run_seq,
        cloud_execution="PENDING_GCP_ACCESS",
        preflight=preflight,
    )


def _gcp_inventory(_: argparse.Namespace) -> int:
    return _emit(
        "gcp inventory",
        "blocked",
        reason="cloud inventory requires GCP credentials and a real project",
        cloud_execution="PENDING_GCP_ACCESS",
        preflight=_gcp_preflight(),
    )


def _gcp_destructive(args: argparse.Namespace) -> int:
    command = f"gcp {args.action}"
    scope = (
        "application GCP data, Iceberg checkpoints, BigQuery datasets, and "
        "Terraform-managed resources; the bootstrap state bucket is excluded"
        if args.action == "reset-data"
        else "the complete Terraform-managed GCP contour; the bootstrap state bucket is excluded"
    )
    if not args.force:
        return _emit(
            command,
            "blocked",
            reason=f"{command} requires --force",
            scope=scope,
        )
    return _emit(
        command,
        "blocked",
        reason="destructive cloud operation requires a real GCP run and operator confirmation",
        scope=scope,
        cloud_execution="PENDING_GCP_ACCESS",
        preflight=_gcp_preflight(),
    )


def _terraform(args: argparse.Namespace) -> int:
    if args.action == "apply" and not args.yes:
        return _emit(
            "gcp terraform apply",
            "blocked",
            reason="terraform apply requires --yes",
        )
    executable = shutil.which("terraform")
    workdir = ROOT / "infra" / "gcp" / "dev"
    if executable is None:
        return _emit("gcp terraform", "blocked", reason="terraform is not installed")
    if not workdir.is_dir():
        return _emit(
            "gcp terraform",
            "blocked",
            reason="infra/gcp/dev is delivered in WP3",
        )
    command = [executable, args.action]
    if args.action == "init":
        backend_configs = getattr(args, "backend_config", [])
        if backend_configs:
            command.extend(f"-backend-config={value}" for value in backend_configs)
        else:
            command.append("-backend=false")
        command.append("-input=false")
    elif args.action in {"plan", "apply", "output"}:
        preflight = _gcp_preflight()
        missing = preflight["missing"]
        if (
            isinstance(missing, list)
            and missing
            and not getattr(args, "allow_missing_auth", False)
        ):
            return _emit(
                "gcp terraform",
                "blocked",
                action=args.action,
                reason="GCP preflight is incomplete",
                **preflight,
            )
        command.append("-input=false")
    var_file = getattr(args, "var_file", None)
    if var_file:
        variable_file = Path(var_file)
        if not variable_file.is_absolute():
            variable_file = ROOT / variable_file
        if not variable_file.is_file():
            return _emit(
                "gcp terraform",
                "blocked",
                action=args.action,
                reason=f"variable file does not exist: {variable_file}",
            )
        command.append(f"-var-file={variable_file}")
    if args.action == "apply":
        command.append("-auto-approve")
    try:
        completed = subprocess.run(
            command,
            cwd=workdir,
            check=False,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _emit("gcp terraform", "failed", error=str(exc))
    output = (completed.stderr or completed.stdout or "").strip()
    return _emit(
        "gcp terraform",
        "ready" if completed.returncode == 0 else "failed",
        action=args.action,
        output=output[-4000:],
    )


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _parity_run(args: argparse.Namespace) -> int:
    output_dir = _resolve_repo_path(args.output)
    local_path = (
        _resolve_repo_path(args.local_evidence) if args.local_evidence else None
    )
    gcp_path = _resolve_repo_path(args.gcp_evidence) if args.gcp_evidence else None
    if bool(local_path) != bool(gcp_path):
        return _emit(
            "parity run",
            "failed",
            reason="local and gcp evidence must be supplied together",
        )
    try:
        report = (
            compare_evidence_files(local_path, gcp_path)
            if local_path is not None and gcp_path is not None
            else pending_report()
        )
        json_path, markdown_path = write_report(output_dir, report)
    except (OSError, ValueError) as exc:
        return _emit("parity run", "failed", error=str(exc))
    report_status = str(report["status"])
    status = {
        "PASS": "accepted",
        "FAIL": "failed",
        "BLOCKED": "blocked",
    }[report_status]
    return _emit(
        "parity run",
        status,
        parity_status=report_status,
        cloud_execution=report.get("cloud_execution"),
        report_json=str(json_path),
        report_markdown=str(markdown_path),
        difference_count=report.get("difference_count", 0),
    )


def _parity_report(args: argparse.Namespace) -> int:
    input_path = _resolve_repo_path(args.input)
    try:
        report = read_report(input_path)
    except (OSError, ValueError) as exc:
        return _emit("parity report", "failed", error=str(exc))
    report_status = str(report["status"])
    status = {
        "PASS": "accepted",
        "FAIL": "failed",
        "BLOCKED": "blocked",
    }[report_status]
    return _emit(
        "parity report",
        status,
        parity_status=report_status,
        cloud_execution=report.get("cloud_execution"),
        report_json=str(input_path),
        difference_count=report.get("difference_count", 0),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="group", required=True)

    doctor = commands.add_parser("doctor")
    doctor.add_argument("legacy_args", nargs=argparse.REMAINDER)
    doctor.set_defaults(func=lambda args: _legacy(["doctor", *args.legacy_args]))

    local = commands.add_parser("local")
    local_commands = local.add_subparsers(dest="action", required=True)
    local_up = local_commands.add_parser("up")
    local_up.add_argument("--build", action="store_true")
    local_up.add_argument("--timeout", type=float, default=1200.0)
    local_up.set_defaults(
        func=lambda args: _legacy(
            ["up", *(["--build"] if args.build else []), "--timeout", str(args.timeout)]
        )
    )
    local_down = local_commands.add_parser("down")
    local_down.set_defaults(func=lambda _: _legacy(["down"]))
    local_reset = local_commands.add_parser("reset-data")
    local_reset.add_argument("--force", action="store_true")
    local_reset.set_defaults(
        func=lambda args: _legacy(["reset", "--yes"] if args.force else ["reset"])
    )
    local_streaming = local_commands.add_parser("streaming")
    local_streaming_commands = local_streaming.add_subparsers(
        dest="streaming_action", required=True
    )
    local_start = local_streaming_commands.add_parser("start")
    local_start.add_argument("--wait-ready", action="store_true")
    local_start.set_defaults(
        func=lambda args: _legacy(
            ["start-streaming", *(["--wait-ready"] if args.wait_ready else [])]
        )
    )
    local_stop = local_streaming_commands.add_parser("stop")
    local_stop.set_defaults(func=lambda _: _legacy(["stop-streaming"]))
    local_status = local_streaming_commands.add_parser("status")
    local_status.set_defaults(
        func=lambda _: _legacy(["status", "--require", "platform"])
    )
    local_serving = local_commands.add_parser("serving")
    local_serving.set_defaults(func=lambda _: _legacy(["sync-serving"]))

    gcp = commands.add_parser("gcp")
    gcp_commands = gcp.add_subparsers(dest="action", required=True)
    preflight = gcp_commands.add_parser("preflight")
    preflight.set_defaults(func=_gcp_preflight_command)
    gcp_up = gcp_commands.add_parser("up")
    gcp_up.add_argument("--build", action="store_true")
    gcp_up.add_argument("--allow-missing-auth", action="store_true")
    gcp_up.add_argument("--timeout", type=float, default=1200.0)
    gcp_up.set_defaults(func=_gcp_up)
    gcp_down = gcp_commands.add_parser("down")
    gcp_down.add_argument("--timeout", type=float, default=300.0)
    gcp_down.set_defaults(func=_gcp_down)
    gcp_streaming = gcp_commands.add_parser("streaming")
    gcp_streaming_commands = gcp_streaming.add_subparsers(dest="action", required=True)
    for action in ("start", "status", "stop"):
        stream_command = gcp_streaming_commands.add_parser(action)
        if action == "start":
            stream_command.add_argument("--build", action="store_true")
            stream_command.add_argument("--allow-missing-auth", action="store_true")
        stream_command.add_argument("--timeout", type=float, default=1200.0)
        stream_command.set_defaults(func=_gcp_streaming)
    migrate = gcp_commands.add_parser("migrate")
    migrate_commands = migrate.add_subparsers(dest="action", required=True)
    migrate_status = migrate_commands.add_parser("status")
    migrate_status.set_defaults(func=_gcp_migrate)
    migrate_render = migrate_commands.add_parser("render")
    migrate_render.add_argument("--project-id")
    migrate_render.add_argument("--catalog-id")
    migrate_render.add_argument(
        "--output", default="data/acceptance/gcp/rendered-migrations"
    )
    migrate_render.set_defaults(func=_gcp_migrate)
    migrate_apply = migrate_commands.add_parser("apply")
    migrate_apply.add_argument("--project-id")
    migrate_apply.add_argument("--catalog-id")
    migrate_apply.add_argument("--allow-missing-auth", action="store_true")
    migrate_apply.set_defaults(func=_gcp_migrate)
    cost = gcp_commands.add_parser("cost")
    cost_commands = cost.add_subparsers(dest="cost_action", required=True)
    cost_report = cost_commands.add_parser("report")
    cost_report.add_argument("--input")
    cost_report.add_argument("--output", default="data/acceptance/gcp/cost")
    cost_report.set_defaults(func=_gcp_cost_report)
    serving = gcp_commands.add_parser("serving")
    serving_run = serving.add_subparsers(dest="serving_action", required=True)
    serving_run_command = serving_run.add_parser("run")
    serving_run_command.add_argument("--sync-run-seq", type=int)
    serving_run_command.set_defaults(func=_gcp_serving)
    reset_data = gcp_commands.add_parser("reset-data")
    reset_data.add_argument("--force", action="store_true")
    reset_data.set_defaults(func=_gcp_destructive, action="reset-data")
    destroy = gcp_commands.add_parser("destroy")
    destroy.add_argument("--force", action="store_true")
    destroy.set_defaults(func=_gcp_destructive, action="destroy")
    inventory = gcp_commands.add_parser("inventory")
    inventory.set_defaults(func=_gcp_inventory)
    vertical_slice = gcp_commands.add_parser("vertical-slice")
    vertical_slice_commands = vertical_slice.add_subparsers(
        dest="action", required=True
    )
    vertical_slice_run = vertical_slice_commands.add_parser("run")
    vertical_slice_run.add_argument("--project-id")
    vertical_slice_run.add_argument("--catalog-id")
    vertical_slice_run.add_argument("--bridge-dataset", default=DEFAULT_BRIDGE_DATASET)
    vertical_slice_run.add_argument(
        "--output", default="data/acceptance/gcp/wp5-vertical-slice-plan.json"
    )
    vertical_slice_run.add_argument("--allow-missing-auth", action="store_true")
    vertical_slice_run.set_defaults(func=_gcp_vertical_slice)
    vertical_slice_report = vertical_slice_commands.add_parser("report")
    vertical_slice_report.add_argument(
        "--output", default="data/acceptance/gcp/wp5-vertical-slice-plan.json"
    )
    vertical_slice_report.set_defaults(func=_gcp_vertical_slice)
    terraform = gcp_commands.add_parser("terraform")
    terraform.add_argument(
        "action", choices=("init", "validate", "plan", "apply", "output")
    )
    terraform.add_argument("--yes", action="store_true")
    terraform.add_argument("--allow-missing-auth", action="store_true")
    terraform.add_argument("--backend-config", action="append", default=[])
    terraform.add_argument("--var-file")
    terraform.add_argument("--timeout", type=float, default=600.0)
    terraform.set_defaults(func=_terraform)

    parity = commands.add_parser("parity")
    parity_commands = parity.add_subparsers(dest="action", required=True)
    parity_run = parity_commands.add_parser("run")
    parity_run.add_argument("--local-evidence")
    parity_run.add_argument("--gcp-evidence")
    parity_run.add_argument("--output", default=str(DEFAULT_PARITY_OUTPUT_DIR))
    parity_run.set_defaults(func=_parity_run)
    parity_report = parity_commands.add_parser("report")
    parity_report.add_argument(
        "--input", default=str(DEFAULT_PARITY_OUTPUT_DIR / "parity.json")
    )
    parity_report.set_defaults(func=_parity_report)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return _emit("lab", "failed", error=str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
