#!/usr/bin/env python3
"""
HYKINGCR api-recon wrapper — invokes ARTEX api-recon methodology.

Usage:
  api-recon.py --target https://example.com [--mode depth|coverage|both] [--outdir OUTDIR]
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

ARTEX_ROOT = OMP_REPOS_ROOT / "ARTEX" / "skills" / "api-recon"


def check_artex() -> bool:
    return ARTEX_ROOT.exists()


def run_static(target: str, outdir: Path) -> None:
    harvest = SCRIPTS / "harvest_static.py"
    if not harvest.exists():
        print(f"[api-recon] harvest_static.py not found at {harvest}")
        print("[api-recon] Run Phase 1 manually per ARTEX methodology.")
        return
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(harvest), "--target", target, "--outdir", str(outdir)],
        check=False,
    )


def run_runtime(target: str, outdir: Path, mode: str) -> None:
    runtime = SCRIPTS / "runtime_harvest.js"
    preload = SCRIPTS / "preload.js"

    if mode in ("depth", "both"):
        if runtime.exists():
            subprocess.run(
                ["node", str(runtime), "--target", target, "--outdir", str(outdir)],
                check=False,
            )
        else:
            print(f"[api-recon] runtime_harvest.js not found — run manually.")

    if mode in ("coverage", "both"):
        if preload.exists():
            subprocess.run(
                ["node", str(preload), "--target", target, "--outdir", str(outdir)],
                check=False,
            )
        else:
            print(f"[api-recon] preload.js not found — run manually.")


def merge_output(outdir: Path) -> None:
    merge = SCRIPTS / "merge_params.py"
    out = outdir / "params_merged.json"
    if merge.exists():
        subprocess.run(
            [sys.executable, str(merge), "--outdir", str(outdir), "--out", str(out)],
            check=False,
        )
    else:
        print(f"[api-recon] merge_params.py not found — run Phase 5 manually.")

    surface = outdir / "api_surface.json"
    if surface.exists():
        data = json.loads(surface.read_text())
        endpoint_count = len(data) if isinstance(data, list) else "?"
        print(f"[api-recon] Surface: {endpoint_count} endpoints → {surface}")


def main() -> None:
    parser = argparse.ArgumentParser(description="HYKINGCR API recon — ARTEX methodology wrapper")
    parser.add_argument("--target", required=True, help="Target URL (e.g. https://app.example.com)")
    parser.add_argument("--mode", choices=["depth", "coverage", "both"], default="depth",
                        help="Runtime harvest mode (default: depth)")
    parser.add_argument("--outdir", default="./api-recon-out",
                        help="Output directory (default: ./api-recon-out)")
    parser.add_argument("--static-only", action="store_true", help="Run Phase 1 static harvest only")
    args = parser.parse_args()

    outdir = Path(args.outdir)

    if not check_artex():
        print(f"ERROR: ARTEX skill not found at {ARTEX_ROOT}", file=sys.stderr)
        print("Clone: https://github.com/morluto/ARTEX", file=sys.stderr)
        sys.exit(1)

    print(f"[api-recon] Target: {args.target}")
    print(f"[api-recon] Mode: {'static-only' if args.static_only else args.mode}")
    print(f"[api-recon] Output: {outdir}")
    print()

    print("[api-recon] Phase 1 — Static harvest...")
    run_static(args.target, outdir)

    if not args.static_only:
        print(f"[api-recon] Phase 2/3 — Runtime ({args.mode})...")
        run_runtime(args.target, outdir, args.mode)
        print("[api-recon] Phase 5 — Merging output...")
        merge_output(outdir)

    print("[api-recon] Done. Read ARTEX SKILL.md for manual phase guidance.")


if __name__ == "__main__":
    main()
