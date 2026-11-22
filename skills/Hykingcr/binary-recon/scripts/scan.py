#!/usr/bin/env python3
"""
HYKINGCR binary-recon scan.py — thin wrapper around universal-modder um/scan.py.

Usage:
  scan.py --target /path/to/game/ [--json] [--kb-search <query>]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "config"))
from paths import OMP_REPOS_ROOT  # noqa: E402

UM_ROOT = OMP_REPOS_ROOT / "universal-modder"
UM_CLI = UM_ROOT / "um" / "cli.py"


def check_um() -> bool:
    return UM_CLI.exists()


def run_scan(target: str, as_json: bool = False) -> None:
    env = os.environ.copy()
    env["UM_ROOT"] = str(UM_ROOT)

    cmd = [sys.executable, str(UM_CLI), "scan", target]
    if as_json:
        cmd.append("--json")

    result = subprocess.run(cmd, env=env, capture_output=False)
    sys.exit(result.returncode)


def run_kb_search(query: str) -> None:
    env = os.environ.copy()
    env["UM_ROOT"] = str(UM_ROOT)

    cmd = [sys.executable, str(UM_CLI), "kb", "search", query]
    result = subprocess.run(cmd, env=env, capture_output=False)
    sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HYKINGCR binary recon — universal-modder scan wrapper."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", metavar="PATH",
                       help="Path to binary, game executable, or game directory")
    group.add_argument("--kb-search", metavar="QUERY",
                       help="Search universal-modder knowledge base")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output machine-readable JSON")
    args = parser.parse_args()

    if not check_um():
        print(f"ERROR: universal-modder not found at {UM_ROOT}", file=sys.stderr)
        print("Clone: https://github.com/morluto/universal-modder", file=sys.stderr)
        sys.exit(1)

    if args.kb_search:
        run_kb_search(args.kb_search)
    else:
        print(f"[binary-recon] Scanning: {args.target}")
        print(f"[binary-recon] UM_ROOT: {UM_ROOT}")
        print()
        run_scan(args.target, args.as_json)


if __name__ == "__main__":
    main()
