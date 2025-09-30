#!/usr/bin/env python3
"""Test all 31 tools in pty-uvx MCP server package"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, List

def send_request(proc: subprocess.Popen, method: str, params: Dict[str, Any] = None, id_num: int = 1) -> Dict:
    """Send JSON-RPC request and get response"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "id": id_num
    }
    if params:
        request["params"] = params
    
    # Send request
    proc.stdin.write(json.dumps(request) + '\n')
    proc.stdin.flush()
    
    # Read response
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            response = json.loads(line)
            if response.get("id") == id_num:
                return response
        except json.JSONDecodeError:
            continue
    return None

def test_tool(proc: subprocess.Popen, tool_name: str, arguments: Dict[str, Any], test_num: int) -> bool:
    """Test a single tool"""
    print(f"  [{test_num:2d}] Testing {tool_name}...", end="")
    
    response = send_request(proc, "tools/call", {
        "name": tool_name,
        "arguments": arguments
    }, test_num)
    
    if response and "result" in response:
        print(" ✓")
        return True
    elif response and "error" in response:
        print(f" ✗ (Error: {response['error'].get('message', 'Unknown')})")
        return False
    else:
        print(" ✗ (No response)")
        return False

def main():
    print("=" * 60)
    print("PTY-UVX MCP Server Tool Test (31 tools)")
    print("=" * 60)
    
    # Start the server
    print("\nStarting pty-mcp-server...")
    proc = subprocess.Popen(
        ["/home/sundeep/.local/bin/pty-mcp-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait for initialization
    time.sleep(1)
    
    # Initialize the connection
    print("Initializing connection...")
    init_response = send_request(proc, "initialize", {
        "protocolVersion": "0.1.0",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }, 0)
    
    if not init_response:
        print("Failed to initialize!")
        proc.terminate()
        return 1
    
    print("Connected successfully!\n")
    
    # Define all 31 tools with test parameters
    tests = [
        # Session Management (2 tools)
        ("status", {"verbose": False}),
        ("sessions", {"format": "summary"}),
        
        # PTY Operations (6 tools)
        ("connect", {"command": "echo", "args": ["test"]}),
        ("send", {"message": "test"}),
        ("disconnect", {}),
        ("bash", {}),
        ("clear", {}),
        ("resize", {"width": 80, "height": 24}),
        
        # Process Operations (3 tools)
        ("spawn", {"command": "echo", "args": ["hello"]}),
        ("send-proc", {"message": "test"}),
        ("kill-proc", {}),
        
        # File Operations (1 tool with multiple actions = 5 operations)
        ("file", {"action": "exists", "path": "/tmp"}),
        ("file", {"action": "list", "path": "/tmp"}),
        ("file", {"action": "write", "path": "/tmp/test.txt", "content": "test"}),
        ("file", {"action": "read", "path": "/tmp/test.txt"}),
        ("file", {"action": "delete", "path": "/tmp/test.txt"}),
        
        # Environment Operations (1 tool with 4 actions)
        ("env", {"action": "get", "name": "PATH"}),
        ("env", {"action": "set", "name": "TEST_VAR", "value": "test"}),
        ("env", {"action": "list"}),
        ("env", {"action": "unset", "name": "TEST_VAR"}),
        
        # Project Management (2 tools)
        ("projects", {}),
        ("activate", {"project_name": "test-project"}),
        
        # Socket Operations (6 tools)
        ("socket-open", {"host": "127.0.0.1", "port": 8080}),
        ("socket-write", {"data": "test"}),
        ("socket-read", {}),
        ("socket-message", {"message": "test"}),
        ("socket-telnet", {"host": "127.0.0.1"}),
        ("socket-close", {}),
        
        # Serial Operations (5 tools)
        ("serial-open", {"device": "/dev/ttyUSB0"}),
        ("serial-write", {"data": "test"}),
        ("serial-read", {}),
        ("serial-message", {"message": "test"}),
        ("serial-close", {}),
        
        # SSH Operations (2 tools)
        ("ssh", {"host": "localhost"}),
        ("ssh-proc", {"host": "localhost", "command": "echo test"}),
        
        # Telnet (1 tool)
        ("telnet", {"host": "127.0.0.1"}),
        
        # Windows-specific (2 tools)
        ("proc-cmd", {}),
        ("proc-ps", {}),
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    print("Running tool tests:\n")
    for i, (tool, args) in enumerate(tests, 1):
        if test_tool(proc, tool, args, i):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"Total unique tools tested: 31")
    print("=" * 60)
    
    # Cleanup
    proc.terminate()
    proc.wait()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())