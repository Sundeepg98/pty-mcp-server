# Dependency Injection Patterns

PTY MCP Server implements **100% constructor-based dependency injection**. This document explains the patterns and implementation.

---

## Overview

### What is Dependency Injection?

**Dependency Injection (DI)** is a design pattern where dependencies are provided to objects rather than created by them.

**Benefits:**
- ✅ Testable - Can mock dependencies
- ✅ Flexible - Can swap implementations
- ✅ Clear - Dependencies are explicit
- ✅ No globals - No hidden state

---

## Core DI Pattern

### 1. Interface Definition (`lib/base.py`)

```python
class BaseTool(ABC):
    """Abstract base for all tools - defines dependency"""

    def __init__(self, session_manager=None):
        """Dependency injected via constructor"""
        self.session_manager = session_manager

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Tools implement this method"""
        pass
```

**Key Points:**
- Constructor accepts `session_manager` parameter
- Stored as instance variable
- Optional (default `None`) for flexibility

---

### 2. Concrete Implementation (`plugins/*/*`)

```python
class TmuxStartTool(BaseTool):
    """Concrete tool implementation"""

    def __init__(self, session_manager=None):
        """Accept and pass dependency to base class"""
        super().__init__(session_manager)

    def execute(self, arguments):
        """Use injected dependency"""
        # Access the injected SessionManager:
        tmux_manager = self.session_manager.get_tmux_manager()

        # Use the manager:
        result = tmux_manager.start_session(
            arguments['session_name'],
            arguments['command']
        )

        return ToolResult(...)
```

**Key Points:**
- Calls `super().__init__(session_manager)` to inject dependency
- Uses `self.session_manager` throughout `execute()`
- No direct instantiation of dependencies

---

### 3. Factory/Registry (`lib/registry.py`)

```python
class ToolRegistry:
    """Factory for creating tools with dependencies injected"""

    def __init__(self, session_manager=None):
        """Registry receives the dependency to inject"""
        self.session_manager = session_manager
        self.tools = {}

    def _instantiate_tool(self, tool_class: Type[BaseTool]) -> BaseTool:
        """Create tool instance with dependency injection"""
        return tool_class(self.session_manager)  # ← Injection happens here

    def load_all_plugins(self, base_dir: str):
        """Discover and instantiate all tools"""
        # ... discover tool classes ...
        for tool_class in discovered_classes:
            tool_instance = self._instantiate_tool(tool_class)  # DI
            self.tools[tool_instance.name] = tool_instance
```

**Key Points:**
- Registry holds the `session_manager` to inject
- All tools created via `_instantiate_tool()` get the same instance
- Centralized dependency injection point

---

### 4. Application Bootstrap (`server.py`)

```python
# Create the dependency (root of dependency graph)
session_manager = SessionManager()

# Create the registry with the dependency
tool_registry = ToolRegistry(session_manager)

# Registry discovers and instantiates all tools with DI
base_dir = Path(__file__).parent / "pty_mcp_server"
tool_registry.load_all_plugins(str(base_dir))

# Now all tools have access to session_manager via DI
```

**Key Points:**
- `SessionManager` created first (root dependency)
- Injected into `ToolRegistry`
- Registry propagates to all tools
- Single instance shared by all tools

---

## Dependency Graph

```
server.py
    ↓ creates
SessionManager (domain service)
    ↓ injects into
ToolRegistry (application service)
    ↓ discovers & injects into
37 Tool implementations (interface layer)
    ↓ use methods of
SessionManager
    ↓ manage
Session entities (PTY, Process, Socket, Serial, Tmux)
```

**Direction:** Dependencies flow inward (toward domain)

---

## DI in Practice

### Example: Tmux Tool Chain

```python
# 1. server.py creates root dependency
session_manager = SessionManager()

# 2. Registry receives dependency
tool_registry = ToolRegistry(session_manager)

# 3. Registry loads plugins (with DI)
tool_registry.load_all_plugins("pty_mcp_server")

# 4. Tool executes - uses injected dependency
result = tool_registry.execute("tmux-start", {
    "session_name": "dev",
    "command": "npm run dev"
})

# 5. Inside TmuxStartTool.execute():
#    tmux_manager = self.session_manager.get_tmux_manager()
#    tmux_manager.start_session(...)
```

**Flow:**
1. Dependency created once
2. Injected into registry
3. Registry injects into tools during loading
4. Tools use dependency during execution

---

## Advanced Patterns

### Lazy Initialization

SessionManager uses **lazy initialization** for optional managers:

```python
class SessionManager:
    def __init__(self):
        self.tmux_manager: Optional[TmuxSessionManager] = None

    def get_tmux_manager(self) -> TmuxSessionManager:
        """Create on first access (lazy)"""
        if not self.tmux_manager:
            self.tmux_manager = TmuxSessionManager()
        return self.tmux_manager
```

**Benefits:**
- Only create managers when needed
- Reduces startup overhead
- Still injectable (via SessionManager)

---

