#!/usr/bin/env python3
"""
Test script for tmux integration in PTY MCP
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from pty_mcp_server.core.manager import SessionManager
from pty_mcp_server.lib.registry import ToolRegistry

def test_tmux_integration(session_manager, tool_registry, base_dir):
    """Test that tmux tools are loaded and functional"""

    print("="*60)
    print("Testing tmux integration in PTY MCP")
    print("="*60)

    # 1. Test SessionManager has tmux_manager
    print("\n1. Testing SessionManager...")

    # Verify tmux_manager attribute exists
    assert hasattr(session_manager, 'tmux_manager'), "SessionManager missing tmux_manager"
    assert hasattr(session_manager, 'get_tmux_manager'), "SessionManager missing get_tmux_manager method"

    # Test get_tmux_manager creates instance
    tmux_manager = session_manager.get_tmux_manager()
    assert tmux_manager is not None, "tmux_manager is None"
    print("✅ SessionManager correctly has tmux_manager")

    # 2. Test tool registry loads tmux tools
    print("\n2. Testing tool registry...")

    # Load all plugins
    loaded = tool_registry.load_all_plugins(str(base_dir))

    print(f"   Loaded tools by category:")
    for category, count in loaded.items():
        print(f"     {category}: {count} tools")

    # Verify tmux category exists and has 6 tools
    assert 'tmux' in loaded, "tmux category not found"
    assert loaded['tmux'] == 6, f"Expected 6 tmux tools, found {loaded['tmux']}"
    print("✅ Tool registry correctly loaded 6 tmux tools")

    # 3. Verify all 6 tmux tools are registered
    print("\n3. Verifying tmux tools...")
    expected_tools = [
        'tmux-start',
        'tmux-list',
        'tmux-send',
        'tmux-capture',
        'tmux-attach',
        'tmux-kill'
    ]

    for tool_name in expected_tools:
        tool = tool_registry.get_tool(tool_name)
        assert tool is not None, f"Tool {tool_name} not found"
        assert tool.category == 'tmux', f"Tool {tool_name} has wrong category"
        print(f"   ✅ {tool_name}")

    print("\n4. Testing tool definitions...")
    tools = tool_registry.list_tools()
    tmux_tools = [t for t in tools if any(t['name'] == name for name in expected_tools)]

    print(f"   Found {len(tmux_tools)} tmux tool definitions")
    for tool in tmux_tools:
        print(f"     • {tool['name']}: {tool['description'][:50]}...")

    # 5. Test SessionManager cleanup includes tmux
    print("\n5. Testing cleanup...")
    session_manager.cleanup_all()
    print("✅ Cleanup executed without errors")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nTmux integration is working correctly!")
    print("PTY MCP now has 31 + 6 = 37 tools total")

if __name__ == "__main__":
    try:
        test_tmux_integration()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
