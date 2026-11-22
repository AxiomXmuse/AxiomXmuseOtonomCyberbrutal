---
name: hykingcr-binary-recon
description: "Binary and game fingerprinting — PE header sniff, engine detection (Unity/Godot/Unreal/GameMaker), anti-cheat identification (EAC/BattleEye/VAC/Denuvo), ranked exploitation routes. Also covers ILSpy, Ghidra/IDA MCP, Frida, Cheat Engine RE methodology."
---

# HYKINGCR — Binary Recon (universal-modder)

Source: `repos/universal-modder/um/scan.py` (51KB) + `repos/universal-modder/skills/reverse-engineering/SKILL.md`

## Scan a Binary or Game Directory

```bash
# Quick scan (wrapper)
python3 '${CLAUDE_SKILL_DIR}/scripts/scan.py' --target /path/to/game/

# Or invoke um/cli.py directly
UM_ROOT=$OMP_REPOS_ROOT/universal-modder
python3 "$UM_ROOT/um/cli.py" scan /path/to/game/
```

## What `um scan` Detects

### Game Engine Detection
| Engine | Detection Method |
|---|---|
| Unity (Mono) | `Assembly-CSharp.dll`, `UnityPlayer.dll`, `globalgamemanagers` |
| Unity (IL2CPP) | `GameAssembly.dll` + `global-metadata.dat` |
| Unreal Engine | `UE4Game`, `UnrealEditor`, `Engine/Binaries/` |
| Godot | `godot.windows.opt.tools`, `project.godot`, `pck` files |
| GameMaker | `data.win`, `runner.exe`, `audiogroup*.dat` |
| CryEngine | `CryGame.dll`, `cry_*.dll` |
| Custom/Unknown | PE header heuristics + string scan |

### Anti-Cheat Detection
| Anti-Cheat | Signatures |
|---|---|
| EasyAntiCheat (EAC) | `EasyAntiCheat.exe`, `EasyAntiCheat_EOS.sys`, EAC service registry |
| BattlEye | `BEClient.dll`, `BEService.exe`, `BattlEye/` directory |
| VAC (Valve) | Steam integration + VAC module references |
| Denuvo | Import table: `VMProtectBegin`, Denuvo license strings |
| nProtect GameGuard | `npggNT.des`, `GameGuard.des` |
| XIGNCODE3 | `x3.xem` service |

### Platform Discovery (Steam/Epic/Xbox)
- Steam: VDF parser → `libraryfolders.vdf` → all game paths
- Epic: `LauncherInstalled.dat` parse
- Xbox: `appxmanifest.xml` scan

### PE Header Analysis
- Architecture (x86/x64/ARM), subsystem, linker version
- Import table: DLL list, suspicious imports
- Compiler/packer identification
- Section entropy (packer/encryption detection)
- Authenticode signature verification

## Output (JSON fingerprint)

```json
{
  "target": "/path/to/game",
  "engine": "Unity IL2CPP",
  "anti_cheat": ["EasyAntiCheat"],
  "platform": "Steam",
  "architecture": "x64",
  "exploit_routes": [
    {"rank": 1, "method": "IL2CPP dump + Cpp2IL", "difficulty": "medium"},
    {"rank": 2, "method": "Frida runtime hook", "difficulty": "medium"},
    {"rank": 3, "method": "Cheat Engine memory scan", "difficulty": "easy"}
  ],
  "warnings": ["EAC kernel driver active — do not attach debugger to live game"]
}
```

## Ranked Exploitation Routes

After detection, `um scan` ranks modding/exploitation approaches:

| Engine | Top Route |
|---|---|
| Unity Mono | ILSpy → `Assembly-CSharp.dll` → full C# source → BepInEx hook |
| Unity IL2CPP | Cpp2IL dump → Ghidra/IDA with Il2CppDumper script → Frida `il2cpp-frida-mcp` |
| Unreal Engine | UE4SS Dumper (reflection data) → names all gameplay classes → native hook |
| Godot | `gdre` tool → GDScript source recovery |
| GameMaker | `UndertaleModTool` → data.win parse |

## RE Methodology (from universal-modder skills)

```
Pick the tool by what the code is (um scan tells you):

Managed .NET  → ILSpy / dnSpyEx / ILSpy-MCP
Unity IL2CPP  → Cpp2IL + Il2CppDumper → Ghidra/IDA with generated script → Frida
Java (Minecraft, etc.) → Vineflower / CFR / Recaf
Native C/C++  → Ghidra (GhidraMCP) or IDA (ida-pro-mcp) → strings → xrefs → function

Dynamic / live:
  Cheat Engine: value scan → "find what writes to this" → struct → owner
  x64dbg: breakpoints + tracing (x64dbg-mcp; bind to 127.0.0.1)

Unreal: UE4SS dumper first — names most gameplay classes for free
```

## Knowledge Base Search

```bash
UM_ROOT=$OMP_REPOS_ROOT/universal-modder
python3 "$UM_ROOT/um/cli.py" kb search '<query>'
```

Searches `repos/universal-modder/knowledge/` field notes.

## Reference

Full source: `$OMP_REPOS_ROOT/universal-modder/`
RE skill: `$OMP_REPOS_ROOT/universal-modder/skills/reverse-engineering/SKILL.md`
