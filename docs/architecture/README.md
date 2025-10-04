# Architecture Overview

PTY MCP Server follows **Domain-Driven Design (DDD)** principles with **100% Dependency Injection**.

---

## Design Philosophy

### Core Principles

1. **Domain-Driven Design** - Business logic separated from infrastructure
2. **100% Dependency Injection** - No global state, all dependencies injected
3. **Plugin Architecture** - Tools are dynamically discovered and loaded
4. **Clean Architecture** - Dependencies point inward toward domain

---

## Layer Structure

```
pty_mcp_server/
├── core/           # DOMAIN LAYER
├── lib/            # APPLICATION LAYER
└── plugins/        # INTERFACE LAYER
```

### Domain Layer (`core/`)
**Purpose:** Business logic and domain entities

**Components:**
- `core/manager.py` - **SessionManager** (domain service)
  - Coordinates all session types
  - Manages project context
  - Provides environment management

- `core/sessions/` - **Domain entities:**
  - `pty.py` - PTY session (pseudo-terminal)
  - `process.py` - Process session (subprocess)
  - `socket.py` - Socket session (TCP/UDP)
  - `serial.py` - Serial session (hardware communication)
  - `tmux.py` - Tmux manager (multi-session)

**Responsibilities:**
- Session lifecycle management
- Domain rules enforcement
- State encapsulation
- No external dependencies (infrastructure concerns)

**Key Pattern:**
```python
class SessionManager:
    """Domain Service - coordinates sessions"""
    def __init__(self, config=None):
        self.pty_session: Optional[PTYSession] = None
        self.proc_session: Optional[ProcessSession] = None
        self.tmux_manager: Optional[TmuxSessionManager] = None
        # ... etc
```

---

### Application Layer (`lib/`)
**Purpose:** Use cases and application services

**Components:**
- `lib/registry.py` - **ToolRegistry** (application service)
  - Plugin discovery and loading
  - Tool instantiation with DI
  - Tool execution orchestration

- `lib/base.py` - **BaseTool** interface
  - Abstract base for all tools
  - Defines tool contract
  - ToolResult standard format

- `lib/env_manager.py` - **Environment management**
  - Project-specific environment variables
  - Dynamic environment switching

- `lib/config.py` - **Configuration management**
  - Project configuration persistence
  - Configuration loading/saving

**Responsibilities:**
- Tool discovery and loading
- Plugin coordination
- Use case orchestration
- Application-level services

**Key Pattern:**
```python
class ToolRegistry:
    """Application Service - manages tools"""
    def __init__(self, session_manager=None):
        self.session_manager = session_manager  # DI

    def _instantiate_tool(self, tool_class):
        return tool_class(self.session_manager)  # Inject dependency
```

---

### Interface Layer (`plugins/`)
**Purpose:** Tool implementations (adapters)

**Structure:**
```
plugins/
├── terminal/    # 8 tools (connect, ssh, telnet, etc.)
├── process/     # 6 tools (spawn, kill, send, etc.)
├── network/     # 6 tools (socket operations)
├── serial/      # 5 tools (serial port operations)
├── system/      # 6 tools (env, file, status, etc.)
└── tmux/        # 6 tools (session management)
```

**Total:** 37 tools across 6 categories

**Responsibilities:**
- User-facing tool implementations
- Input validation and sanitization
- Output formatting (MCP protocol)
- Adapting domain services to tool interface

**Key Pattern:**
```python
class TmuxStartTool(BaseTool):
    """Interface Layer - adapts domain service to tool"""
    def __init__(self, session_manager=None):
        super().__init__(session_manager)  # DI

    def execute(self, arguments):
        # Use injected domain service:
        manager = self.session_manager.get_tmux_manager()
        result = manager.start_session(...)
        return ToolResult(...)  # Standard format
```

---

### Infrastructure (Implicit)
**Location:** Currently scattered (needs improvement)

