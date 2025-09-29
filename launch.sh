#!/bin/bash
# PTY MCP Server Launch Script with proper MCP SDK

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Ensure requirements are installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "[INFO] Installing MCP SDK..." >&2
    pip install -q -r requirements.txt
fi

# Run the server
exec python3 main.py