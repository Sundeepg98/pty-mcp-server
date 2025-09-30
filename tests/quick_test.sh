#!/bin/bash
# Quick test of PTY MCP server

echo "Testing PTY MCP Server..."
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | timeout 2 pty-mcp-server 2>&1 | head -5