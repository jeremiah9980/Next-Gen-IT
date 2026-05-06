#!/usr/bin/env python3
"""Generate the Central-Texas AI target list.

Usage:
    python scripts/generate_targets.py [output_dir] [--primary N] [--secondary N] [--no-ai]

Defaults to writing JSON into ./data/targets/. Set ANTHROPIC_API_KEY or
OPENAI_API_KEY to use the AI path; otherwise the curated seed list is used.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.target_generator import generate_target_list, save_target_list  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Central Texas target list")
    parser.add_argument("output_dir", nargs="?", default="data/targets",
                        help="Directory to write the JSON file into")
    parser.add_argument("--primary", type=int, default=20,
                        help="Number of primary (real estate) targets")
    parser.add_argument("--secondary", type=int, default=15,
                        help="Number of secondary (title company) targets")
    parser.add_argument("--no-ai", action="store_true",
                        help="Skip AI providers and use the curated seed list only")
    parser.add_argument("--stdout", action="store_true",
                        help="Print JSON to stdout instead of writing a file")
    args = parser.parse_args()

    target_list = generate_target_list(
        primary_count=args.primary,
        secondary_count=args.secondary,
        use_ai=not args.no_ai,
    )

    if args.stdout:
        print(json.dumps(target_list.to_dict(), indent=2))
        return 0

    path = save_target_list(target_list, args.output_dir)
    summary = (
        f"Wrote {len(target_list.primary_targets)} primary + "
        f"{len(target_list.secondary_targets)} secondary targets "
        f"({target_list.source}) to {path}"
    )
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
