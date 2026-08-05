"""Explicit guard for unsupported streaming driver commands."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            {
                "status": "not_available_until",
                "not_available_until": "streaming-runtime",
                "scope": args.scope,
            },
            sort_keys=True,
        )
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
