---
name: hykingcr-reverse-skill
description: "Universal reverse engineering router — 45 skill playbooks (R0–R45): APK, iOS, JS, .NET, IDA, Ghidra, radare2, firmware, malware, EDR bypass, patch-diff, pwn/ROP, LLM security."
---

# HYKINGCR — Reverse Skill Router (R0–R45)

Source: `repos/reverse-skill/skills/` (MIT license)

## Routing Contract

Run the master router first:
```bash
bash '${CLAUDE_SKILL_DIR}/scripts/master-route.sh' '<ask>'
```

The script delegates to `repos/reverse-skill/skills/scripts/master-route.sh` with `SKILL_ROOT` set.
Routes R0–R45 are defined in `hykingcr/config/routing.json`.

## Skill Index (R0–R45)

| ID | Module | Directory | Trigger |
|---|---|---|---|
| R0 | General reverse-engineering | `reverse-engineering/` | GDB, Frida, angr, Unicorn, Unity/IL2CPP, game reverse |
| R1 | APK reverse | `apk-reverse/` | Android APK, jadx, smali, Frida hook, repack |
| R2 | Mobile reverse | `mobile-reverse/` | iOS, IPA, objection, MobSF, SSL pinning bypass |
| R3 | JS/frontend reverse | `js-reverse/` | Webpack, encrypted param, frontend sign, CDP |
| R4 | DSL VM reverse | `reverse-engineering/dsl-vm-reverse/` | Custom VM, opcode VM, fireye |
| R5 | .NET reverse | `dotnet-reverse/` | dnSpyEx, de4dot, ConfuserEx, IL patch |
| R6 | IDA reverse | `ida-reverse/` | IDA Pro MCP, decompile, xrefs, .so/.elf |
| R7 | radare2 | `radare2/` | r2, rabin2, rasm2, radiff2 |
| R8 | Firmware pentest | `firmware-pentest/` | binwalk, EMBA, Firmadyne, QEMU, IoT |
| R9 | Malware analysis | `malware-analysis/` | YARA, CAPE, PE-sieve, ransomware, webshell |
| R10 | Attack chain | `attack-chain/` | Full pentest, lateral movement, domain controller |
| R11 | Pentest tools | `pentest-tools/` | Nmap, nuclei, sqlmap, ffuf, Burp, Metasploit |
| R12 | API security | `api-security/` | BOLA, BFLA, GraphQL, OAuth, REST API |
| R13 | Supply chain | `supply-chain-security/` | SBOM, Trivy, gitleaks, dependency scan |
| R14 | LLM/Agent security | `llm-security/` | Prompt injection, jailbreak, OWASP LLM |
| R15 | Binary diff | `binary-diff/` | bindiff, symbol migration, PDB |
| R16 | Patch-diff/N-day | `patch-diff-exploit/` | N-day, patch diff, Tuesday patches |
| R17 | Pwn chain | `pwn-chain/` | ROP, ret2libc, heap/stack overflow, pwntools |
| R18 | EDR bypass RE | `edr-bypass-re/` | EDR hooks, syscall, AMSI, ETW, Hell's Gate |
| R19 | Browser/desktop automation | `browser-automation/` | Playwright, OpenReverse, UI automation |
| R20 | Docs generator | `docs-generator/` | Writeup, pentest report, RE report |
| R21 | Protocol reverse | `protocol-reverse/` | Custom protocol, protobuf, gRPC, PCAP |
| R22 | Ghidra reverse | `ghidra-reverse/` | Ghidra MCP, analyzeHeadless, PyGhidra |
| R23 | Cloud/K8s | `cloud-k8s/` | K8s, container escape, IMDS, S3, IAM |
| R24 | Windows/AD | `windows-ad/` | BloodHound, Kerberoast, NTLM relay, impacket |
| R25 | Digital forensics | `digital-forensics/` | Volatility, memory dump, Autopsy, IR |
| R26 | Code audit/SAST | `code-audit/` | Semgrep, CodeQL, white-box, source review |
| R27 | Threat hunting | `threat-hunting/` | Sigma rules, blue team, detection engineering |
| R28 | OT/ICS | `ot-ics/` | SCADA, PLC, Modbus, DNP3, Purdue model |
| R29 | Wi-Fi/wireless | `wifi-wireless/` | aircrack, WPA handshake, PMKID |
| R30 | Browser extension | `browser-extension-reverse/` | CRX, XPI, MV3, Chrome extension |
| R31 | macOS/Mach-O | `macos-reverse/` | codesign, ObjC, Swift, XPC, LaunchAgent |
| R32 | Thick client | `thick-client/` | Electron, WinForms, WPF, desktop C/S |
| R33 | Go/Rust reverse | `go-rust-reverse/` | Stripped Go/Rust, pclntab, panic strings |
| R34 | Hardware/debug | `hardware-security/` | UART, JTAG, SWD, flashrom, chip extraction |
| R35 | Database security | `database-security/` | MySQL, Postgres, MongoDB, Redis, MSSQL |
| R36 | Email/phishing | `email-security/` | SPF, DKIM, DMARC, BEC, phishing analysis |
| R37 | Identity federation | `identity-federation/` | SAML, OIDC, OAuth2, SSO |
| R38 | RF/SDR | `radio-sdr/` | HackRF, RTL-SDR, GNU Radio, Bluetooth/BLE |
| R39 | Diagram generation | `diagram-generator/` | Mermaid, Graphviz, PlantUML, attack path |
| R40 | Case evidence review | `case-review/` | Evidence chain, traceability, fixity |
| R44 | Threat intel/OSINT | `threat-intelligence/` | IOC, CTI, open source intelligence |
| R45 | Binary Ninja | `binary-ninja-reverse/` | HLIL, MLIL, Binary Ninja MCP |

## Execution

```bash
# Route and execute
bash '${CLAUDE_SKILL_DIR}/scripts/master-route.sh' '<ask>'

# Read the routed skill directly
SKILL_ROOT=$OMP_REPOS_ROOT/reverse-skill/skills
read "$SKILL_ROOT/<routed-skill>/SKILL.md"
```
