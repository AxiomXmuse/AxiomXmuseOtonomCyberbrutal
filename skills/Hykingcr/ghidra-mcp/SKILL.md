---
name: hykingcr-ghidra-mcp
description: "Ghidra MCP bridge — 25 tools (decompile, disassemble, xrefs, rename, memory read, function search). Supports GUI mode (Java plugin on port 8080) and headless mode via PyGhidra. DeferredBackend for session-load gating."
---

# HYKINGCR — Ghidra MCP

Source: `repos/GhidraMCP/` (Apache-2.0)

## Two Modes

| Mode | How | When |
|---|---|---|
| GUI | Java plugin starts HTTP server on port 8080; Python client connects | Ghidra GUI is open with a program loaded |
| Headless | `python -m ghidra_mcp --headless` via PyGhidra | No GUI; batch analysis |

## Install

```bash
pip install ghidra-mcp

# Install Java plugin into Ghidra:
# Copy GhidraMCPPlugin.jar to $GHIDRA_HOME/Extensions/Ghidra/
# Enable in Ghidra: File → Install Extensions → GhidraMCP → restart
```

## Start

```bash
# GUI mode (Ghidra must have a program open):
python -m ghidra_mcp             # connects to localhost:8080

# Custom port:
python -m ghidra_mcp --port 8181

# Headless via PyGhidra:
python -m ghidra_mcp --headless --binary /path/to/binary
```

## 25 MCP Tools

| Tool | Description |
|---|---|
| `get_program_info` | Name, architecture, language, compiler, base address |
| `list_functions` | Paginated function list (offset, limit, optional filter) |
| `search_functions_by_name` | Search functions by name regex (offset, limit) |
| `list_classes` | List all defined classes (offset, limit) |
| `list_namespaces` | List all namespaces (offset, limit) |
| `list_segments` | Memory segments with addresses and sizes |
| `list_imports` | Imported symbols and their addresses |
| `list_exports` | Exported symbols |
| `list_data_items` | Defined data labels (offset, limit) |
| `list_strings` | All defined strings (offset, limit, optional filter) |
| `get_function_by_address` | Function at address: name, entry, body |
| `decompile_function` | Decompile function by name → C pseudocode |
| `decompile_function_by_address` | Decompile function at address |
| `disassemble_function` | Disassemble function at address (offset, limit) |
| `get_xrefs_to` | Cross-references TO an address |
| `get_xrefs_from` | Cross-references FROM an address |
| `get_function_xrefs` | All xrefs into a function |
| `get_function_calls` | All functions called by a function |
| `read_memory` | Raw bytes at address (length) |
| `rename_function_by_address` | Rename function at address |
| `rename_function` | Rename function by current name |
| `rename_data` | Rename a data label at address |
| `rename_variable` | Rename local variable in function |
| `set_function_prototype` | Set function signature string |
| `set_decompiler_comment` | Add comment at address in decompiler view |

**GUI-only tools (gated by DeferredBackend in headless):**
`get_current_address`, `get_current_function` — unavailable without active GUI session; headless returns "not available".

## `DeferredBackend` Pattern

In headless mode, `DeferredBackend` gates all tools that require a loaded program until `GhidraBackend.request()` confirms the session is ready. GUI-only tools return a structured error; all analysis tools work normally.

## Example Usage (Python MCP client)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["-m", "ghidra_mcp"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("decompile_function", {"name": "main"})
            print(result.content[0].text)

asyncio.run(main())
```

## Reference

Full source: `$OMP_REPOS_ROOT/GhidraMCP/`
