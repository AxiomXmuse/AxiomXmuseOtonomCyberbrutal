---
name: hykingcr

---

# HYKINGCR — Маршрутизатор Технической Безопасности

**Весь арсенал тестирования безопасности живёт здесь. Один навык обнаружен — полный доступ разблокирован.**

```
skills/Hykingcr/
├── SKILL.md                    ← you are here (master router, alwaysApply)
├── scripts/router.py           ← CLI dispatcher
├── config/routing.json         ← all routes R0–R45 + H01–H14 (single source of truth)
├── rules/                      ← OpenCodeHighEnd offensive addendum
├── 9router/                    ← existing 9router skill (untouched)
├── pwn-suite/                  ← Axiom web-pwn 303 skills · 15 categories (jail/skills/020-web-hacking-extreme)
├── reverse-skill/              ← RE router (45 playbooks, R0–R45)
├── api-recon/                  ← API surface discovery (ARTEX methodology)
├── pentest-agents/             ← 26 Decepticon autonomous pentest agents
├── killchain-engine/           ← 8 cross-skill kill-chain detection patterns
├── llm-redteam/                ← LLM vulnerability testing (40 vuln classes)
├── ida-mcp/                    ← IDA Pro MCP bridge (75 tools)
├── ghidra-mcp/                 ← Ghidra MCP bridge (25 tools)
├── jshook-mcp/                 ← jshook MCP (735 tools, 36 domains)
├── re-tools-mcp/               ← REA MCP (80+ RE tools)
├── rea-prompts/                ← 26 reverse-engineering prompt packs
├── geo-osint/                  ← Photo geolocation OSINT
├── binary-recon/               ← Binary/game fingerprinting
├── ctf-toolindex/              ← CTF tool reference index
├── malware-toolindex/          ← Malware analysis tool reference
├── browser-act/                ← Browser automation CLI for stealth/multi-account
└── chrome-devtools-axi/        ← Chromium DevTools CDP diagnostics interface
```




## Таблица маршрутизации: Ключевые слова → Под-навык

| Ключевые слова | Под-навык | Режим |
|---|---|---|
| decepticon, red team agents, create recon agent, create exploit agent, langgraph pentest, neo4j skill, skillogy, workflow pentest | `pentest-agents/SKILL.md` | чтение |
| kill chain, killchain, chain detect, idor chain, ssrf chain, xss csrf chain, severity boost, owasp killchain, methodology chain | `killchain-engine/SKILL.md` | чтение → запуск |
| api recon, swagger harvest, spa harvest, webpack extract, vite map, xhr stub, openapi discover, artex, api surface | `api-recon/SKILL.md` | чтение → запуск |
| pwn, web pwn, hackingmode, aggressive pentest, full pipeline, axiom pipeline, wstg, post exploit, red team web, c2 sliver, havoc, cloud aws, gcp k8s | `pwn-suite/SKILL.md` | запуск |
| ida pro, ida mcp, idalib, idalib-mcp, idapython, decompile ida, xref ida, signature generation, triage profile, debug ida | `ida-mcp/SKILL.md` | чтение |
| ghidra, ghidra mcp, decompile ghidra, list functions, ghidra headless, pyghidra, rename function ghidra | `ghidra-mcp/SKILL.md` | чтение |
| jshook, jshookmcp, frontend hook, cdp hook, frida session, symbolic execution, wasm analysis, adb bridge, native emulator, v8 inspector | `jshook-mcp/SKILL.md` | чтение |
| rea, rea-agents, reverse anything, frida rea, gdb rea, rizin, apktool jadx, flutter dart, evm bytecode, pcap tshark, il2cpp, go binary | `re-tools-mcp/SKILL.md` | чтение |
| llm red team, llm redteam, deepteam, prompt injection test, jailbreak test, pii leakage, shell injection llm, ssrf llm, crescendo jailbreak, tree jailbreak, guardrails, llm vulnerability, owasp llm, nist ai | `llm-redteam/SKILL.md` | чтение → запуск |
| reap, rea prompt, reap-17, reap-10, vulnerability research prompt, malware analysis prompt, binary exploration prompt, anti-cheat research, firmware prompt, kernel exploit prompt | `rea-prompts/SKILL.md` | чтение |
| ctf tools list, ctf toolbox, what tool for ctf, pwntools, rop gadget, ctf crypto tool, ctf forensics tool, ctf bruteforce | `ctf-toolindex/SKILL.md` | чтение |
| malware analysis tool, yara cuckoo, volatility, sandbox analysis, threat intel tool, ioc extract, malware collection, virustotal, hybrid analysis | `malware-toolindex/SKILL.md` | чтение |
| geolocate photo, geolocation osint, where is this photo, terrain match, shadow sun location, satellite imagery search, board candidate, exif gps, osm overpass, reverse image search location | `geo-osint/SKILL.md` | чтение → запуск |
| binary fingerprint, game scan, anti-cheat detect, engine detect, pe header, unity detect, unreal detect, elf scan, game recon, app fingerprint | `binary-recon/SKILL.md` | чтение → запуск |
| apk, smali, jadx, apktool, android reverse, ios, ipa, objection, mobsf, mobile reverse, firmware, binwalk, iot, malware, yara, radare2, r2, ghidra, ida, decompile, disassembl, pwn, rop, ret2libc, ctf, awd, edr, bloodhound, windows ad, digital forensics, code audit, threat hunt, protocol reverse | `reverse-skill/SKILL.md` | чтение → маршрут R0–R45 |

## Вызов маршрутизатора

```bash
# Направить к нужному под-навыку
python3 '${CLAUDE_SKILL_DIR}/scripts/router.py' --ask '<user ask>'

# Список всех маршрутов
python3 '${CLAUDE_SKILL_DIR}/scripts/router.py' --list

# Вывод в машиночитаемом формате
python3 '${CLAUDE_SKILL_DIR}/scripts/router.py' --ask '<user ask>' --json
```

