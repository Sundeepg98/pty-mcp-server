# ADR-002: Integrate Tmux Multi-Session Support

**Status:** Accepted
**Date:** 2024-01-20
**Deciders:** Architecture Team

---

## Context

PTY MCP Server initially supported 4 singleton sessions:
1. **PTY Session** - Single pseudo-terminal
2. **Process Session** - Single subprocess
3. **Socket Session** - Single network connection
4. **Serial Session** - Single serial port

**Limitations:**
- ❌ Only ONE of each type active at a time
- ❌ Sessions die when MCP server restarts
- ❌ Cannot run multiple dev servers concurrently
- ❌ Cannot have multiple database connections
- ❌ No way to detach and reattach to running processes

**User Pain Points:**
1. Starting `npm run dev` blocks all other operations
2. Opening `mysql` terminal requires dedicated session
3. Cannot monitor logs while developing
4. Restarting Claude Code kills all active processes

**Question:** How do we enable multiple concurrent persistent sessions?

## Options Considered

### Option 1: Multiple Singleton Instances
Create `pty_session_1`, `pty_session_2`, etc.

**Pros:**
- Simple implementation
- Minimal code changes

**Cons:**
- ❌ Fixed number of sessions (not scalable)
- ❌ Still dies on MCP restart
- ❌ No session naming (which is which?)
- ❌ No manual attach/detach capability

**Verdict:** ❌ Rejected - Not scalable or persistent

---

### Option 2: Custom Multi-Session Manager
Build custom process manager from scratch

**Pros:**
- Full control over implementation
- Tailored to our exact needs

**Cons:**
- ❌ Reinventing the wheel
- ❌ Significant development effort
- ❌ Need to solve persistence ourselves
- ❌ Manual attach/detach is complex
- ❌ Testing burden

**Verdict:** ❌ Rejected - Too much effort for solved problem

---

### Option 3: Integrate Tmux
Use `tmux` as the multi-session backend

**Pros:**
- ✅ Proven technology (30+ years)
- ✅ Native persistence (survives restarts)
- ✅ Unlimited named sessions
- ✅ Manual attach/detach built-in
- ✅ Session management already solved
- ✅ Cross-platform (Linux, macOS, BSD)

**Cons:**
- ⚠️ External dependency (tmux must be installed)
- ⚠️ Windows support limited (WSL required)
- ⚠️ Learning curve for users unfamiliar with tmux

**Verdict:** ✅ **SELECTED** - Best balance of features vs effort

## Decision

We integrate **tmux** as a 6th session type in PTY MCP Server.

### Implementation Approach

#### 1. Domain Layer
Create `TmuxSessionManager` in `core/sessions/tmux.py`:
- Manages multiple named sessions
- Coordinates with tmux server
- Provides session lifecycle operations

```python
class TmuxSessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def start_session(self, session_name: str, command: str)
    def list_sessions(self)
    def send_keys(self, session_name: str, command: str)
    def capture_pane(self, session_name: str, lines: int)
    def get_attach_command(self, session_name: str)
    def kill_session(self, session_name: str)
```

#### 2. Integration with SessionManager
Add `tmux_manager` to existing `SessionManager`:

```python
class SessionManager:
    def __init__(self, config=None):
        # Existing singletons
        self.pty_session = None
        self.proc_session = None
        self.socket_session = None
        self.serial_session = None

        # NEW: Tmux manager (multi-session)
        self.tmux_manager = None

    def get_tmux_manager(self) -> TmuxSessionManager:
        if not self.tmux_manager:
            self.tmux_manager = TmuxSessionManager()
        return self.tmux_manager
```

#### 3. Plugin Layer
Create 6 new tools in `plugins/tmux/`:
1. **tmux-start** - Start new session
2. **tmux-list** - List all sessions
3. **tmux-send** - Send commands
4. **tmux-capture** - Capture output
5. **tmux-attach** - Get attach command
6. **tmux-kill** - Kill session

**All tools follow 100% DI pattern:**
```python
class TmuxStartTool(BaseTool):
    def __init__(self, session_manager=None):
        super().__init__(session_manager)  # DI

    def execute(self, arguments):
        tmux_manager = self.session_manager.get_tmux_manager()
        return tmux_manager.start_session(...)
```

### Architecture Consistency

**Fits DDD Architecture:**
- ✅ Domain Layer: `TmuxSessionManager` (domain service)
- ✅ Application Layer: Integrated via `SessionManager`
- ✅ Interface Layer: 6 tools in `plugins/tmux/`
- ✅ Dependency Injection: 100% constructor-based

**Comparison with Existing Sessions:**

| Feature | PTY/Process/Socket/Serial | Tmux |
|---------|-------------------------|------|
| **Instance Type** | Singleton | Manager (multiple) |
| **Persistence** | Dies with MCP restart | Survives restarts |
| **Session Limit** | 1 per type (4 total) | Unlimited |
| **Manual Attach** | No | Yes (Ctrl+B, D) |
| **Naming** | Unnamed | User-defined names |

