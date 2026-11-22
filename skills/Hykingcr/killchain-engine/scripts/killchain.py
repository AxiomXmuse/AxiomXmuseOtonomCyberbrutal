#!/usr/bin/env python3
"""
HYKINGCR killchain.py — detects kill-chain patterns across a set of findings.

Usage:
  killchain.py --findings findings.json [--json] [--verbose]

Input JSON: [{"name": str, "cwe_ids": [str], "owasp_id": str, "asset": str (optional)}]
Output: {"chains": [{"pattern": str, "severity_boost": int, "combined_severity": str,
                      "findings": [str], "next_steps": [str]}]}
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

# ─── Chain Pattern Definitions ────────────────────────────────────────────────
# Each pattern: list of (cwe_regex, owasp_regex) tuples.
# A chain fires when at least one tuple matches finding_A and at least one different
# tuple matches finding_B (or same tuple matches two different findings with different names).

CHAIN_PATTERNS: dict[str, dict[str, Any]] = {
    "credential_endpoint": {
        "description": "Exposed credential/auth endpoint enables account takeover",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-52[2-9]|CWE-25[5-9]|CWE-798|CWE-307|CWE-306", "owasp": r"A02|A07|API[23]"},
            {"cwe": r"CWE-2[0-9][0-9]", "owasp": r"A01|A05|API1"},
        ],
        "next_steps": [
            "Test credential stuffing / password spray",
            "Verify MFA bypass",
            "Check session fixation after login",
            "Test for default credentials",
        ],
    },
    "info_disclosure_ssrf": {
        "description": "Info disclosure leaks internal IPs, enables SSRF pivot",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-200|CWE-209|CWE-213", "owasp": r"A01|A05|API3"},
            {"cwe": r"CWE-918", "owasp": r"A10|API7"},
        ],
        "next_steps": [
            "Use disclosed internal IP for SSRF pivot",
            "Test IMDS (169.254.169.254) via SSRF",
            "Enumerate internal services via SSRF",
            "Check for cloud metadata leakage",
        ],
    },
    "redirect_oauth": {
        "description": "Open redirect + OAuth → token theft via redirect_uri hijack",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-601", "owasp": r"A01|A03"},
            {"cwe": r"CWE-287|CWE-346", "owasp": r"A07|OAuth|API[45]"},
        ],
        "next_steps": [
            "Craft redirect_uri pointing to attacker-controlled host",
            "Test OAuth state parameter bypass",
            "Check token leakage in Referer header",
            "Test PKCE downgrade",
        ],
    },
    "idor_data_leak": {
        "description": "IDOR + data exposure = full account/PII compromise",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-639|CWE-284|CWE-285", "owasp": r"A01|API1"},
            {"cwe": r"CWE-200|CWE-359|CWE-312", "owasp": r"A02|A05|API3"},
        ],
        "next_steps": [
            "Test sequential/enumerable ID patterns",
            "Verify PII scope of exposed data",
            "Check cross-user data isolation",
            "Test horizontal privilege escalation",
        ],
    },
    "xss_csrf": {
        "description": "XSS + CSRF = persistent account takeover or state mutation",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-79|CWE-80|CWE-83", "owasp": r"A03"},
            {"cwe": r"CWE-352", "owasp": r"A01|A05"},
        ],
        "next_steps": [
            "Chain XSS to steal CSRF token → forge state-changing request",
            "Test stored XSS for persistent session hijack",
            "Check SameSite cookie attribute",
            "Verify CORS policy alignment with CSRF protection",
        ],
    },
    "ssti_rce": {
        "description": "SSTI leads to RCE via template engine escape",
        "severity_boost": 3,
        "rules": [
            {"cwe": r"CWE-94|CWE-1336|CWE-116", "owasp": r"A03|A09"},
            {"cwe": r"CWE-78|CWE-77|CWE-74", "owasp": r"A03"},
        ],
        "next_steps": [
            "Identify template engine (Jinja2, Twig, Freemarker, Pebble, Velocity)",
            "Test {{7*7}} / ${7*7} / #{7*7} payloads",
            "Escalate to OS command via __class__.__mro__ chain (Python)",
            "Attempt escape for full RCE",
        ],
    },
    "race_condition_business": {
        "description": "Race condition in payment/transfer/invite enables business logic bypass",
        "severity_boost": 2,
        "rules": [
            {"cwe": r"CWE-362|CWE-366|CWE-367", "owasp": r"A04|API4"},
            {"cwe": r"CWE-840|CWE-841", "owasp": r"A04|API8"},
        ],
        "next_steps": [
            "Test concurrent requests with Turbo Intruder / last-byte sync",
            "Check database transaction isolation level",
            "Verify idempotency token enforcement",
            "Test duplicate payment / invite / coupon use",
        ],
    },
    "custom": {
        "description": "User-defined chain: any two findings on same asset with compound impact",
        "severity_boost": 1,
        "rules": [
            {"cwe": r"CWE-\d+", "owasp": r".+"},
        ],
        "next_steps": [
            "Document compound impact across both findings",
            "Verify asset overlap (same domain/subdomain)",
            "Estimate combined CVSS score",
        ],
    },
}

SEVERITY_ORDER = ["info", "low", "medium", "high", "critical"]


def max_severity(a: str, b: str) -> str:
    ia = SEVERITY_ORDER.index(a) if a in SEVERITY_ORDER else 0
    ib = SEVERITY_ORDER.index(b) if b in SEVERITY_ORDER else 0
    return SEVERITY_ORDER[max(ia, ib)]


def boost_severity(sev: str, boost: int) -> str:
    idx = SEVERITY_ORDER.index(sev) if sev in SEVERITY_ORDER else 0
    return SEVERITY_ORDER[min(idx + boost, len(SEVERITY_ORDER) - 1)]


def rule_matches(finding: dict, rule: dict) -> bool:
    cwe_list = finding.get("cwe_ids", [])
    owasp = finding.get("owasp_id", "")
    cwe_match = any(re.search(rule["cwe"], c, re.IGNORECASE) for c in cwe_list)
    owasp_match = bool(re.search(rule["owasp"], owasp, re.IGNORECASE)) if owasp else False
    return cwe_match or owasp_match


def detect_chains(findings: list[dict], verbose: bool = False) -> list[dict]:
    chains = []
    seen: set[str] = set()

    for pattern_name, pattern in CHAIN_PATTERNS.items():
        rules = pattern["rules"]
        boost = pattern["severity_boost"]

        if pattern_name == "custom":
            continue  # custom handled separately at end

        # Find pairs of findings that satisfy the two rule slots
        for i, fa in enumerate(findings):
            for j, fb in enumerate(findings):
                if i >= j:
                    continue
                key = f"{pattern_name}:{i}:{j}"
                if key in seen:
                    continue

                # Check if fa matches rule[0] and fb matches rule[1], or vice versa
                fa_r0 = rule_matches(fa, rules[0]) if len(rules) > 0 else False
                fb_r1 = rule_matches(fb, rules[1]) if len(rules) > 1 else False
                fa_r1 = rule_matches(fa, rules[1]) if len(rules) > 1 else False
                fb_r0 = rule_matches(fb, rules[0]) if len(rules) > 0 else False

                matched = (fa_r0 and fb_r1) or (fa_r1 and fb_r0)
                if not matched:
                    continue

                seen.add(key)
                sev_a = fa.get("severity", "medium")
                sev_b = fb.get("severity", "medium")
                base = max_severity(sev_a, sev_b)
                combined = boost_severity(base, boost)

                chains.append({
                    "pattern": pattern_name,
                    "description": pattern["description"],
                    "severity_boost": boost,
                    "combined_severity": combined,
                    "findings": [fa.get("name", f"Finding {i}"), fb.get("name", f"Finding {j}")],
                    "next_steps": pattern["next_steps"],
                })

                if verbose:
                    print(f"  [+] Chain detected: {pattern_name}", file=sys.stderr)
                    print(f"      {fa.get('name')} ← → {fb.get('name')}", file=sys.stderr)
                    print(f"      Combined severity: {combined} (boost +{boost})", file=sys.stderr)

    # Sort by combined severity descending
    order = {s: i for i, s in enumerate(reversed(SEVERITY_ORDER))}
    chains.sort(key=lambda c: order.get(c["combined_severity"], 99))
    return chains


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HYKINGCR kill-chain detector — identifies attack chain patterns across findings."
    )
    parser.add_argument("--findings", required=True,
                        help="Path to findings JSON (or /dev/stdin)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output machine-readable JSON")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detection details to stderr")
    args = parser.parse_args()

    try:
        with open(args.findings, "r", encoding="utf-8") as fh:
            findings = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR reading findings: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(findings, list):
        print("ERROR: findings.json must be a JSON array", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"[killchain] Analyzing {len(findings)} findings for chain patterns...", file=sys.stderr)

    chains = detect_chains(findings, verbose=args.verbose)

    result = {"chains": chains, "total": len(chains)}

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        if not chains:
            print("No kill-chain patterns detected across provided findings.")
        else:
            print(f"Kill-Chain Detection Results ({len(chains)} chain(s) found)")
            print("=" * 60)
            for chain in chains:
                print(f"\nPattern:  {chain['pattern']}")
                print(f"Severity: {chain['combined_severity'].upper()} (+{chain['severity_boost']} boost)")
                print(f"Findings: {' <-> '.join(chain['findings'])}")
                print(f"Next steps:")
                for step in chain["next_steps"]:
                    print(f"  • {step}")


if __name__ == "__main__":
    main()
