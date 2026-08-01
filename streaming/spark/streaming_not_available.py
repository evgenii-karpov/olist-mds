"""Explicit Wave 2 guard for the not-yet-implemented streaming drivers."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            {
                "status": "not_available_until",
                "not_available_until": "J2",
                "phase": args.phase,
            },
            sort_keys=True,
        )
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