## Consequences

### Positive

✅ **Multi-Session Capability**
- Run dev server + database + logs concurrently
- No limit on number of sessions
- Each session independently managed

✅ **Persistence**
- Sessions survive MCP server restarts
- Sessions survive Claude Code restarts
- Can check on sessions hours/days later

✅ **Manual Interaction**
- `tmux attach -t session_name` for full control
- Press Ctrl+B, D to detach (process keeps running)
- Hybrid automation + manual workflow

✅ **Backward Compatibility**
- All existing 31 tools work unchanged
- No breaking changes to SessionManager API
- Singleton sessions unaffected

✅ **Architecture Alignment**
- Follows DDD layer separation
- Maintains 100% dependency injection
- Fits plugin architecture naturally

### Negative

⚠️ **External Dependency**
- Requires `tmux` installed on system
- Installation burden for users
- Version compatibility considerations

⚠️ **Windows Limitations**
- Tmux not native on Windows
- Requires WSL (Windows Subsystem for Linux)
- May confuse Windows-only users

⚠️ **Increased Complexity**
- 6 new tools to maintain
- Users must learn tmux basics
- Attach/detach workflow unfamiliar to some

### Mitigations

1. **Clear Documentation**
   - Feature documentation (docs/features/tmux-integration.md)
   - Use case examples (dev workflow, debugging)
   - Installation instructions

2. **Graceful Degradation**
   - Check if tmux is installed
   - Provide clear error messages
   - Suggest installation if missing

3. **Comprehensive Testing**
   - Integration tests (plugin loading)
   - Functional tests (real tmux operations)
   - Error handling tests

## Use Cases Enabled

### 1. Development Workflow
```python
# Start dev server
tmux-start(session_name="dev", command="npm run dev")

# Start database
tmux-start(session_name="db", command="mysql -u root")

# Start log watcher
tmux-start(session_name="logs", command="tail -f app.log")

# All run concurrently, survive restarts!
```

### 2. Interactive Debugging
```python
# Start Python REPL in tmux
tmux-start(session_name="debug", command="python3")

# Send commands remotely
tmux-send(session_name="debug", command="import sys")
tmux-send(session_name="debug", command="print(sys.version)")

# Need manual interaction? Attach!
tmux-attach(session_name="debug")
# User runs: tmux attach -t debug
# Full interactive REPL access
# Press Ctrl+B, D to detach
```

### 3. Long-Running Tasks
```python
# Start build in background
tmux-start(session_name="build", command="npm run build:prod")

# Check progress later
tmux-capture(session_name="build", lines=50)

# Build done? Kill session
tmux-kill(session_name="build")
```

## Implementation Status

**Completed:**
- ✅ `TmuxSessionManager` implementation (251 lines)
- ✅ 6 tools in `plugins/tmux/`
- ✅ SessionManager integration
- ✅ Integration tests
- ✅ Functional tests
- ✅ Merged to master (commit 9c07ec4)

**Tool Count:**
- Before: 31 tools
- After: **37 tools** (31 + 6 tmux)

**Total Session Types:**
- 4 singletons (PTY, process, socket, serial)
- 1 multi-session manager (tmux)

## Alternatives Considered

### Standalone tmux-mcp Server
**Approach:** Create separate MCP server for tmux only

**Pros:**
- Minimal dependencies
- Focused functionality
- Easier to deploy independently

**Cons:**
- ❌ User must manage 2 MCP servers
- ❌ No shared SessionManager
- ❌ Duplicate infrastructure code

**Decision:** Rejected - Integration better for users

### Using screen Instead of tmux
**screen** is older alternative to tmux

**Pros:**
- More widely available
- Simpler implementation

**Cons:**
- ❌ Less powerful (no pane splitting)
- ❌ Less active development
- ❌ tmux is modern standard

**Decision:** Rejected - tmux is industry standard

## Future Enhancements

Potential future additions (not committed):
1. **tmux-rename** - Rename sessions
2. **tmux-switch** - Switch between sessions
3. **tmux-split** - Create split panes
4. **tmux-windows** - Manage multiple windows
5. **tmux-config** - Configure tmux options

These can be added incrementally based on user demand.

## Related Decisions

- **[ADR-001](./001-domain-driven-design.md)** - DDD architecture (tmux follows this)
- **Dependency Injection** - See [dependency-injection.md](../dependency-injection.md)

## Metrics

**Before Integration:**
- 31 tools
- 4 session types (all singleton)
- Max concurrent sessions: 4

**After Integration:**
- 37 tools (+6)
- 5 session types (4 singleton + 1 multi)
- Max concurrent sessions: 4 singletons + unlimited tmux

## References

- [Tmux Official Documentation](https://github.com/tmux/tmux/wiki)
- [tmux Cheat Sheet](https://tmuxcheatsheet.com/)
- [Feature Documentation](../../features/tmux-integration.md)

---

**Review Date:** 2024-07-20 (6 months)
**Reviewers:** Architecture team, users with tmux workflows
