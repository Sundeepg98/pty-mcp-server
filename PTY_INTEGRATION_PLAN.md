# PTY Integration Plan: Preserving Existing Architecture

## Investigation Results

### ✅ GOOD: What to Keep
The original PTY has **excellent architecture** that we should preserve:

1. **Plugin Architecture** (`/plugins/`)
   - Clean separation into categories: terminal, process, system, network, serial
   - 37 well-structured tool plugins
   - Each tool has: name, description, input_schema, execute method

2. **Core Components** (`/core/`)
   - `SessionManager`: Manages PTY, Process, Socket, Serial sessions
   - Session types in `/core/sessions/`: Clean separation of concerns
   - Well-tested session management

3. **Libraries** (`/lib/`)
   - `BaseTool`: Clean abstraction for all tools
   - `ToolRegistry`: Dynamic plugin loading
   - `ToolResult`: Consistent response format
   - `PtyConfig`: Configuration management

4. **Tools Already Have MCP-Compatible Structure**:
   ```python
   class BashTool(BaseTool):
       @property
       def name(self) -> str: return "bash"
       
       @property
       def description(self) -> str: return "Start bash shell"
       
       @property
       def input_schema(self) -> Dict: return {...}
       
       def execute(self, arguments) -> ToolResult: ...
   ```

### ❌ BAD: What Needs Fixing
Only **ONE file** needs major changes: `main.py`
- Custom JSON protocol → MCP SDK protocol
- Missing error responses → Proper JSON-RPC error handling
- Direct stdin/stdout → MCP stdio_server

## The Solution: Adapter Pattern

**We don't rewrite everything!** We create an **adapter** that bridges existing tools to MCP SDK:

```python
# main.py - MCP SDK adapter for existing PTY architecture
from mcp.server import Server
from lib.registry import ToolRegistry
from core.manager import SessionManager

server = Server("pty-mcp-server")
registry = ToolRegistry()
session_manager = SessionManager()

@server.list_tools()
async def list_tools():
    # Convert existing tools to MCP format
    tools = []
    for name, tool in registry._tools.items():
        tools.append(types.Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.input_schema
        ))
    return tools

@server.call_tool()
async def call_tool(name, arguments):
    # Execute using existing tool infrastructure
    tool = registry.get_tool(name)
    result = tool.execute(arguments)
    return [types.TextContent(
        type="text",
        text=result.content if result.success else f"Error: {result.error}"
    )]
```

## Implementation Steps

### Step 1: Create MCP Adapter (main.py only)
- Import existing SessionManager, ToolRegistry, BaseTool
- Load all existing plugins using ToolRegistry
- Bridge to MCP SDK with @server decorators
- Proper error handling with JSON-RPC responses

### Step 2: No Changes to Existing Structure
- ✅ Keep `/core/` - All session management stays
- ✅ Keep `/lib/` - Base classes and registry stay
- ✅ Keep `/plugins/` - All 37 tools stay exactly as is
- ✅ Keep folder structure - No reorganization needed

### Step 3: Test Each Category
1. Terminal tools (bash, ssh, telnet)
2. Process tools (spawn, kill, proc_cmd)
3. System tools (exec, file, env, projects)
4. Network tools (socket operations)
5. Serial tools (serial port operations)

## Why This Approach is Best

1. **Minimal Changes**: Only touch main.py, everything else works
2. **Preserve Investment**: Keep all the good code and architecture
3. **Quick Implementation**: Can be done in one file
4. **Easy Testing**: Can test category by category
5. **Backward Compatible**: Can run both versions side-by-side

## Files to Change
```
CHANGE:
└── main.py          # Replace with MCP SDK adapter

KEEP AS-IS:
├── core/            # ✅ No changes
│   ├── manager.py   
│   └── sessions/    
├── lib/             # ✅ No changes
│   ├── base.py      
│   ├── registry.py  
│   └── config.py    
└── plugins/         # ✅ No changes
    ├── terminal/    # 8 tools
    ├── process/     # 6 tools
    ├── system/      # 7 tools
    ├── network/     # 6 tools
    └── serial/      # 5 tools
```

## Summary
We're NOT rewriting everything! We're creating a thin MCP SDK adapter layer that uses all the existing excellent architecture. This preserves your work while fixing the protocol issue.