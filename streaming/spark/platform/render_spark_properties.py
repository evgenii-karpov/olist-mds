"""Atomically render the secret Spark properties file with mode 0600."""

from __future__ import annotations

import argparse
import os
import secrets
import stat
from pathlib import Path

from .config import SparkPlatformConfig


def _property_line(name: str, value: str) -> str:
    if not name or any(character in name for character in " \t\r\n=:"):
        raise ValueError(f"invalid Spark property name: {name!r}")
    if any(character in value for character in ("\r", "\n", "\x00")):
        raise ValueError(f"Spark property {name} contains a forbidden control byte")
    return f"{name} {value}\n"


def render_properties(
    output: Path, config: SparkPlatformConfig, mode: str = "streaming"
) -> None:
    """Write properties without ever placing credentials in process arguments."""

    output = output.absolute()
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if output.exists() and (output.is_symlink() or not output.is_file()):
        raise ValueError(f"refusing non-regular output path: {output}")

    contents = "".join(
        _property_line(name, value)
        for name, value in config.spark_properties(mode=mode).items()
    )
    temporary = output.with_name(f".{output.name}.{secrets.token_hex(8)}.tmp")
    previous_umask = os.umask(0o077)
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, output)
            os.chmod(output, 0o600)
        finally:
            if temporary.exists():
                temporary.unlink()
    finally:
        os.umask(previous_umask)

    # Windows cannot represent POSIX owner-only modes; the production image is Linux.
    if os.name != "nt":
        actual_mode = stat.S_IMODE(output.stat().st_mode)
        if actual_mode != 0o600:
            raise PermissionError(
                f"Spark properties mode is {actual_mode:o}, expected 600"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render the Olist Spark/Polaris properties file from *_FILE secrets"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/run/spark/conf/olist-lakehouse.properties"),
    )
    parser.add_argument(
        "--mode",
        choices=["streaming", "maintenance"],
        default="streaming",
    )
    arguments = parser.parse_args()
    render_properties(
        arguments.output, SparkPlatformConfig.from_environment(), mode=arguments.mode
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