**Components:**
- `server.py` - MCP protocol adapter
- Session classes - External process/socket management
- `lib/config.py` - File I/O operations

**Should be refactored to:** `infrastructure/`
- `mcp/` - Protocol adapters
- `filesystem/` - File I/O
- `processes/` - External process management

---

## Dependency Flow

```
User Request (MCP)
    ↓
server.py (Infrastructure)
    ↓
SessionManager (Domain Service)
    ↓ injected into
ToolRegistry (Application Service)
    ↓ discovers and instantiates
Tool Implementations (Interface Layer)
    ↓ use
SessionManager methods
    ↓ manage
Domain Entities (Sessions)
    ↓ interact with
External Systems (tmux, ssh, sockets, etc.)
```

---

## Design Patterns

### 1. Dependency Injection
**Implementation:** Constructor injection throughout

**Benefits:**
- No global state
- Testable (can mock dependencies)
- Flexible (can swap implementations)
- Clear dependency graph

See [Dependency Injection](./dependency-injection.md) for details.

### 2. Factory Pattern
**Implementation:** ToolRegistry creates tool instances

**Benefits:**
- Centralized tool creation
- Consistent DI across all tools
- Dynamic plugin loading

### 3. Repository Pattern (implicit)
**Implementation:** SessionManager manages session entities

**Benefits:**
- Encapsulates session storage
- Provides clean API for session access

### 4. Plugin Architecture
**Implementation:** Dynamic discovery via filesystem scanning

**Benefits:**
- Extensible (add new tools without modifying core)
- Organized by category
- Self-documenting (tool metadata)

---

## Key Architectural Decisions

See [Architecture Decision Records (ADR)](./adr/) for detailed rationale:

- **[ADR-001](./adr/001-domain-driven-design.md)** - Adopt Domain-Driven Design
- **[ADR-002](./adr/002-tmux-integration.md)** - Integrate Tmux Multi-Session Support

---

## Domain Model

### Core Concepts

**Session:** A connection or process managed by PTY MCP
- PTY Session - Pseudo-terminal (interactive)
- Process Session - Subprocess (non-interactive)
- Socket Session - Network connection
- Serial Session - Hardware serial port
- Tmux Session - Named persistent session

**Tool:** An executable capability exposed via MCP
- Implements BaseTool interface
- Receives SessionManager via DI
- Returns ToolResult

**SessionManager:** Coordinates all sessions
- Domain Service
- Manages session lifecycle
- Provides session access to tools

---

## Testing Strategy

### Test Organization
```
tests/
├── unit/          # Isolated component tests
│   ├── domain/    # Test core/sessions entities
│   ├── application/  # Test lib/* services
│   └── tools/     # Test individual plugins
├── integration/   # Component interaction tests
└── functional/    # End-to-end workflow tests
```

See [Testing Guide](../../tests/README.md) for details.

---

## Future Improvements

### Planned Enhancements

1. **Extract Infrastructure Layer**
   - Move `server.py` to `infrastructure/mcp/`
   - Abstract file I/O to `infrastructure/filesystem/`
   - Extract process management to `infrastructure/processes/`

2. **Clarify Naming**
   - Consider renaming `lib/` → `application/`
   - Consider renaming `core/` → `domain/`
   - Document current naming rationale

3. **Add Explicit Use Cases**
   - Create `application/use_cases/` directory
   - Implement explicit use case classes
   - Separate orchestration from ToolRegistry

4. **Domain Events** (optional)
   - Publish events on session lifecycle changes
   - Enable loose coupling between components

---

## Related Documentation

- **[Dependency Injection](./dependency-injection.md)** - DI patterns and implementation
- **[ADR Index](./adr/)** - Architecture decisions and rationale
- **[Testing Guide](../../tests/README.md)** - Test structure and guidelines
- **[Features](../features/)** - Feature-specific documentation

---

## Resources

- [Domain-Driven Design (DDD)](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Dependency Injection](https://martinfowler.com/articles/injection.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
