#!/bin/bash
# Quick test of pty-uvx server

echo "Testing PTY-UVX Server..."
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | timeout 2 /home/sundeep/.local/bin/pty-mcp-server 2>&1 | head -5