"""Thin command-line presentation layer for the deterministic simulator."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.simulation.database import (
    DatabaseSettings,
    SimulatorRepository,
    connect,
)
from scripts.simulation.domain import SimulationConfig
from scripts.simulation.engine import RunEngine, deterministic_run_id
from scripts.simulation.seeding import seed_archive

DEFAULT_LOGICAL_START = "2020-01-01T00:00:00"


def emit(event: str, **fields: object) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True, default=str))


def add_database_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--host", default=os.environ.get("OLTP_POSTGRES_HOST", "localhost")
    )
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("OLTP_POSTGRES_PORT", "5433"))
    )
    parser.add_argument(
        "--database", default=os.environ.get("OLTP_POSTGRES_DB", "olist_oltp")
    )
    parser.add_argument(
        "--user", default=os.environ.get("OLTP_POSTGRES_USER", "olist_simulator")
    )
    parser.add_argument("--password", default=os.environ.get("OLTP_POSTGRES_PASSWORD"))
    parser.add_argument(
        "--password-file", default=os.environ.get("OLTP_POSTGRES_PASSWORD_FILE")
    )


def add_run_configuration(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--start-time", default=DEFAULT_LOGICAL_START)
    parser.add_argument("--rate", type=float, default=5.0)
    limit = parser.add_mutually_exclusive_group()
    limit.add_argument("--event-limit", type=int)
    limit.add_argument("--duration-seconds", type=float)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    seed = commands.add_parser("seed", help="Idempotently seed Olist source data")
    add_database_arguments(seed)
    seed.add_argument("--archive", required=True)
    seed.add_argument("--seed", type=int, required=True)
    seed.add_argument("--run-id")
    seed.add_argument("--start-time", default=DEFAULT_LOGICAL_START)

    run = commands.add_parser("run", help="Generate finite or continuous lifecycles")
    add_database_arguments(run)
    add_run_configuration(run)
    run.add_argument("--cancel-probability", type=float, default=0.08)
    run.add_argument("--unavailable-probability", type=float, default=0.02)
    run.add_argument("--review-probability", type=float, default=0.35)
    run.add_argument("--correction-probability", type=float, default=0.05)
    run.add_argument("--hard-delete-probability", type=float, default=0.01)
    run.add_argument("--no-pacing", action="store_true", help=argparse.SUPPRESS)

    replay = commands.add_parser("replay", help="Replay inferred seeded lifecycles")
    add_database_arguments(replay)
    add_run_configuration(replay)
    replay.add_argument("--speed-multiplier", type=float, default=60.0)

    status = commands.add_parser("status", help="Report persisted simulator state")
    add_database_arguments(status)
    status.add_argument("--run-id")

    stop = commands.add_parser("stop", help="Request a transaction-boundary stop")
    add_database_arguments(stop)
    stop.add_argument("--run-id", required=True)
    return root


def settings_from_args(args: argparse.Namespace) -> DatabaseSettings:
    return DatabaseSettings.with_password_file(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
        password_file=args.password_file,
    )


def logical_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(UTC).replace(tzinfo=None)
    return parsed


def event_limit(args: argparse.Namespace) -> int | None:
    if args.event_limit is not None:
        return args.event_limit
    if args.duration_seconds is not None:
        calculated = int(args.duration_seconds * args.rate)
        if calculated < 1:
            raise ValueError("duration and rate must produce at least one lifecycle")
        return calculated
    return None


def simulation_config(args: argparse.Namespace) -> SimulationConfig:
    kwargs: dict[str, Any] = {
        "random_seed": args.seed,
        "start_time": logical_time(args.start_time),
        "target_rate": args.rate,
    }
    for name in (
        "cancel_probability",
        "unavailable_probability",
        "review_probability",
        "correction_probability",
        "hard_delete_probability",
    ):
        if hasattr(args, name):
            kwargs[name] = getattr(args, name)
    return SimulationConfig(**kwargs)


def execute(args: argparse.Namespace) -> int:
    connection = connect(settings_from_args(args))
    repository = SimulatorRepository(connection)
    try:
        if args.command == "seed":
            started_at = logical_time(args.start_time)
            run_id = args.run_id or deterministic_run_id("seed", args.seed, started_at)
            counts = seed_archive(
                repository,
                Path(args.archive),
                random_seed=args.seed,
                run_id=run_id,
                logical_time=started_at,
            )
            emit("seed_completed", run_id=run_id, row_counts=counts)
            return 0
        if args.command == "run":
            config = simulation_config(args)
            run_id = args.run_id or deterministic_run_id(
                "run", args.seed, config.start_time
            )
            completed = RunEngine(repository).run(
                run_id,
                config,
                event_limit=event_limit(args),
                pace=not args.no_pacing,
            )
            emit("run_completed", run_id=run_id, lifecycles=completed)
            return 0
        if args.command == "replay":
            config = simulation_config(args)
            run_id = args.run_id or deterministic_run_id(
                "replay", args.seed, config.start_time
            )
            completed = RunEngine(repository).replay(
                run_id,
                config,
                event_limit=event_limit(args),
                speed_multiplier=args.speed_multiplier,
            )
            emit("replay_completed", run_id=run_id, lifecycles=completed)
            return 0
        if args.command == "status":
            value = repository.status(args.run_id)
            emit(
                "status", **(value or {"run_state": "not_found", "run_id": args.run_id})
            )
            return 0 if value else 1
        if args.command == "stop":
            requested = repository.request_stop(
                args.run_id, datetime.now(UTC).replace(tzinfo=None)
            )
            emit("stop_requested", run_id=args.run_id, accepted=requested)
            return 0 if requested else 1
        raise ValueError(f"Unsupported command: {args.command}")
    finally:
        connection.close()


def main() -> int:
    args = parser().parse_args()
    try:
        return execute(args)
    except Exception as exc:
        emit(
            "command_failed",
            command=args.command,
            error_type=type(exc).__name__,
            message=str(exc),
        )
        return 1
