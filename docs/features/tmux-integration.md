# Tmux Integration for PTY MCP

## Overview

PTY MCP now includes **tmux integration**, adding 6 new tools for multi-session management with session persistence and true mid-execution backgrounding.

**Total tools: 31 (original) + 6 (tmux) = 37 tools**

## Architecture

### Integration Design

The tmux integration follows PTY MCP's plugin architecture with 100% dependency injection:

```
pty_mcp_server/
├── core/
│   ├── sessions/
│   │   ├── tmux.py          # TmuxSessionManager class
│   │   ├── pty.py           # Existing PTY session
│   │   ├── process.py       # Existing process session
│   │   ├── socket.py        # Existing socket session
│   │   └── serial.py        # Existing serial session
│   └── manager.py            # SessionManager (updated with tmux_manager)
│
└── plugins/
    └── tmux/                 # NEW: Tmux plugin category
        ├── __init__.py
        ├── tmux_start.py     # Start new session
        ├── tmux_list.py      # List all sessions
        ├── tmux_send.py      # Send commands
        ├── tmux_capture.py   # Capture output
        ├── tmux_attach.py    # Get attach command
        └── tmux_kill.py      # Kill session
```

### Key Differences from Other Sessions

| Feature | PTY/Process/Socket/Serial | Tmux |
|---------|-------------------------|------|
| **Instance Type** | Singleton (one per type) | Manager (multiple named sessions) |
| **Persistence** | Dies with MCP restart | Survives restarts (tmux server) |
| **Session Limit** | 1 per type (4 total) | Unlimited |
| **Manual Attach** | No | Yes (Ctrl+B, D) |
| **Naming** | Unnamed | User-defined names |

## New Tools

### 1. `tmux-start`
Start a new detached tmux session.

**Parameters:**
- `session_name` (string, required): Unique name for the session
- `command` (string, required): Command to run

**Example:**
```python
{
    "session_name": "dev-server",
    "command": "npm run dev"
}
```

### 2. `tmux-list`
List all active tmux sessions.

**Parameters:** None

**Output:**
- Session names
- Creation timestamps
- Attached/Detached status

### 3. `tmux-send`
Send commands to a running session (non-interactive).

**Parameters:**
- `session_name` (string, required): Target session
- `command` (string, required): Command to send

**Example:**
```python
{
    "session_name": "dev-server",
    "command": "npm test"
}
```

### 4. `tmux-capture`
Capture terminal output from a session without attaching.

**Parameters:**
- `session_name` (string, required): Session to capture from
- `lines` (integer, optional): Number of lines to capture

**Example:**
```python
{
    "session_name": "dev-server",
    "lines": 50
}
```

### 5. `tmux-attach`
Get the command to manually attach to a session from a terminal.

**Parameters:**
- `session_name` (string, required): Session to attach to

**Output:**
- Attach command: `tmux attach -t <session_name>`
- Detach instructions: Press Ctrl+B, then D

### 6. `tmux-kill`
Kill a session and terminate its processes.

**Parameters:**
- `session_name` (string, required): Session to kill

## Use Cases

### Development Workflow

```python
# Start dev server
tmux-start(session_name="dev", command="npm run dev")

# Start database
tmux-start(session_name="db", command="mysql -u root")

# Start log watcher
tmux-start(session_name="logs", command="tail -f app.log")

# All run concurrently, survive MCP restarts!
```

### Interactive Debugging

```python
# Start Python REPL in tmux
tmux-start(session_name="debug", command="python3")

# Send commands remotely
tmux-send(session_name="debug", command="import sys")
tmux-send(session_name="debug", command="print(sys.version)")

# Need manual interaction? Get attach command
tmux-attach(session_name="debug")
# User runs: tmux attach -t debug
# Full interactive REPL access
# Press Ctrl+B, D to detach - process keeps running!
```

## Integration with SessionManager

### SessionManager Changes

```python
class SessionManager:
    def __init__(self, config=None):
        # Existing singleton sessions
        self.pty_session: Optional[PTYSession] = None
        self.proc_session: Optional[ProcessSession] = None
        self.socket_session: Optional[SocketSession] = None
        self.serial_session: Optional[SerialSession] = None

        # NEW: Tmux manager (supports multiple sessions)
        self.tmux_manager: Optional[TmuxSessionManager] = None

    def get_tmux_manager(self) -> TmuxSessionManager:
        """Get or create tmux session manager"""
        if not self.tmux_manager:
            self.tmux_manager = TmuxSessionManager()
        return self.tmux_manager
```

### Dependency Injection

All tmux tools receive `session_manager` via constructor injection (BaseTool pattern):

```python
class TmuxStartTool(BaseTool):
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        # Injected session_manager is used here
        tmux_manager = self.session_manager.get_tmux_manager()
        result = tmux_manager.start_session(...)
```

## Testing

### Integration Tests

Run comprehensive integration tests:

```bash
pytest tests/integration/test_tmux_integration.py
```

**Tests:**
1. SessionManager has tmux_manager
2. Tool registry loads 6 tmux tools
3. All tools are properly registered
4. Tool definitions are correct
5. Cleanup works without errors

### Functional Tests

Run functional tests with real tmux operations:

```bash
pytest tests/functional/test_tmux_functional.py
```

**Tests:**
1. Start a tmux session
2. Send commands to session
3. Capture output
4. List sessions
5. Get attach command
6. Kill session
7. Verify cleanup

## Comparison: PTY MCP vs tmux-mcp (Standalone)

### PTY MCP Tmux Integration (This Implementation)

**Advantages:**
- ✅ Unified tool interface (37 tools in one MCP)
- ✅ Shared SessionManager across all tool types
- ✅ Consistent architecture with existing PTY tools
- ✅ Single MCP server to manage

**Use Case:**
- Comprehensive I/O toolkit with multi-session capabilities
- Teams wanting all-in-one MCP solution

### Standalone tmux-mcp Server

**Advantages:**
- ✅ Minimal dependencies
- ✅ Focused solely on tmux operations
- ✅ Easier to deploy independently
- ✅ Smaller codebase

**Use Case:**
- Users who only need tmux functionality
- Microservice-style MCP deployment

**Both are valid approaches!** Choose based on your needs:
- Want all-in-one? → PTY MCP with tmux integration
- Want focused tool? → Standalone tmux-mcp

## Future Enhancements

Potential future additions:

1. **tmux-rename**: Rename sessions
2. **tmux-switch**: Switch between sessions
3. **tmux-split**: Create split panes
4. **tmux-windows**: Manage multiple windows
5. **tmux-config**: Configure tmux options

## Backward Compatibility

The tmux integration is **fully backward compatible**:

- ✅ All existing 31 tools work unchanged
- ✅ No breaking changes to SessionManager API
- ✅ Existing singleton sessions unaffected
- ✅ Tool registry automatically discovers tmux tools

## Summary

**PTY MCP now has:**
- 37 total tools (31 original + 6 tmux)
- 6 categories: terminal, process, network, serial, system, **tmux**
- Maximum concurrent sessions: 4 singletons + unlimited tmux sessions
- True multi-session management with persistence

**Key Innovation:**
Combines PTY MCP's comprehensive I/O capabilities with tmux's session management, providing both single-task operations (PTY/process/socket/serial) and multi-session workflows (tmux) in one unified MCP server.
