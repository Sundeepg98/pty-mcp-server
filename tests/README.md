# Test Suite

## ⚠️ Note
These test files were created during development and need updating:
- Some reference the removed `exec` tool
- Paths are hard-coded to developer environment
- Import structures need updating for package format

## Running Tests

For basic functionality testing:
```bash
# Test server initialization
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | pty-mcp-server

# Test with Python
python3 -c "from pty_mcp_server import run; print('Entry point OK')"
```

## TODO
- [ ] Update tests to use proper package imports
- [ ] Remove references to exec tool
- [ ] Use dynamic paths instead of hard-coded ones
- [ ] Add proper unit tests with pytest