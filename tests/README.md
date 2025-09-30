# Test Suite

## Current Status
This folder is a placeholder for the future test suite. The development/debugging scripts that were here have been removed from version control as they contained hard-coded paths and weren't proper unit tests.

## Testing the Package

### Quick Test
To verify the server is working:
```bash
# Test server initialization
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | pty-mcp-server

# Test with Python
python3 -c "from pty_mcp_server import run; print('✅ Package imports successfully')"
```

### Manual Testing
```python
# Start the server and test tools manually
import subprocess
import json

proc = subprocess.Popen(
    ['pty-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send initialization
init_request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "0.1.0",
        "capabilities": {}
    },
    "id": 1
}
proc.stdin.write(json.dumps(init_request) + '\n')
proc.stdin.flush()
```

## Future Test Suite
A proper test suite should include:

1. **Unit Tests** (`test_unit_*.py`)
   - Test individual functions and classes
   - Mock external dependencies
   - Use pytest or unittest

2. **Integration Tests** (`test_integration_*.py`)
   - Test tool execution
   - Test session management
   - Test plugin loading

3. **End-to-End Tests** (`test_e2e_*.py`)
   - Test full MCP protocol flow
   - Test all 31 tools

## Contributing
When adding tests, please:
1. Use pytest framework
2. Follow naming convention: `test_*.py`
3. Include docstrings
4. Mock external resources
5. Ensure tests are portable (no hard-coded paths)