---
name: hykingcr-killchain-engine
description: "Kill-chain detection engine — analyzes findings for 8 cross-skill attack chain patterns (IDOR+data leak, XSS+CSRF, SSTI+RCE, credential endpoint, SSRF, OAuth redirect, race condition, custom). Outputs chain candidates with severity boost and next-step recommendations."
---

# HYKINGCR — Kill-Chain Engine

Source: `repos/CyberStrike/packages/cyberstrike/src/methodology/chain.ts` (pattern methodology; AGPL — patterns referenced only, no source copied)

## 8 Kill-Chain Patterns

| Pattern | Description | CWE Triggers |
|---|---|---|
| `credential_endpoint` | Exposed credential/auth endpoint enables account takeover | CWE-522, CWE-255, CWE-798 |
| `info_disclosure_ssrf` | Info disclosure leaks internal IPs → SSRF pivot | CWE-200, CWE-918 |
| `redirect_oauth` | Open redirect + OAuth → token theft via redirect_uri | CWE-601, OAuth redirect_uri |
| `idor_data_leak` | IDOR + data exposure = full account/PII compromise | CWE-639, CWE-200 |
| `xss_csrf` | XSS + CSRF = persistent account takeover or state mutation | CWE-79, CWE-352 |
| `ssti_rce` | SSTI leads directly to RCE via template engine escape | CWE-94, CWE-1336 |
| `race_condition_business` | Race condition in payment/transfer/invite enables business logic bypass | CWE-362, business logic |
| `custom` | User-defined chain: any two findings with shared asset and compound impact | — |

## Detection Logic

A chain fires when ALL required CWE/OWASP patterns match across the input findings set, on the **same asset or related subdomain**.

Severity boost: combined severity = max(finding_a.severity, finding_b.severity) + one tier, capped at `critical`.

## Run

```bash
# From findings JSON
python3 '${CLAUDE_SKILL_DIR}/scripts/killchain.py' --findings findings.json [--json] [--verbose]

# Pipe from another tool
cat burp_findings.json | python3 '${CLAUDE_SKILL_DIR}/scripts/killchain.py' --findings /dev/stdin --json
```

## Input Format

`findings.json` — array of finding objects:
```json
[
  {"name": "IDOR on /api/user/{id}", "cwe_ids": ["CWE-639"], "owasp_id": "API1:2023"},
  {"name": "Sensitive data exposure in response", "cwe_ids": ["CWE-200"], "owasp_id": "API3:2023"},
  {"name": "Open redirect on /auth/callback", "cwe_ids": ["CWE-601"], "owasp_id": "A01:2021"}
]
```

## Output Format

```json
{
  "chains": [
    {
      "pattern": "idor_data_leak",
      "severity_boost": 2,
      "combined_severity": "critical",
      "findings": ["IDOR on /api/user/{id}", "Sensitive data exposure in response"],
      "next_steps": ["Test data exfiltration scope", "Check for PII in response", "Verify auth bypass"]
    }
  ]
}
```

## Agent Procedure (Manual)

Given a set of findings, apply kill-chain detection mentally:

1. Group findings by asset (same domain or subdomain match)
2. For each pair of findings on the same asset, check against 8 patterns above
3. Pattern match → escalate combined severity + one tier
4. List next_steps: what finding would complete or weaponize this chain
5. Prioritize chains by combined_severity (critical > high > medium)

## `Skill.Info` Schema Fields for Chaining

When documenting findings for chain detection, include:
- `chains_with: []` — IDs of skills/findings that this chains with
- `prerequisites: []` — required findings before this chain activates
- `severity_boost` — severity escalation string when chain fires
- `cwe_ids: []` — CWE identifiers for pattern matching
