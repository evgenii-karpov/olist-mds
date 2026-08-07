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
from scripts.orchestration.compose_profiles import (
    LakehouseTarget,
    compose_profiles,
    validate_profile_selection,
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
        os.environ.get("GCP_PROJECT_ID", "").strip()
        or os.environ.get("TF_VAR_" + "project_id", "").strip()
    )
    region = (
        os.environ.get("GCP_REGION", "").strip()
        or os.environ.get("TF_VAR_" + "region", "").strip()
    )
    adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    adc_available = bool(adc_path) and Path(adc_path).is_file()
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
    return _emit(
        "gcp streaming start",
        "blocked",
        reason="GCP streaming drivers are delivered in WP4; no cloud stream was started",
        profiles=list(profiles),
        preflight=preflight,
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
    parity.add_argument("action", choices=("run", "report"))
    parity.set_defaults(
        func=lambda args: _emit(
            f"parity {args.action}",
            "blocked",
            reason="parity implementation is added in a later work package",
        )
    )
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
