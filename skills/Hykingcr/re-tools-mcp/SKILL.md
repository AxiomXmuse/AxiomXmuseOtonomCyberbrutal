---
name: hykingcr-re-tools-mcp
description: "REA MCP — 80+ reverse engineering tools: Ghidra, IDA Pro, Hopper, JEB, Frida, pwndbg/pwntools, GDB, Rizin, apktool, jadx, IL2CPP, Flutter/Dart ELF, EVM bytecode, WASM, PCAP/tshark, firmware extraction, SQLite inspection, V8 runtime."
---

# HYKINGCR — REA Reverse Tools MCP

Source: `repos/rea/` (MIT license) | npm: `rea-agents` v6.8.0

## Start

```bash
# stdio MCP (default)
npx rea-agents@latest

# HTTP transport
npx rea-agents@latest --http

# Setup (copies skills to ~/.claude/skills/ and ~/.codex/skills/)
npx rea-agents@latest setup
```

## Tool Providers (40+ registration modules)

| Provider | Domain | Key Tools |
|---|---|---|
| `registerAnalysisSettingsTools` | Settings | analysis config, verbosity, timeout |
| `registerDevicetreeTool` | Firmware | devicetree blob parse, DTS output |
| `registerGpuCodeObjectsTools` | GPU | OpenCL/HIP code object analysis |
| `registerCaptureTools` | Network | pcap capture, tshark decode, filter |
| `registerSignalTools` | Signal | signal analysis, frequency domain |
| `registerWasmTools` | WASM | module inspect, function list, decompile |
| `registerApkSignatureTools` | Android | APK signature verify, v1/v2/v3/v4 |
| `registerElfNotesTool` | ELF | ELF note sections: build-id, ABI |
| `registerAppleIpsTool` | iOS | IPS crash report parse |
| `registerKernelModuleTool` | Linux | .ko module: symbols, params, deps |
| `registerPeLoadConfigTool` | Windows | PE load config: CFG, SEH, guard |
| `registerPeCertificatesTool` | Windows | PE Authenticode certificate chain |
| `registerPeImportsTool` | Windows | PE import table: DLLs, functions, ordinals |
| `registerPeResourcesTool` | Windows | PE resources: icons, strings, manifests |
| `registerNativeExportsTool` | Binary | ELF/PE/Mach-O export table |
| `registerEvmTools` | Blockchain | EVM bytecode disassemble, opcode decode |
| `registerSqliteTools` | Database | SQLite schema, query, dump |
| `registerRecordedCrashTools` | Debug | crash report analysis, symbolication |
| `registerDesktopApplicationTool` | Desktop | app metadata, frameworks detected |
| `registerModelArtifactTools` | AI/ML | ONNX, PyTorch, TF model inspection |
| `registerGoTools` | Go | pclntab parse, symbol recovery, goroutine |
| `registerIl2cppTools` | Unity | IL2CPP dump, type/method recovery |
| `registerRustTools` | Rust | panic strings, symbol demangle, rlib |
| `registerPythonPycTool` | Python | .pyc decompile, bytecode decode |
| `registerErlangTools` | Erlang | BEAM binary analysis |
| `registerAnalysisViewTool` | UI | analysis view export |
| `registerBinaryDiagnosticsTools` | Binary | checksec, entropy, packer detect |
| `registerFridaTools` | Dynamic | Frida attach, script inject, intercept |
| `registerApplicationTools` | App | app bundle analysis, metadata |
| `registerArtifactTools` | Files | file type detect, hash, extract |
| `registerNativeTools` | Native | native binary: strings, sections, relocs |
| `registerBrowserScenarioTool` | Browser | browser automation scenario |
| `registerBrowserTools` | Browser | CDP tools, page interaction |
| `registerWebScriptTool` | Web | web script analysis |
| `registerWebModuleTool` | Web | webpack/vite module analysis |
| `registerWebSourceLocationTool` | Web | source map location resolution |
| `registerWebRuntimeTools` | Web | runtime XHR/fetch capture |
| `registerWebNetworkCaptureTool` | Web | network request capture |
| `registerJavaScriptRecoveryTool` | JS | minified JS recovery, rename |
| `registerElectronTools` | Electron | asar extract, main/renderer analysis |
| `registerEnhancedTools` | Enhanced | composite analysis workflows |
| `registerJavaScriptRuntimeObservationTools` | JS | runtime observation, V8 hooks |
| `registerManagedTools` | .NET | managed code analysis |
| `registerFirmwareTools` | Firmware | firmware extraction, filesystem |
| `registerAndroidTools` | Android | APK analysis, DEX, resources |
| `registerApktoolTools` | Android | apktool decode/rebuild |
| `registerPcapTools` | Network | pcap/pcapng analysis, protocol decode |
| `registerFlutterTools` | Flutter | Flutter/Dart ELF symbol recovery |
| `registerJebTools` | JEB | JEB decompiler integration |
| `registerAdbTools` | Android | ADB shell, logcat, push/pull |

## Bridge Locations

Pre-built bridges for popular tools:
```
repos/rea/bridge/
├── ghidra/          ← Ghidra bridge (HTTP JSON-RPC)
├── hopper_bridge.py ← Hopper Disassembler bridge
├── pwndbg/          ← pwndbg GDB plugin bridge
├── pwntools/        ← pwntools CTF exploit library bridge
└── android/         ← ADB/Frida Android bridge
```

## Key Capabilities by Domain

**Reverse Engineering:**
- Ghidra, IDA Pro, Hopper, JEB via bridge
- `registerFridaTools` — dynamic instrumentation
- `registerBinaryDiagnosticsTools` — checksec, entropy, packer detection

**Mobile:**
- `registerAndroidTools` + `registerApktoolTools` + `registerAdbTools` — full Android pipeline
- `registerFlutterTools` — Dart ELF, Flutter symbol recovery
- `registerIl2cppTools` — Unity IL2CPP: type/method dump from GameAssembly.dll + global-metadata.dat

**Web/JS:**
- `registerJavaScriptRecoveryTool` + `registerWebModuleTool` — webpack/vite bundle analysis
- `registerWebRuntimeTools` + `registerWebNetworkCaptureTool` — XHR/fetch capture

**Binary:**
- `registerPeImportsTool` / `registerPeCertificatesTool` / `registerPeLoadConfigTool` — PE headers
- `registerElfNotesTool` — ELF notes
- `registerEvmTools` — EVM/Ethereum bytecode

**Network:**
- `registerCaptureTools` + `registerPcapTools` — live capture + pcap analysis via tshark
- `registerSignalTools` — RF signal analysis

## Reference

Full source: `$OMP_REPOS_ROOT/rea/`
