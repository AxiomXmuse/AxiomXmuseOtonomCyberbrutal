#!/usr/bin/env python3
"""
HYKINGCR redteam_run.py — standalone LLM red-team runner using deepteam.

Usage:
  redteam_run.py --target-url https://llm-api/v1/chat \\
                 --vulns ShellInjection,SSRF,PIILeakage \\
                 --attacks PromptInjection,CrescendoJailbreaking \\
                 --output report.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from typing import Any


def check_deepteam() -> bool:
    return importlib.util.find_spec("deepteam") is not None


def build_vuln(name: str) -> Any:
    from deepteam import vulnerabilities as V  # type: ignore
    cls = getattr(V, name, None)
    if cls is None:
        print(f"ERROR: Unknown vulnerability class '{name}'", file=sys.stderr)
        print("Run with --list-vulns to see available classes.", file=sys.stderr)
        sys.exit(1)
    return cls()


def build_attack(name: str) -> Any:
    from deepteam.attacks import single_turn as ST, multi_turn as MT  # type: ignore
    cls = getattr(ST, name, None) or getattr(MT, name, None)
    if cls is None:
        print(f"ERROR: Unknown attack class '{name}'", file=sys.stderr)
        print("Run with --list-attacks to see available classes.", file=sys.stderr)
        sys.exit(1)
    return cls()


def list_vulns() -> None:
    if not check_deepteam():
        print("deepteam not installed. Run: pip install deepteam")
        return
    import deepteam.vulnerabilities as V  # type: ignore
    names = [n for n in dir(V) if not n.startswith("_") and n[0].isupper()]
    print("Available vulnerability classes:")
    for n in sorted(names):
        print(f"  {n}")


def list_attacks() -> None:
    if not check_deepteam():
        print("deepteam not installed. Run: pip install deepteam")
        return
    from deepteam.attacks import single_turn as ST, multi_turn as MT  # type: ignore
    st = [n for n in dir(ST) if not n.startswith("_") and n[0].isupper()]
    mt = [n for n in dir(MT) if not n.startswith("_") and n[0].isupper()]
    print("Single-turn attacks:")
    for n in sorted(st):
        print(f"  {n}")
    print("Multi-turn attacks:")
    for n in sorted(mt):
        print(f"  {n}")


def make_http_callback(url: str, method: str = "POST", field: str = "prompt"):
    """Returns a model_callback that POSTs to url and extracts response."""
    import urllib.request
    import urllib.parse

    def callback(prompt: str) -> str:
        payload = json.dumps({field: prompt}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                # Try common response field names
                for key in ("response", "content", "text", "output", "message", "choices"):
                    if key in data:
                        val = data[key]
                        if isinstance(val, list) and val:
                            val = val[0]
                        if isinstance(val, dict):
                            val = val.get("message", {}).get("content", str(val))
                        return str(val)
                return str(data)
        except Exception as e:
            return f"[HTTP ERROR: {e}]"

    return callback


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HYKINGCR LLM red-team runner — deepteam wrapper."
    )
    parser.add_argument("--target-url", metavar="URL",
                        help="LLM API endpoint (POST with JSON {prompt: <text>})")
    parser.add_argument("--vulns", metavar="CLASSES",
                        help="Comma-separated vulnerability class names (e.g. ShellInjection,SSRF)")
    parser.add_argument("--attacks", metavar="CLASSES",
                        help="Comma-separated attack class names (e.g. PromptInjection,CrescendoJailbreaking)")
    parser.add_argument("--output", default="report.json",
                        help="Output report path (default: report.json)")
    parser.add_argument("--request-field", default="prompt",
                        help="JSON field name for the prompt in HTTP requests (default: prompt)")
    parser.add_argument("--list-vulns", action="store_true",
                        help="List all available vulnerability classes and exit")
    parser.add_argument("--list-attacks", action="store_true",
                        help="List all available attack classes and exit")
    args = parser.parse_args()

    if args.list_vulns:
        list_vulns()
        return

    if args.list_attacks:
        list_attacks()
        return

    if not check_deepteam():
        print("deepteam is not installed.", file=sys.stderr)
        print("Install with: pip install deepteam", file=sys.stderr)
        sys.exit(1)

    if not args.target_url:
        parser.error("--target-url is required unless --list-vulns or --list-attacks is set.")

    from deepteam import red_team  # type: ignore

    vuln_names = [v.strip() for v in (args.vulns or "ShellInjection,PIILeakage,SSRF").split(",")]
    attack_names = [a.strip() for a in (args.attacks or "PromptInjection,Base64").split(",")]

    vulnerabilities = [build_vuln(n) for n in vuln_names]
    attacks = [build_attack(n) for n in attack_names]

    callback = make_http_callback(args.target_url, field=args.request_field)

    print(f"[redteam] Target: {args.target_url}")
    print(f"[redteam] Vulnerabilities: {', '.join(vuln_names)}")
    print(f"[redteam] Attacks: {', '.join(attack_names)}")
    print(f"[redteam] Output: {args.output}")
    print()

    risk = red_team(
        model_callback=callback,
        vulnerabilities=vulnerabilities,
        attacks=attacks,
    )

    report = {
        "target": args.target_url,
        "vulnerabilities_tested": vuln_names,
        "attacks_used": attack_names,
        "risk": str(risk),
    }

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"[redteam] Report written to {args.output}")
    print(f"[redteam] Risk score: {risk}")


if __name__ == "__main__":
    main()
