# Python Package vs Source Architecture Report
## PTY MCP Server Analysis

**Date:** 2025-09-30  
**Version:** 3.1.0  
**Status:** Critical Issues Identified

---

## Executive Summary

The PTY MCP Server has **fundamental architectural incompatibilities** between source execution (pty-fixed) and package execution (pty-uvx). While the immediate import path issue was fixed, there are **5 critical architectural problems** that prevent proper package operation.

---

## Architecture Comparison

### 1. EXECUTION ENVIRONMENTS

| Aspect | Source (pty-fixed) | Package (pty-uvx) |
|--------|-------------------|-------------------|
| **Launch Method** | `bash launch.sh → python3 main.py` | `pty-mcp-server → entry point` |
| **Working Directory** | `/var/projects/mcp-servers/pty-mcp-python/` | User's current directory |
| **Python Executable** | System Python (`/usr/bin/python3`) | Isolated venv (`~/.local/share/uv/tools/pty-mcp-server/bin/python3`) |
| **Module Resolution** | Project directory in sys.path | Only site-packages in sys.path |

### 2. IMPORT PATH STRUCTURES

**Source Execution:**
```
/var/projects/mcp-servers/pty-mcp-python/
├── main.py                    ← Entry point
├── core/                      
├── lib/                       
└── plugins/
    └── terminal/
        └── bash.py            ← Imports as "plugins.terminal.bash"
```

**Package Execution:**
```
site-packages/
└── pty_mcp_server/           ← Package namespace
    ├── __init__.py           ← Entry point
    ├── server.py
    ├── core/
    ├── lib/
    └── plugins/
        └── terminal/
            └── bash.py        ← Must import as "pty_mcp_server.plugins.terminal.bash"
```

---

## Critical Issues Identified

### 🔴 Issue #1: Broken Import Paths (PARTIALLY FIXED)
**Location:** `/pty_mcp_server/lib/registry.py:83`
```python
# ORIGINAL (BROKEN):
module = importlib.import_module(f"{plugin_dir.name}.{module_name}")

# FIXED:
if is_packaged:
    import_path = f"pty_mcp_server.plugins.{plugin_dir.name}.{module_name}"
else:
    import_path = f"{plugin_dir.name}.{module_name}"
```
**Status:** ✅ Fixed in latest commit

---

### 🔴 Issue #2: Sys.path Manipulation in ALL Plugins
**Location:** Every plugin file (31 occurrences)
```python
# PROBLEMATIC CODE IN EVERY PLUGIN:
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.base import BaseTool, ToolResult
```

**Problems:**
- Assumes `__file__` is always available and reliable
- Adds wrong paths in package environment
- Creates import conflicts
- Makes package imports unpredictable

**Required Fix:**
```python
# Should be:
from pty_mcp_server.lib.base import BaseTool, ToolResult
# Or with relative imports:
from ...lib.base import BaseTool, ToolResult
```

---

### 🔴 Issue #3: Hard-coded Absolute Paths
**Location:** `/pty_mcp_server/lib/config.py:26`
```python
base_dir = os.environ.get('PTY_MCP_BASE_DIR', '/home/sundeep/.claude/mcp/pty')
config_path = os.path.join(base_dir, 'config', 'projects.json')
```

**Problems:**
- Assumes specific user directory structure
- Won't work on other machines
- Package can't access these paths

**Required Fix:**
- Use XDG base directories
- Or package data resources
- Or user config directory (`~/.config/pty-mcp/`)

---

### 🔴 Issue #4: File-based Plugin Discovery
**Location:** `/pty_mcp_server/lib/registry.py:116`
```python
plugins_dir = Path(base_dir) / "plugins"
for category_dir in plugins_dir.iterdir():
    if category_dir.is_dir():
        # ...file system traversal
```

**Problems:**
- Assumes plugins are files on disk
- In package, might be in zip or wheel
- `__file__` may not point to actual directory

**Required Fix:**
- Use `importlib.resources` for package data
- Or explicit plugin registration
- Or entry points discovery

---

### 🔴 Issue #5: State Persistence Paths
**Location:** `/pty_mcp_server/lib/config.py:28`
```python
state_path = os.path.join(base_dir, '.active_project')
```

**Problems:**
- Writes to package installation directory
- May not have write permissions
- State lost on package updates

**Required Fix:**
- Use proper user data directory
- `~/.local/share/pty-mcp/` on Linux
- Or XDG_DATA_HOME

---

## Impact Analysis

### Current State
- **0 tools exposed** in pty-uvx (was loading 0 from 5 categories)
- Import mechanism partially fixed but plugins still broken
- Configuration and state management non-functional in package

### Root Causes
1. **Design Assumption:** Code assumes it always runs from source directory
2. **Import Strategy:** Relies on sys.path manipulation instead of proper imports
3. **Resource Access:** Direct file system access instead of package resources
4. **Path Resolution:** Uses `__file__` and relative paths extensively

---

## Recommended Solution Path

### Phase 1: Fix Imports (URGENT)
1. ✅ Fix plugin loader import paths (DONE)
2. ⬜ Remove sys.path manipulations from all 31 plugins
3. ⬜ Convert to proper package imports or relative imports

### Phase 2: Fix Resource Access
1. ⬜ Replace hard-coded paths with platform-appropriate directories
2. ⬜ Use `importlib.resources` for package data
3. ⬜ Implement proper config file discovery

### Phase 3: Fix State Management
1. ⬜ Move state files to user data directory
2. ⬜ Implement migration for existing configurations
3. ⬜ Add environment variable overrides

### Phase 4: Testing & Validation
1. ⬜ Create automated tests for package installation
2. ⬜ Test on clean system without source code
3. ⬜ Verify all 31 tools load and function

---

## Technical Details

### Python Import Resolution
```python
# SOURCE CONTEXT
sys.path = [
    '',  # Current directory
    '/var/projects/mcp-servers/pty-mcp-python',  # Added by script
    '/usr/lib/python3.10/site-packages',  # System packages
]

# PACKAGE CONTEXT  
sys.path = [
    '',  # Current directory
    '/home/sundeep/.local/share/uv/tools/pty-mcp-server/lib/python3.12/site-packages',  # Isolated
]
```

### Package Structure Requirements
```
pty_mcp_server/
├── __init__.py         # Must define package interface
├── py.typed           # For type hints (optional)
├── plugins/
│   └── __init__.py    # Makes it a proper package
└── data/              # Package data files
    └── config.json    # Default configuration
```

---

## Conclusion

The PTY MCP Server requires **significant refactoring** to work properly as a package. The current architecture is deeply tied to source execution patterns that don't translate to packaged distribution.

**Immediate Action Required:**
1. Remove all sys.path manipulations from plugins
2. Fix import statements to use package namespace
3. Relocate configuration and state files

**Estimated Effort:** 
- Quick fixes: 2-4 hours
- Proper refactoring: 8-12 hours
- Full testing: 4-6 hours

---

## Appendix: File Listing

### Files with sys.path manipulation (31 files):
- All files in `plugins/terminal/*.py`
- All files in `plugins/process/*.py`
- All files in `plugins/network/*.py`
- All files in `plugins/serial/*.py`
- All files in `plugins/system/*.py`
- `core/manager.py`

### Files with hard-coded paths:
- `lib/config.py`
- `config/projects.json`

### Files using __file__:
- `server.py:135`
- All plugin files (for sys.path)