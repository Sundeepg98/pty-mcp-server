#!/bin/bash
# PTY MCP Server Launch Script with proper MCP SDK

# Source user profile for proper environment
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

if [ -f ~/.profile ]; then
    source ~/.profile
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Ensure proper PATH for python3 and pip
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Ensure requirements are installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "[INFO] Installing MCP SDK..." >&2
    pip install --user -q -r requirements.txt
fi

# Run the server with unbuffered output
exec python3 -u main.py