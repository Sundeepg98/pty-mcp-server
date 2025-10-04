#!/usr/bin/env python3
"""Direct test of pty-uvx MCP server tools"""

import json
import subprocess
import time

def test_server():
    print("Testing PTY-UVX MCP Server (v4.0.0)")
    print("="*50)
    
    # Start the server
    proc = subprocess.Popen(
        ['/home/sundeep/.local/bin/pty-mcp-server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Initialize
    init_req = {
        'jsonrpc': '2.0',
        'method': 'initialize',
        'params': {
            'protocolVersion': '0.1.0',
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'}
        },
        'id': 1
    }
    
    proc.stdin.write(json.dumps(init_req) + '\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Read initialization response
    init_response = proc.stdout.readline()
    try:
        init_data = json.loads(init_response)
        if 'result' in init_data:
            print(f"✅ Server initialized: v{init_data['result']['serverInfo']['version']}")
    except:
        print(f"❌ Init failed: {init_response}")
        proc.terminate()
        return
    
    # List tools
    list_req = {
        'jsonrpc': '2.0',
        'method': 'tools/list',
        'params': {},
        'id': 2
    }
    
    proc.stdin.write(json.dumps(list_req) + '\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    # Read tools response
    tools_response = proc.stdout.readline()
    try:
        tools_data = json.loads(tools_response)
        if 'result' in tools_data and 'tools' in tools_data['result']:
            tools = tools_data['result']['tools']
            print(f"✅ Tools loaded: {len(tools)}")
            
            # Group by category
            categories = {}
            for tool in tools:
                name = tool['name']
                # Guess category from tool name
                if name in ['connect', 'send', 'disconnect', 'bash', 'clear', 'resize', 'ssh', 'telnet']:
                    cat = 'terminal'
                elif name in ['spawn', 'send-proc', 'kill-proc', 'ssh-proc', 'proc-cmd', 'proc-ps']:
                    cat = 'process'
                elif name in ['socket-open', 'socket-write', 'socket-read', 'socket-message', 'socket-telnet', 'socket-close']:
                    cat = 'network'
                elif name in ['serial-open', 'serial-write', 'serial-read', 'serial-message', 'serial-close']:
                    cat = 'serial'
                elif name in ['status', 'sessions', 'file', 'env', 'projects', 'activate']:
                    cat = 'system'
                else:
                    cat = 'unknown'
                
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(name)
            
            # Print summary
            for cat in sorted(categories.keys()):
                print(f"  {cat}: {len(categories[cat])} tools")
                for tool in sorted(categories[cat])[:3]:
                    print(f"    - {tool}")
                if len(categories[cat]) > 3:
                    print(f"    ... and {len(categories[cat])-3} more")
        else:
            print(f"❌ No tools found in response")
            print(f"   Response: {tools_response}")
    except Exception as e:
        print(f"❌ Error parsing tools: {e}")
        print(f"   Response: {tools_response}")
    
    # Test a simple tool call
    print("\nTesting tool execution:")
    call_req = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'status',
            'arguments': {'verbose': False}
        },
        'id': 3
    }
    
    proc.stdin.write(json.dumps(call_req) + '\n')
    proc.stdin.flush()
    time.sleep(0.5)
    
    call_response = proc.stdout.readline()
    try:
        call_data = json.loads(call_response)
        if 'result' in call_data:
            print("✅ Tool executed successfully")
        elif 'error' in call_data:
            print(f"❌ Tool error: {call_data['error'].get('message', 'Unknown')}")
    except:
        print(f"❌ Invalid response: {call_response}")
    
    proc.terminate()
    print("\n" + "="*50)
    print("Test complete!")

if __name__ == "__main__":
    test_server()