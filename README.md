# PTY MCP Server

A Model Context Protocol (MCP) server providing 32 tools for terminal, process, network, and serial communication with perfect dependency injection architecture.

## Architecture

### Clean Separation (10/10 DI Score)

```
/core/          → Domain Logic (Business Entities)
  manager.py    → Central session coordinator
  sessions/     → Connection types
    pty.py      → PTY (pseudo-terminal) sessions
    process.py  → Process management
    socket.py   → Network connections
    serial.py   → Serial port communication

/lib/           → Infrastructure (Utilities)
  config.py     → Configuration management (injected INTO core)
  registry.py   → Tool registry and plugin loader
  base.py       → Base abstractions for tools

/plugins/       → Extensions (MCP Tools)
  system/       → System utilities (7 tools)
  terminal/     → Terminal operations (8 tools)
  process/      → Process management (6 tools)
  network/      → Network operations (6 tools)
  serial/       → Serial communication (5 tools)
```

### Dependency Flow
```
main.py
  ├→ /core/manager.py (receives injected config)
  │    └→ /core/sessions/* (domain entities)
  └→ /lib/config.py (configuration)
     /lib/registry.py (tool management)
```

### Key Principles
- **Dependency Injection**: Config created in main, injected into core
- **Inward Dependencies**: main→core→lib, never lib→core
- **Single Responsibility**: Each file has one clear purpose
- **No Circular Dependencies**: Clean unidirectional flow
- **Testable**: Easy to mock dependencies for testing

## Features

- **Session Management**: Only one active session per type (PTY/Process/Socket/Serial)
- **Cross-Platform**: Works on Linux/Mac/WSL, Windows CMD accessible via WSL
- **Clean Output**: Terminal escape sequences automatically filtered
- **Project Support**: Switch between projects with saved state
- **Dynamic Environment**: Project-specific .env files automatically loaded for exec commands
- **Error Handling**: Graceful degradation for missing features

## Available Tools (32)

### System Tools (7)
- `env` - Environment variable management
- `file` - File operations (read/write/list/delete)
- `status` - Get session status
- `activate` - Activate a project
- `projects` - List registered projects
- `exec` - Execute shell commands
- `sessions` - List all active sessions

### Terminal Tools (8)
- `bash` - Start interactive bash shell
- `connect` - Connect to PTY with custom command
- `disconnect` - Terminate PTY session
- `send` - Send input to PTY
- `ssh` - SSH connection via PTY
- `telnet` - Telnet connection via PTY
- `clear` - Clear terminal screen
- `resize` - Resize terminal dimensions

### Process Tools (6)
- `spawn` - Spawn a process (non-PTY)
- `kill-proc` - Kill active process
- `send-proc` - Send to process stdin
- `ssh-proc` - SSH as subprocess
- `proc-cmd` - Windows CMD (Windows only)
- `proc-ps` - Windows PowerShell (Windows only)

### Network Tools (6)
- `socket-open` - Open TCP/UDP socket
- `socket-close` - Close socket connection
- `socket-read` - Read from socket
- `socket-write` - Write to socket
- `socket-message` - Send message, wait for response
- `socket-telnet` - Telnet with IAC handling

### Serial Tools (5)
- `serial-open` - Open serial port
- `serial-close` - Close serial connection
- `serial-read` - Read from serial port
- `serial-write` - Write to serial port
- `serial-message` - Send message, wait for response

## Installation

### Via Claude CLI
```bash
# Already configured in ~/.claude.json
claude mcp list  # Should show pty server
```

### Manual Setup
```bash
cd ~/.claude/mcp/pty
python3 main.py  # For testing
```

## Usage Examples

### Basic Commands
```python
# Execute a shell command
mcp__pty__exec(command="ls -la")

# Start bash session
mcp__pty__bash()
mcp__pty__send(message="echo 'Hello World'")
mcp__pty__disconnect()

# Process spawning
mcp__pty__spawn(command="python", args=["script.py"])
mcp__pty__kill-proc()
```

### Windows Integration (via WSL)
```python
# Access Windows CMD from WSL
mcp__pty__bash(working_dir="/mnt/c")
mcp__pty__send(message="cmd.exe /c 'dir'")
```

### Network Operations
```python
# TCP connection
mcp__pty__socket-open(host="example.com", port=80)
mcp__pty__socket-write(data="GET / HTTP/1.0\r\n\r\n")
mcp__pty__socket-read()
mcp__pty__socket-close()
```

### Serial Communication
```python
# Serial port (requires pyserial)
mcp__pty__serial-open(device="/dev/ttyUSB0", baudrate=9600)
mcp__pty__serial-message(message="AT")
mcp__pty__serial-close()
```

### Dynamic Environment (Project-Specific)
```python
# Activate project with .env file
mcp__pty__activate(project_name="ics")
# Project's .env file automatically loaded

# Exec commands use project environment
mcp__pty__exec(command="echo $DATABASE_URL")  
# Returns: postgresql://ics_user:password@localhost:5432/ics_db

# Switch to different project
mcp__pty__activate(project_name="memory-service")
mcp__pty__exec(command="echo $DATABASE_URL")
# Returns: postgresql://memory@localhost/memory_db

# Note: PTY/bash sessions maintain global environment (by design)
mcp__pty__bash()  # Uses system environment, not project .env
```

## Configuration

Configuration is managed via environment variables or `config/projects.json`:

```json
{
  "projects": {
    "ics": "/var/projects/ICS",
    "pty-mcp": "/home/sundeep/.claude/mcp/pty"
  }
}
```

### Project Environment Files

Each project can have a `.env` file in its root directory that will be automatically loaded when the project is activated:

```bash
# /var/projects/ICS/.env
DATABASE_URL=postgresql://ics_user:password@localhost:5432/ics_db
ICS_PROJECT_VAR=ICS_SPECIFIC_VALUE
API_KEY=secret-key-123
```

When a project is activated:
1. The `.env` file is loaded into memory
2. `exec` commands receive the merged environment (system + project)
3. PTY/bash sessions keep the global environment (architectural constraint)
4. Switching projects automatically loads the new project's environment

Environment variables:
- `PTY_MCP_BASE_DIR` - Base directory (default: ~/.claude/mcp/pty)
- `PTY_DEFAULT_TIMEOUT` - Read timeout in seconds (default: 0.5)
- `PTY_MAX_BUFFER` - Max buffer size (default: 4096)

## Technical Details

### Session Types
- **PTYSession**: Full terminal emulation with escape sequence filtering
- **ProcessSession**: Simple process management without PTY
- **SocketSession**: TCP/UDP network connections
- **SerialSession**: Serial port communication

### Clean Architecture Benefits
1. **Testability**: Mock config for unit tests
2. **Maintainability**: Clear separation of concerns
3. **Scalability**: Easy to add new session types
4. **Flexibility**: Swap implementations without changing core

### Error Handling
- All tools return standardized `ToolResult` objects
- Errors are properly propagated with descriptive messages
- Sessions auto-cleanup on termination

## Requirements

- Python 3.8+
- Linux/Mac/WSL
- Optional: `pyserial` for serial communication

## Development

### Running Tests
```bash
cd ~/.claude/mcp/pty
python3 -c "import main; server = main.MCPServer(); print(f'{len(server.registry)} tools loaded')"
```

### Adding New Tools
1. Create tool class in appropriate plugin directory
2. Inherit from `BaseTool`
3. Implement required properties and `execute()` method
4. Tool auto-registers on server start

## Version

3.1.0 - Added dynamic project-specific environment loading for exec commands

## License

Private project for Claude Code integration.