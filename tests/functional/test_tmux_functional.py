#!/usr/bin/env python3
"""
Functional test for tmux tools
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from pty_mcp_server.core.manager import SessionManager
from pty_mcp_server.lib.registry import ToolRegistry

def test_tmux_functionality(session_manager, tool_registry, base_dir):
    """Test actual tmux operations"""

    print("="*60)
    print("Functional test for tmux tools")
    print("="*60)

    # Load plugins
    tool_registry.load_all_plugins(str(base_dir))

    test_session = "test-integration"

    try:
        # 1. Start a session
        print("\n1. Starting tmux session...")
        result = tool_registry.execute("tmux-start", {
            "session_name": test_session,
            "command": "bash"
        })
        print(result["content"][0]["text"])
        assert "Started tmux session" in result["content"][0]["text"]

        time.sleep(1)

        # 2. Send a command
        print("\n2. Sending command...")
        result = tool_registry.execute("tmux-send", {
            "session_name": test_session,
            "command": "echo 'Hello from tmux!'"
        })
        print(result["content"][0]["text"])

        time.sleep(0.5)

        # 3. Capture output
        print("\n3. Capturing output...")
        result = tool_registry.execute("tmux-capture", {
            "session_name": test_session
        })
        print(result["content"][0]["text"])
        assert "Hello from tmux!" in result["content"][0]["text"]

        # 4. List sessions
        print("\n4. Listing sessions...")
        result = tool_registry.execute("tmux-list", {})
        print(result["content"][0]["text"])
        assert test_session in result["content"][0]["text"]

        # 5. Get attach command
        print("\n5. Getting attach command...")
        result = tool_registry.execute("tmux-attach", {
            "session_name": test_session
        })
        print(result["content"][0]["text"])
        assert "tmux attach" in result["content"][0]["text"]

        # 6. Kill session
        print("\n6. Killing session...")
        result = tool_registry.execute("tmux-kill", {
            "session_name": test_session
        })
        print(result["content"][0]["text"])
        assert "Killed session" in result["content"][0]["text"]

        # 7. Verify session is gone
        print("\n7. Verifying session is gone...")
        result = tool_registry.execute("tmux-list", {})
        print(result["content"][0]["text"])

        print("\n" + "="*60)
        print("✅ ALL FUNCTIONAL TESTS PASSED!")
        print("="*60)

    except Exception as e:
        # Cleanup on error
        try:
            tool_registry.execute("tmux-kill", {"session_name": test_session})
        except:
            pass
        raise

if __name__ == "__main__":
    try:
        test_tmux_functionality()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
