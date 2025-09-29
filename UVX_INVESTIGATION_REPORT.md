# UVX Installation Investigation Report

## Current State Analysis

### Package Structure ✓
```
/var/projects/mcp-servers/pty-mcp-python/
├── core/          # Business logic
├── lib/           # Infrastructure
├── plugins/       # Tool implementations
├── tests/         # Test suite
└── main.py        # Entry point
```

### Existing Foundation
- **Entry Point**: `main.py` with `async def main()`
- **Dependencies**: Minimal - only `mcp>=1.0.0`
- **Architecture**: Clean separation already in place
- **Package Init**: `__init__.py` files present in all modules

## Requirements for UVX Support

### 1. Package Configuration
**File Needed**: `pyproject.toml`
```toml
[project]
name = "pty-mcp-server"
version = "3.1.0"
description = "PTY MCP Server with dynamic environment support"
requires-python = ">=3.8"
dependencies = ["mcp>=1.0.0"]

[project.scripts]
pty-mcp-server = "pty_mcp_server:run"

[tool.uvx]
scripts = ["pty-mcp-server"]
```

### 2. Module Restructuring
**Current**: Loose files with main.py at root
**Required**: Package format
```
pty_mcp_server/
├── __init__.py      # Package entry
├── __main__.py      # Console entry
├── server.py        # Main server (from main.py)
├── core/
├── lib/
└── plugins/
```

### 3. Entry Point Wrapper
**File Needed**: `pty_mcp_server/__init__.py`
```python
from .server import main

def run():
    """Console entry point for uvx"""
    import asyncio
    asyncio.run(main())
```

### 4. Build Configuration
**File Needed**: `pyproject.toml` additions
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["pty_mcp_server"]
```

## Implementation Scope

### Phase 1: Package Structure (2 hours)
1. Create `pty_mcp_server` directory
2. Move modules into package
3. Rename `main.py` → `server.py`
4. Create package `__init__.py` and `__main__.py`

### Phase 2: Configuration (1 hour)
1. Create `pyproject.toml` with metadata
2. Add build system configuration
3. Define console entry points
4. Configure uvx scripts

### Phase 3: Testing (1 hour)
1. Test local installation: `pip install -e .`
2. Test uvx installation: `uvx install .`
3. Verify command: `uvx pty-mcp-server`
4. Test MCP integration

## Architecture Preservation

### Maintained Principles
- **Dependency Flow**: main → core → lib (unchanged)
- **SessionManager**: Remains central coordinator
- **ToolRegistry**: Dynamic plugin loading preserved
- **Config Injection**: Configuration still injected into core

### No Breaking Changes
- All existing imports remain valid
- Tool structure unchanged
- Session management intact
- Environment handling preserved

## Benefits

1. **Single Command Install**: `uvx install pty-mcp-server`
2. **Isolated Environment**: uvx manages dependencies
3. **Version Management**: Easy upgrades/downgrades
4. **Distribution Ready**: Can publish to PyPI
5. **MCP Standard**: Follows MCP server conventions

## Risk Assessment

**Low Risk**:
- No logic changes required
- Only restructuring files
- Backward compatible
- Can maintain both structures during transition

## Recommendation

Proceed with implementation. The existing clean architecture makes this transformation straightforward without compromising design principles.