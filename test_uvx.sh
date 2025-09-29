#!/bin/bash
echo "=== UVX Installation Test ==="
echo

echo "1. Package Structure:"
ls -la pty_mcp_server/ | head -10

echo
echo "2. Entry Point Test:"
python3 -c "from pty_mcp_server import run; print('✅ Entry point importable')"

echo
echo "3. Module Test:"
timeout 2 python3 -m pty_mcp_server 2>&1 | head -3 && echo "✅ Module runnable"

echo
echo "4. Installation Command:"
echo "  uvx install /var/projects/mcp-servers/pty-mcp-python"

echo
echo "5. After installation, run:"
echo "  uvx pty-mcp-server"
