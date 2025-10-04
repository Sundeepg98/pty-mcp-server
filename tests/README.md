# Test Suite

## Structure

```
tests/
├── conftest.py         # Pytest configuration and shared fixtures
├── unit/               # Unit tests (isolated, mocked dependencies)
│   ├── domain/         # Tests for core/sessions (domain entities)
│   ├── application/    # Tests for lib/* (application services)
│   └── tools/          # Tests for individual tool implementations
├── integration/        # Integration tests (multiple components)
├── functional/         # End-to-end tests (full workflows)
└── fixtures/           # Shared test data and helpers
```

## Running Tests

### All tests:
```bash
pytest tests/
```

### Specific category:
```bash
pytest tests/unit/          # Fast unit tests
pytest tests/integration/   # Integration tests
pytest tests/functional/    # Slower functional tests
```

### With coverage:
```bash
pytest tests/ --cov=pty_mcp_server --cov-report=html
```

### Verbose output:
```bash
pytest tests/ -v
```

## Current Tests

### Integration Tests
- `test_tmux_integration.py` - Verifies tmux plugin loading and SessionManager integration

### Functional Tests
- `test_tmux_functional.py` - Tests real tmux operations (start, send, capture, kill)

## Test Guidelines

### 1. Unit Tests - Test single classes/functions
**Purpose:** Isolated testing of individual components

**Characteristics:**
- Mock external dependencies
- Fast execution (<1s per test)
- Use fixtures from conftest.py
- Test one thing at a time

**Example:**
```python
def test_session_manager_has_tmux_manager(session_manager):
    """Test SessionManager has tmux_manager attribute"""
    assert hasattr(session_manager, 'tmux_manager')
    assert hasattr(session_manager, 'get_tmux_manager')
```

**Location:** `tests/unit/{domain|application|tools}/`

---

### 2. Integration Tests - Test component interactions
**Purpose:** Verify multiple components work together

**Characteristics:**
- Test plugin loading
- Test session manager with real sessions
- Verify DI works end-to-end
- May use real dependencies (files, etc.)

**Example:**
```python
def test_plugin_loading(tool_registry, base_dir):
    """Test that all plugins load correctly"""
    loaded = tool_registry.load_all_plugins(str(base_dir))
    assert 'tmux' in loaded
    assert loaded['tmux'] == 6
```

**Location:** `tests/integration/`

---

### 3. Functional Tests - Test real workflows
**Purpose:** End-to-end testing of complete use cases

**Characteristics:**
- Use actual external systems (tmux, ssh, etc.)
- May be slower (seconds per test)
- Test full user workflows
- Verify real-world scenarios

**Example:**
```python
def test_tmux_workflow(tool_registry):
    """Test complete tmux session lifecycle"""
    # Start session
    result = tool_registry.execute("tmux-start", {...})
    assert "Started tmux session" in result["content"][0]["text"]

    # Send command
    result = tool_registry.execute("tmux-send", {...})

    # Capture output
    result = tool_registry.execute("tmux-capture", {...})

    # Kill session
    result = tool_registry.execute("tmux-kill", {...})
```

**Location:** `tests/functional/`

---

## Writing New Tests

### Use Fixtures (conftest.py)

Available fixtures:
- `session_manager` - Provides SessionManager instance
- `tool_registry` - Provides ToolRegistry instance
- `base_dir` - Provides path to pty_mcp_server/ for plugin loading

**Example:**
```python
def test_my_feature(session_manager, tool_registry):
    # Use fixtures directly
    assert session_manager is not None
```

### Follow Naming Conventions

- File names: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Test Organization

```python
# tests/unit/domain/test_session_manager.py
class TestSessionManager:
    def test_initialization(self, session_manager):
        """Test SessionManager initializes correctly"""
        pass

    def test_get_tmux_manager(self, session_manager):
        """Test get_tmux_manager creates TmuxSessionManager"""
        pass
```

### Use Descriptive Names

Good:
```python
def test_tmux_manager_starts_session_with_valid_name():
    pass
```

Bad:
```python
def test_tmux():
    pass
```

## Dependencies

Required for testing:
```bash
pip install pytest pytest-cov
```

Optional but recommended:
```bash
pip install pytest-asyncio  # For async tests
pip install pytest-mock     # For mocking helpers
```

## Continuous Integration

Tests should:
1. Run on every commit
2. Pass before merging
3. Maintain >80% code coverage
4. Execute in <5 minutes (ideal)

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Add unit tests** for new classes/functions
3. **Add integration tests** if multiple components interact
4. **Add functional tests** for new user-facing features
5. **Update this README** if adding new test categories

## Test Data

Place test fixtures in `tests/fixtures/`:
- Sample configurations
- Mock responses
- Test session data

## Troubleshooting

### Tests not found
```bash
# Ensure project is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Import errors
```bash
# Install package in editable mode
pip install -e .
```

### Cleanup after tests
Some tests (functional) may leave processes running:
```bash
# Kill tmux sessions
tmux kill-server

# Check for orphaned processes
ps aux | grep pty-mcp
```

## Future Improvements

- [ ] Add unit tests for all domain entities
- [ ] Add unit tests for all tools
- [ ] Add integration tests for all plugin categories
- [ ] Achieve >90% code coverage
- [ ] Add performance benchmarks
- [ ] Add CI/CD pipeline configuration
