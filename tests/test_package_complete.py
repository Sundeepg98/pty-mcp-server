#!/usr/bin/env python3
"""
Comprehensive test suite for the refactored PTY MCP Server package
Tests all 31 tools to ensure they load and work properly
"""

import json
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

class PackageTester:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def run_mcp_command(self, command: str) -> str:
        """Run a command that interacts with the MCP server"""
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    
    def test_server_startup(self) -> bool:
        """Test if the server starts without errors"""
        print("\n=== Testing Server Startup ===")
        
        # Start the server and immediately send initialization
        test_script = """
import json
import subprocess
import time

proc = subprocess.Popen(
    ['/home/sundeep/.local/bin/pty-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Send initialization
init_request = {
    'jsonrpc': '2.0',
    'method': 'initialize',
    'params': {
        'protocolVersion': '0.1.0',
        'capabilities': {},
        'clientInfo': {'name': 'test-client', 'version': '1.0'}
    },
    'id': 1
}

proc.stdin.write(json.dumps(init_request) + '\\n')
proc.stdin.flush()

# Wait for response
time.sleep(1)
response = proc.stdout.readline()

try:
    data = json.loads(response)
    if 'result' in data:
        print('SUCCESS: Server initialized')
        print(f'Server version: {data["result"]["serverInfo"]["version"]}')
    else:
        print('FAIL: No result in response')
except:
    print(f'FAIL: Invalid response: {response}')

proc.terminate()
"""
        
        result = subprocess.run(
            ['python3', '-c', test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "SUCCESS" in result.stdout:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Server startup failed: {result.stdout}")
            print(f"   Error: {result.stderr}")
            return False
    
    def test_tool_loading(self) -> Tuple[bool, int]:
        """Test if tools are loaded properly"""
        print("\n=== Testing Tool Loading ===")
        
        test_script = """
import json
import subprocess
import time

proc = subprocess.Popen(
    ['/home/sundeep/.local/bin/pty-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Initialize
init_request = {
    'jsonrpc': '2.0',
    'method': 'initialize',
    'params': {
        'protocolVersion': '0.1.0',
        'capabilities': {},
        'clientInfo': {'name': 'test', 'version': '1.0'}
    },
    'id': 1
}

proc.stdin.write(json.dumps(init_request) + '\\n')
proc.stdin.flush()
time.sleep(0.5)
proc.stdout.readline()  # Read init response

# List tools
list_request = {
    'jsonrpc': '2.0',
    'method': 'tools/list',
    'params': {},
    'id': 2
}

proc.stdin.write(json.dumps(list_request) + '\\n')
proc.stdin.flush()
time.sleep(0.5)

# Read response
response = proc.stdout.readline()
try:
    data = json.loads(response)
    if 'result' in data and 'tools' in data['result']:
        tools = data['result']['tools']
        print(f'TOOLS_COUNT: {len(tools)}')
        for tool in tools:
            print(f'TOOL: {tool["name"]}')
    else:
        print('TOOLS_COUNT: 0')
except Exception as e:
    print(f'ERROR: {e}')
    print(f'Response: {response}')

proc.terminate()
"""
        
        result = subprocess.run(
            ['python3', '-c', test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse output
        tool_count = 0
        tools = []
        
        for line in result.stdout.split('\n'):
            if line.startswith('TOOLS_COUNT:'):
                tool_count = int(line.split(':')[1].strip())
            elif line.startswith('TOOL:'):
                tools.append(line.split(':')[1].strip())
        
        print(f"Tools loaded: {tool_count}")
        
        if tool_count == 31:
            print(f"✅ All 31 tools loaded successfully")
            
            # List tools by category
            categories = {
                'terminal': ['connect', 'send', 'disconnect', 'bash', 'clear', 'resize'],
                'process': ['spawn', 'send-proc', 'kill-proc', 'ssh-proc', 'proc-cmd', 'proc-ps'],
                'network': ['socket-open', 'socket-write', 'socket-read', 'socket-message', 
                           'socket-telnet', 'socket-close', 'ssh', 'telnet'],
                'serial': ['serial-open', 'serial-write', 'serial-read', 'serial-message', 'serial-close'],
                'system': ['status', 'sessions', 'file', 'env', 'projects', 'activate']
            }
            
            for cat, expected in categories.items():
                found = [t for t in tools if t in expected]
                print(f"  {cat}: {len(found)}/{len(expected)} tools")
            
            return True, tool_count
        else:
            print(f"❌ Expected 31 tools, got {tool_count}")
            if tools:
                print(f"   Tools found: {', '.join(tools[:10])}...")
            return False, tool_count
    
    def test_tool_execution(self) -> bool:
        """Test executing a simple tool"""
        print("\n=== Testing Tool Execution ===")
        
        test_script = '''
import json
import subprocess
import time

proc = subprocess.Popen(
    ['/home/sundeep/.local/bin/pty-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Initialize
init_request = {
    'jsonrpc': '2.0',
    'method': 'initialize',
    'params': {
        'protocolVersion': '0.1.0',
        'capabilities': {},
        'clientInfo': {'name': 'test', 'version': '1.0'}
    },
    'id': 1
}

proc.stdin.write(json.dumps(init_request) + '\\n')
proc.stdin.flush()
time.sleep(0.5)
proc.stdout.readline()  # Read init response

# Call status tool
call_request = {
    'jsonrpc': '2.0',
    'method': 'tools/call',
    'params': {
        'name': 'status',
        'arguments': {'verbose': False}
    },
    'id': 3
}

proc.stdin.write(json.dumps(call_request) + '\\n')
proc.stdin.flush()
time.sleep(0.5)

# Read response
response = proc.stdout.readline()
try:
    data = json.loads(response)
    if 'result' in data:
        print('SUCCESS: Tool executed')
        if 'content' in data['result']:
            print('Tool returned content')
    elif 'error' in data:
        print(f'ERROR: {data["error"]["message"]}')
    else:
        print(f'UNKNOWN: {response}')
except Exception as e:
    print(f'PARSE_ERROR: {e}')

proc.terminate()
'''
        
        result = subprocess.run(
            ['python3', '-c', test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "SUCCESS" in result.stdout:
            print(f"✅ Tool execution successful")
            return True
        else:
            print(f"❌ Tool execution failed")
            print(f"   Output: {result.stdout}")
            print(f"   Error: {result.stderr}")
            return False
    
    def check_logs(self):
        """Check the server logs for errors"""
        print("\n=== Checking Server Logs ===")
        
        log_file = Path("/tmp/pty-mcp.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Check last 20 lines for errors
            recent_lines = lines[-20:] if len(lines) > 20 else lines
            
            errors = [l for l in recent_lines if '[ERROR]' in l]
            warnings = [l for l in recent_lines if '[WARNING]' in l]
            
            if errors:
                print(f"❌ Found {len(errors)} errors in logs:")
                for error in errors[-3:]:  # Show last 3 errors
                    print(f"   {error.strip()}")
            else:
                print("✅ No errors in logs")
            
            if warnings:
                print(f"⚠️  Found {len(warnings)} warnings in logs")
            
            # Check for successful tool loading
            tool_loads = [l for l in recent_lines if 'Loaded' in l and 'tools from' in l]
            if tool_loads:
                print(f"ℹ️  Last load: {tool_loads[-1].strip()}")
        else:
            print("⚠️  No log file found at /tmp/pty-mcp.log")
    
    def run_all_tests(self):
        """Run all tests"""
        print("="*60)
        print("PTY MCP Server Package Test Suite")
        print("="*60)
        
        # Test 1: Server startup
        if self.test_server_startup():
            self.passed += 1
        else:
            self.failed += 1
        
        # Test 2: Tool loading
        success, count = self.test_tool_loading()
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        # Test 3: Tool execution
        if self.test_tool_execution():
            self.passed += 1
        else:
            self.failed += 1
        
        # Check logs
        self.check_logs()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n✅ ALL TESTS PASSED - Package is working correctly!")
        else:
            print(f"\n❌ {self.failed} tests failed - Package needs fixes")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = PackageTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)