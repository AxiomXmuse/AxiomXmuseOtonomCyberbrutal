---
name: hykingcr-jshook-mcp
description: "jshook MCP — 735 tools across 36 domains: CDP/browser, Frida instrumentation, Ghidra analysis, WASM, V8 inspector, ADB bridge, native emulator, syscall hook, TLS inspector, exploit-dev, protocol analysis. Profile-tiered loading, hot-reload plugins, declarative workflows."
---

# HYKINGCR — jshook MCP

Source: `repos/jshookmcp/` | npm: `@jshookmcp/jshook`

## Start

```bash
# stdio MCP (default)
npx jshookmcp
# or
npx @jshookmcp/jshook

# HTTP transport
npx @jshookmcp/jshook --http --port 3333
```

## Profile Tiers

Load only what you need — context window vs. capability tradeoff:

| Profile | Tools loaded | Context size |
|---|---|---|
| `search` | ~50 core tools | ~3K tokens |
| `workflow` | ~200 tools | ~20K tokens |
| `full` | all 735 tools | ~109K tokens |

## 36 Domain Modules

| Domain | Tools | Key Capabilities |
|---|---|---|
| `browser` | ~40 | CDP session management, page navigation, screenshot, network intercept |
| `hook` | ~30 | Frida hook injection, interceptor attach/detach, message relay |
| `frida` (via hook) | ~25 | `FridaSession` — spawn/attach, RPC exports, stalker tracing |
| `symbolic` | ~20 | `SymbolicExecutor` — angr/Z3 backed symbolic execution |
| `ghidra` (analyzer) | ~25 | `GhidraAnalyzer` — decompile, xrefs, rename, headless batch |
| `adb` | ~20 | `ADB bridge` — device list, shell, logcat, push/pull, screenshot |
| `v8-inspector` | ~15 | `V8InspectorProvider` — CDP debug protocol, heap snapshot, profiler |
| `dart-inspector` | ~10 | Dart VM inspector for Flutter app analysis |
| `emulator` | ~15 | `NativeEmulator` via QEMU/Unicorn — binary emulation without hardware |
| `native-emulator` | ~15 | PE/ELF native code emulation, register/memory control |
| `syscall-hook` | ~15 | System call interception and replay |
| `tls-inspector` | ~12 | TLS handshake dissection, certificate chain, MITM setup |
| `wasm` | ~20 | WASM module analysis, function export enumeration, memory inspection |
| `trace` | ~15 | `TraceRecorder` — function call trace, stack trace, coverage |
| `monitor` | ~10 | Process/memory monitor, resource usage, event log |
| `deobfuscator` | ~15 | JS/native deobfuscation — control flow simplify, string decrypt |
| `crypto` | ~10 | Crypto algorithm detection, key extraction, cipher analysis |
| `stealth` | ~10 | Anti-detection: hook masking, detection evasion indicators |
| `detector` | ~10 | Frida/debugger/root/emulator detection probe |
| `binary-secrets` | ~10 | Hardcoded credential/key extraction from binaries |
| `jadx-search` | ~10 | Jadx Java decompiler search integration |
| `axml-parser` | ~8 | Android XML (AXML) binary format parser |
| `apk-packer` | ~10 | APK repack, sign, zipalign |
| `captcha` | ~8 | CAPTCHA solving integration hooks |
| `protocol-analysis` | ~15 | Custom binary protocol analysis, field extraction |
| `exploit-dev` | ~15 | ROP gadget search, shellcode generation helpers, pwntools bridge |
| `symbolic` (Z3) | ~10 | Z3 SMT solver integration for constraint solving |
| `extension-registry` | ~8 | Hot-reload plugin management (`ExtensionManager`) |
| `mojo-ipc` | ~8 | Chromium Mojo IPC analysis |
| `webgpu` | ~5 | WebGPU shader analysis |
| `worker` | ~8 | Web worker and shared worker inspection |
| `security` | ~12 | CSP analysis, CORS audit, cookie security flags |
| `skia-capture` | ~5 | Skia rendering pipeline capture |
| `process` | ~10 | Process enumeration, memory map, module list |
| `collector` | ~8 | Data collection and exfiltration detection |
| `external` | ~8 | External tool integration bridge |

## Key Classes

| Class | Role |
|---|---|
| `FridaSession` | Spawn/attach to process, inject JS, call RPC exports, use Stalker for coverage |
| `GhidraAnalyzer` | Headless Ghidra analysis: decompile functions, cross-references, batch rename |
| `SymbolicExecutor` | angr/Z3 backed symbolic execution: find paths, solve constraints |
| `BrowserSessionCoordinator` | CDP multi-tab orchestration, network capture, XHR intercept |
| `WorkflowEngine` | Declarative YAML/JSON workflow execution across multiple tools |
| `TraceRecorder` | Record function call traces with arguments, return values, stack |
| `V8InspectorProvider` | V8 debug protocol: heap snapshot, CPU profiler, remote script eval |
| `ExtensionManager` | Hot-reload plugins without server restart |

## Fleet API

Multi-agent orchestration via `./fleet-api`:
```typescript
import { createFleet } from '@jshookmcp/jshook/fleet-api'
const fleet = createFleet({ agents: 4, transport: 'http' })
fleet.distribute(tasks)
```

## Declarative Workflows

```yaml
# workflow.yaml
name: frida-ssl-unpin
steps:
  - tool: adb.connect
    args: { device: "emulator-5554" }
  - tool: frida.spawn
    args: { package: "com.target.app" }
  - tool: hook.inject
    args: { script: "ssl-pinning-bypass.js" }
  - tool: trace.start
    args: { filter: "*.SSL*" }
```

```bash
npx @jshookmcp/jshook workflow run workflow.yaml
```

## Reference

Full source: `$OMP_REPOS_ROOT/jshookmcp/`
