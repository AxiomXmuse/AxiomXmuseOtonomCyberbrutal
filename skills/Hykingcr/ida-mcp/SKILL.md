---
name: hykingcr-ida-mcp
description: "IDA Pro MCP bridge — 75 tools over HTTP JSON-RPC (decompile, disassemble, xrefs, memory, types, rename, debug, IDAPython execution, signature generation). Supports GUI plugin mode and headless idalib multi-IDB supervisor. Profiles: readonly, triage."
---

# HYKINGCR — IDA Pro MCP

Source: `repos/ida-pro-mcp/` (MIT license)

## Two Modes

| Mode | CLI | When to use |
|---|---|---|
| GUI proxy | `ida-pro-mcp` | IDA Pro GUI is open; plugin bridges to running IDB |
| Headless supervisor | `idalib-mcp <binary>` | No GUI; idalib processes binary directly (IDA 9.4+ Home/Pro) |

## Install

```bash
pip install ida-pro-mcp

# Install IDA plugin (adds MCP server to IDA's plugin dir)
ida-pro-mcp install
```

## Start

```bash
# GUI mode: run inside IDA (plugin auto-starts) or externally:
ida-pro-mcp --port 13337

# Headless mode: process a binary directly
idalib-mcp /path/to/binary.elf

# Headless supervisor (multiple IDBs):
idalib-mcp --supervisor /path/to/
```

## Profiles

Apply profiles to restrict tool surface:

```python
# Inside MCP client config:
apply_profile("readonly")   # analysis only, no mutations
apply_profile("triage")     # minimal: list_funcs, decompile, xrefs, get_string
```

**readonly profile tools:**
`server_health`, `list_funcs`, `list_globals`, `imports`, `imports_query`, `lookup_funcs`, `func_query`, `entity_query`, `int_convert`, `find_regex`, `decompile`, `disasm`, `func_profile`, `analyze_batch`, `xrefs_to`, `xref_query`, `xrefs_to_field`, `callees`, `basic_blocks`, `find_bytes`, `find`, `insn_query`, `export_funcs`, `callgraph`, `analyze_function`, `analyze_component`, `trace_data_flow`, `read_struct`, `type_query`, `get_bytes`, `get_int`, `get_string`, `get_global_value`, `stack_frame`

**triage profile tools:**
`list_funcs`, `list_globals`, `imports`, `lookup_funcs`, `decompile`, `disasm`, `xrefs_to`, `callees`, `get_string`

## 75 Tools by Module

### api_core — Identity & listings
`server_health`, `list_funcs`, `list_globals`, `imports`, `imports_query`, `lookup_funcs`, `func_query`, `entity_query`, `int_convert`, `find_regex`, `export_funcs`

### api_analysis — Decompile / disasm / xrefs
`decompile`, `disasm`, `func_profile`, `analyze_batch`, `xrefs_to`, `xref_query`, `xrefs_to_field`, `callees`, `basic_blocks`, `find_bytes`, `find`, `insn_query`, `callgraph`, `analyze_function`, `analyze_component`, `trace_data_flow`

### api_types — Type system (read/write)
`read_struct`, `type_query`, `set_type`, `create_struct`, `add_struct_member`, `set_member_type`

### api_modify — Rename / comment / patch
`rename_func`, `rename_global`, `set_func_comment`, `set_insn_comment`, `set_func_flags`, `patch_bytes`

### api_debug — Debug tools (opt-in via `?ext=dbg`)
`launch_debugger`, `attach_debugger`, `detach_debugger`, `run_to_cursor`, `step_into`, `step_over`, `get_registers`, `set_breakpoint`, `remove_breakpoint`, `read_debug_memory`

### api_memory — Memory reads
`get_bytes`, `get_int`, `get_string`, `get_global_value`

### api_stack — Stack frame
`stack_frame`

### api_python — IDAPython execution
`exec_python` — runs arbitrary IDAPython code in IDA's main thread via `@idasync`

### api_survey — Survey / search
`find`, `find_regex`, `find_bytes`

### api_sigmaker — Signature generation
`make_sig`, `search_sig` — generate IDA-format byte signatures from function addresses

## `@idasync` Pattern

All IDA calls must be posted to IDA's main thread:
```python
from ida_pro_mcp.worker_lifecycle import idasync

@idasync
def my_analysis():
    import idc
    return idc.get_name(0x400000)
```

## Extension Groups

- `?ext=dbg` — debug tools (attach/step/breakpoint); opt-in, disabled by default
- Default: all non-debug tools active

## Connection

```json
// MCP client config (stdio transport):
{
  "mcpServers": {
    "ida-pro-mcp": {
      "command": "ida-pro-mcp",
      "args": ["--port", "13337"]
    }
  }
}
```

HTTP transport: `ida-pro-mcp --http --port 13337`

## Reference

Full source: `$OMP_REPOS_ROOT/ida-pro-mcp/`
