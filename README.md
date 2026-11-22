# AxiomXmuseOtonomCyberbrutal

Axiom autonomous red-team harness for Muse — skills, router, and agent loop in one repo, ready to use.

> **Scope guard — read this first.** Use these skills only against targets you are authorized to test: your own lab, a CTF / hackathon sandbox, or a target with a written scope / bug-bounty program. Never use them against production systems, other people's infrastructure, or for spam / abuse. See `SECURITY.md` and `SCOPE.md`.

## What is inside

| Area | Location | Contents |
|---|---|---|
| Agent operating rules | `AGENTS.md` | How Axiom works in this repo |
| Hykingcr skills | `skills/Hykingcr/` | CLI + MCP skills: nmap, gobuster, hashcat, hydra, metasploit, netexec, nikto, responder, evil-winrm, certipy, chisel, ghidra, ida, re-tools, llm-redteam, killchain-engine, pentest-agents, pwn-suite, api-recon, binary-recon, geo-osint, browser-act, and more. Router in `skills/Hykingcr/scripts/router.py`, routing table in `skills/Hykingcr/config/routing.json`. |
| Web hacking extreme | `skills/020-web-hacking-extreme/` | 15 categories: 01-recon, 02-waf-bypass, 03-exploit, 04-client-side, 05-auth-oauth, 06-automation, 07-web-security, 08-cloud-web, 09-ai-llm-web, 10-adv-recon, 11-network-web, 12-red-team-web, 13-log-siem-web, 14-exploit-arsenal, 15-threat-intel, plus `pipeline/`. |
| HackinMode | `skills/HackinMode/` | Web-pwn mode entry point (`skill.md`). |
| Skill index | `SKILLS_INDEX.md` | All 300 `SKILL.md` files, with paths. |

Counts, verified 2026-11-22: **300 `SKILL.md` files, 301 `agent.py` scripts**, 1,376+ files in total, ~10 MB.

## Install

```bash
git clone https://github.com/AxiomXmuse/AxiomXmuseOtonomCyberbrutal.git
cd AxiomXmuseOtonomCyberbrutal
python3 --version   # 3.12+
# Install only the tools you need for the target, in your lab:
# nmap, gobuster, ffuf, nuclei, sqlmap, hydra, hashcat — see each skill's SKILL.md
```

No credentials are stored in this repo. No `.env` files are included. If a skill needs a token, export it in your own shell, never commit it.

## Use

1. Pick a target that is in scope — write it down first (host, IP range, or URL, plus who authorized it).
2. Pick a skill from `SKILLS_INDEX.md`, read its `SKILL.md` first.
3. Run the skill's script with the target as an argument, in the lab.
4. Save proof: command, output, and what changed. No proof = not done.

Example (recon only, authorized target):

```bash
python3 skills/Hykingcr/scripts/router.py "recon web target"
```

## Safety

- Secret scan is fail-closed: `gitleaks dir .` from the repo root must be clean before any push. Verified example tokens in skill docs are listed in `.gitleaksignore` with fingerprints — no real credential is ignored, and new secrets are still flagged.
- `__pycache__` and `*.pyc` are excluded (see `.gitignore`).
- Abuse tools (SMS / OTP bombers and similar) are **not** in this repo. Do not add them.

## Surprise inside

- `skills/Hykingcr/scripts/router.py` + `config/routing.json` — route a task in plain words to the right skill.
- `skills/020-web-hacking-extreme/pipeline/` — end-to-end web pipeline (recon → detection → WAF bypass → exploit → chain → report). Run it only in the lab, against an in-scope target.
- `SKILLS_INDEX.md` — one-line index of every skill, so Muse can find the right one without reading 300 files.

## License

MIT — see `LICENSE`.
