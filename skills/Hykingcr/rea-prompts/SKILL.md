---
name: hykingcr-rea-prompts
description: "REA reverse engineering prompt packs — 26 ready-to-use prompt libraries (reap-00 through reap-22+wildcard): native binary, Android/APK, kernel, vulnerability research, malware analysis, anti-cheat, firmware, Electron/JS, game RE, DMA/hardware cheat research, software cracking, Go/Rust binary source recovery."
---

# HYKINGCR — REA Prompt Packs (reap-00 – reap-22)

Source: `repos/REA-Prompts/Skills/` (MIT license)

## Usage

This skill is an **index/dispatcher**. When a pack is relevant:
1. Identify the pack from the table below
2. Read its `SKILL.md` directly from the absolute path
3. Follow the pack's procedure

## 26 Prompt Packs

| Pack | Name | Description | Absolute Path |
|---|---|---|---|
| reap-00 | Install and Verify | REA setup, verification, MCP server health check | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-00-install-and-verify/SKILL.md` |
| reap-01 | Getting Started | First analysis: binary identification, quick triage | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-01-getting-started/SKILL.md` |
| reap-02 | Feature Tracing | Trace any program feature: entry → data flow → exit | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-02-feature-tracing-any-program/SKILL.md` |
| reap-03 | Native Binary Exploration | ELF/PE/Mach-O deep dive: symbols, sections, xrefs | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-03-native-binary-exploration/SKILL.md` |
| reap-04 | Software & Feature Cloning | Reverse and re-implement a closed-source feature | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-04-software-and-feature-cloning/SKILL.md` |
| reap-05 | Games | Game binary analysis: engine ID, asset format, function map | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-05-games/SKILL.md` |
| reap-06 | Game Portability to WASM | Port game logic to WebAssembly | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-06-game-portability-to-wasm/SKILL.md` |
| reap-07 | Firmware & Embedded | Firmware extraction, filesystem, UART, JTAG | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-07-firmware-and-embedded/SKILL.md` |
| reap-08 | Android | APK analysis, Frida, Jadx, SSL pinning, root detection | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-08-android/SKILL.md` |
| reap-09 | Kernel Analysis | Linux kernel module analysis, syscall hooks, kprobes | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-09-kernel-analysis/SKILL.md` |
| reap-10 | Vulnerability Research | CVE analysis, PoC development, root cause, patch diff | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-10-vulnerability-research/SKILL.md` |
| reap-11 | Electron & JavaScript | Electron app: asar extract, main/renderer, JS deobfuscation | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-11-electron-and-javascript/SKILL.md` |
| reap-12 | Anti-Cheat & Protection | Anti-cheat system analysis: EAC, BattleEye, VAC, kernel hooks | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-12-anti-cheat-and-protection-research/SKILL.md` |
| reap-13 | DMA & Hardware Cheat (Defensive) | DMA read device detection, PCIe enumeration, IOMMU bypass indicators | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-13-dma-and-hardware-assisted-cheat-research-defensive/SKILL.md` |
| reap-14 | Software Cracking Research | License protection analysis: dongle, serial, online activation | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-14-software-cracking-research/SKILL.md` |
| reap-15 | Version Comparison & Crash | Binary diff across versions, crash reproduction, regression | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-15-version-comparison-and-crash-work/SKILL.md` |
| reap-16 | Long Running Investigations | Multi-session RE workflow, evidence tracking, progressive analysis | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-16-long-running-investigations/SKILL.md` |
| reap-17 | Malware Analysis | Malware triage, sandbox evasion detection, IOC extraction, YARA | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-17-malware-analysis/SKILL.md` |
| reap-18 | Advanced Binary Exploration | Obfuscated binary, OLLVM, VM packer, control flow deobfuscation | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-18-advanced-binary-exploration-and-deobfuscation/SKILL.md` |
| reap-19 | Kernel & Driver Exploitation | Kernel exploit dev: UAF, pool overflow, IOCTL misuse, privilege escalation | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-19-kernel-and-driver-exploitation-research/SKILL.md` |
| reap-20 | Advanced Software Cloning | Full feature reconstruction from stripped binary | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-20-advanced-software-cloning-and-feature-reconstruction/SKILL.md` |
| reap-21 | Protector & Obfuscator | Commercial packer/protector research: Themida, VMProtect, Enigma | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-21-protector-and-obfuscator-research/SKILL.md` |
| reap-22 | Go & Rust Binary Source Recovery | Stripped Go/Rust binary: pclntab, panic strings, type recovery | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-22-go-and-rust-binary-source-recovery/SKILL.md` |
| reap-wildcard | Wildcard | General-purpose RE prompt for any unlisted scenario | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-wildcard/SKILL.md` |
| reap-prompt-writing-tips | Tips | How to write effective RE prompts for LLM agents | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-prompt-writing-tips/SKILL.md` |
| reap-prompts | Index | Master prompt index | `$OMP_REPOS_ROOT/REA-Prompts/Skills/reap-prompts/SKILL.md` |

## Quick Dispatch

| Trigger | Pack |
|---|---|
| malware analysis prompt | reap-17 |
| vulnerability research prompt | reap-10 |
| anti-cheat research, eac battleye | reap-12 |
| kernel exploit prompt | reap-19 |
| firmware prompt, embedded | reap-07 |
| android, apk prompt | reap-08 |
| go binary, rust binary source | reap-22 |
| dma, hardware cheat | reap-13 |
| software cracking research | reap-14 |
| obfuscated binary, vmprotect, themida | reap-21 |
| binary exploration | reap-03 or reap-18 |
| game reverse engineering | reap-05 |

## Reference

Full source: `$OMP_REPOS_ROOT/REA-Prompts/`
