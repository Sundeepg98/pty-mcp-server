# PTY MCP Server

A secure Model Context Protocol (MCP) server providing terminal, process, network, and serial communication capabilities for AI assistants.

## ✨ Features

- **🖥️ Terminal Operations**: PTY sessions, SSH, Telnet
- **⚙️ Process Management**: Spawn and control processes  
- **🌐 Network Tools**: TCP/UDP sockets, messaging
- **📡 Serial Communication**: RS232/USB serial device control
- **🔧 System Utilities**: File operations, environment management
- **🔒 Security**: Removed dangerous exec tool, all operations sandboxed

## 📦 Installation

### Via PyPI (Recommended)
```bash
pip install pty-mcp-server
```

### Using UV Tools
```bash
uv tool install pty-mcp-server
```

### From Source
```bash
git clone https://github.com/yourusername/pty-mcp-python
cd pty-mcp-python
uv tool install .
```

## 🚀 Quick Start

### Configure with Claude
Add to your Claude configuration (`~/.claude.json`):

```json
{
  "mcp_servers": {
    "pty": {
      "command": "pty-mcp-server"
    }
  }
}
```

### Test Installation
```bash
# Verify server responds
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | pty-mcp-server
```

## 🛠️ Available Tools (31)

### System Tools (6)
- `env` - Environment variable management
- `file` - File operations (read/write/list/delete)
- `status` - Get session status
- `activate` - Activate a project
- `projects` - List registered projects
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

## 📚 Usage Examples

### Terminal Operations
```python
# Start bash session
bash()
send(message="ls -la")
send(message="echo 'Hello World'")
disconnect()

# SSH connection
ssh(host="server.example.com", user="admin")
send(message="uptime")
disconnect()
```

### Process Management
```python
# Spawn a Python script
spawn(command="python", args=["script.py"])
send-proc(message="input data\n")
kill-proc()

# Run SSH command
ssh-proc(host="server.example.com", command="df -h")
```

### Network Operations
```python
# HTTP request
socket-open(host="example.com", port=80)
socket-write(data="GET / HTTP/1.0\r\n\r\n")
socket-read()
socket-close()

# Telnet session
socket-telnet(host="telnet.example.com")
socket-message(message="help")
socket-close()
```

### Serial Communication
```python
# Arduino/Microcontroller
serial-open(device="/dev/ttyUSB0", baudrate=9600)
serial-message(message="AT")
serial-read()
serial-close()
```

## 🏗️ Architecture

### Clean Separation (Dependency Injection)
```
pty_mcp_server/
├── core/          → Domain Logic
│   ├── manager.py → Session coordinator
│   └── sessions/  → Connection types
├── lib/           → Infrastructure
│   ├── config.py  → Configuration
│   └── registry.py → Plugin loader
└── plugins/       → MCP Tools
    ├── system/    → System utilities
    ├── terminal/  → Terminal operations
    ├── process/   → Process management
    ├── network/   → Network operations
    └── serial/    → Serial communication
```

## ⚙️ Configuration

### Environment Variables
- `PTY_MCP_BASE_DIR` - Base directory for config/state
- `PTY_DEFAULT_TIMEOUT` - Read timeout in seconds (default: 0.5)
- `PTY_MAX_BUFFER` - Max buffer size (default: 4096)

### Project Management
Projects can be registered with their own environments:

```json
{
  "projects": {
    "myproject": "/path/to/project"
  }
}
```

Each project can have a `.env` file that's loaded when activated:
```bash
activate(project_name="myproject")
# Now project-specific environment is available
```

## 🔄 Migration from v3.x

### Breaking Changes
- Removed dangerous `exec` tool
- Changed from source-based to package installation
- Configuration moved to XDG-compliant paths

### Upgrade Steps
1. Uninstall old version
2. Install v4.0.0: `pip install pty-mcp-server`
3. Update Claude configuration to use `pty-mcp-server` command
4. Migrate any custom project configurations

## 📋 Requirements

- Python 3.8+
- Linux/macOS/WSL
- Optional: `pyserial` for serial communication

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🔖 Version History

- **v4.0.0** - Package distribution, removed exec tool, 31 secure tools
- **v3.1.0** - Added dynamic environment loading
- **v3.0.0** - MCP SDK integration
- **v2.0.0** - Plugin architecture
- **v1.0.0** - Initial release

## 🔗 Links

- [GitHub Repository](https://github.com/yourusername/pty-mcp-python)
- [PyPI Package](https://pypi.org/project/pty-mcp-server/)
- [MCP Documentation](https://modelcontextprotocol.org)

---

**Security Note**: This server is designed for local development use with AI assistants. Never expose it to untrusted networks or use in production without proper security measures.