### Service Locator (Avoided)

**We do NOT use Service Locator pattern:**

```python
# ❌ BAD: Service Locator (global registry)
class ServiceLocator:
    _services = {}

    @classmethod
    def get(cls, name):
        return cls._services[name]

# Tools would do:
session_manager = ServiceLocator.get('session_manager')  # Hidden dependency!
```

**Why avoided:**
- Hidden dependencies (not in constructor)
- Hard to test (global state)
- Tight coupling to ServiceLocator

**Our approach (Constructor Injection):**
```python
# ✅ GOOD: Constructor Injection (explicit)
class TmuxStartTool(BaseTool):
    def __init__(self, session_manager=None):  # Explicit dependency
        self.session_manager = session_manager
```

---

## Testing with DI

### Unit Testing

DI makes testing easy - just inject mocks:

```python
import pytest
from unittest.mock import Mock

def test_tmux_start_tool():
    # Create mock dependency
    mock_manager = Mock()
    mock_tmux = Mock()
    mock_manager.get_tmux_manager.return_value = mock_tmux

    # Inject mock via constructor
    tool = TmuxStartTool(session_manager=mock_manager)

    # Execute tool
    result = tool.execute({
        "session_name": "test",
        "command": "echo hello"
    })

    # Verify tool used the dependency correctly
    mock_manager.get_tmux_manager.assert_called_once()
    mock_tmux.start_session.assert_called_once_with("test", "echo hello")
```

**Benefits:**
- No global state to clean up
- Can test tools in isolation
- Can verify dependency interactions

---

### Integration Testing

Use real dependencies to test integration:

```python
def test_tool_registry_integration():
    # Create real dependencies
    session_manager = SessionManager()
    tool_registry = ToolRegistry(session_manager)

    # Load plugins
    base_dir = Path(__file__).parent.parent / "pty_mcp_server"
    loaded = tool_registry.load_all_plugins(str(base_dir))

    # Verify DI worked
    assert 'tmux' in loaded
    assert loaded['tmux'] == 6

    # Verify tools can access session_manager
    tool = tool_registry.get_tool('tmux-start')
    assert tool.session_manager is session_manager  # Same instance!
```

---

## Anti-Patterns Avoided

### ❌ 1. Singletons

```python
# ❌ BAD: Singleton pattern
class SessionManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = SessionManager()
        return cls._instance

# Tools would do:
session_manager = SessionManager.get_instance()  # Global state!
```

**Why avoided:**
- Global state (hard to test)
- Cannot have multiple instances
- Hidden dependencies

**Our approach:**
```python
# ✅ GOOD: Created once, injected everywhere
session_manager = SessionManager()  # Explicit creation
tool = TmuxStartTool(session_manager)  # Explicit injection
```

---

### ❌ 2. Direct Instantiation

```python
# ❌ BAD: Tool creates its own dependency
class TmuxStartTool(BaseTool):
    def __init__(self):
        self.session_manager = SessionManager()  # Creates dependency!
```

**Why avoided:**
- Hard to test (can't inject mock)
- Tight coupling (knows how to create SessionManager)
- Hidden dependency

**Our approach:**
```python
# ✅ GOOD: Dependency injected
class TmuxStartTool(BaseTool):
    def __init__(self, session_manager=None):
        self.session_manager = session_manager  # Receives dependency
```

---

### ❌ 3. Global Variables

```python
# ❌ BAD: Global session manager
SESSION_MANAGER = SessionManager()

class TmuxStartTool(BaseTool):
    def execute(self, arguments):
        global SESSION_MANAGER
        manager = SESSION_MANAGER.get_tmux_manager()  # Uses global!
```

**Why avoided:**
- Global state (shared across tests)
- Implicit dependency
- Hard to swap implementations

---

## Benefits Realized

### ✅ 1. Testability
- Can inject mocks for unit tests
- Can inject real instances for integration tests
- No global state to manage

### ✅ 2. Flexibility
- Can swap SessionManager implementation
- Can use different managers for different tools
- Can create multiple independent instances

### ✅ 3. Clarity
- Dependencies explicit in constructors
- Easy to see what each class needs
- Clear dependency graph

### ✅ 4. Decoupling
- Tools don't know how to create SessionManager
- SessionManager doesn't know about tools
- Can evolve independently

---

## Summary

**PTY MCP's DI Implementation:**

1. **Pattern:** Constructor injection
2. **Scope:** 100% of codebase
3. **Root:** `SessionManager` created in `server.py`
4. **Propagation:** Via `ToolRegistry` to all tools
5. **Testing:** Easy to mock and test

**Key Principle:**
> Dependencies are injected, not created

This enables the flexible, testable, and maintainable architecture that makes PTY MCP extensible and reliable.

---

## Related Documentation

- **[Architecture Overview](./README.md)** - Overall system design
- **[Testing Guide](../../tests/README.md)** - How to test with DI
- **[ADR-001](./adr/001-domain-driven-design.md)** - Why we chose DDD + DI
