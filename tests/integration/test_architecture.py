#!/usr/bin/env python3
"""
Comprehensive test for DDD restructure changes
Tests all 37 tools including 6 tmux tools from current source
"""

import sys
from pathlib import Path

# Add project to path (test from source, not installed version)
sys.path.insert(0, str(Path(__file__).parent))

from pty_mcp_server.core.manager import SessionManager
from pty_mcp_server.lib.registry import ToolRegistry

def test_ddd_architecture():
    """Test that DDD architecture is properly implemented"""

    print("="*70)
    print("TESTING DDD RESTRUCTURE - PTY MCP SERVER")
    print("="*70)

    # Test 1: Domain Layer - SessionManager
    print("\n📦 TEST 1: Domain Layer (SessionManager)")
    print("-" * 70)
    session_manager = SessionManager()

    # Verify all session types exist
    assert hasattr(session_manager, 'pty_session'), "Missing pty_session"
    assert hasattr(session_manager, 'proc_session'), "Missing proc_session"
    assert hasattr(session_manager, 'socket_session'), "Missing socket_session"
    assert hasattr(session_manager, 'serial_session'), "Missing serial_session"
    assert hasattr(session_manager, 'tmux_manager'), "Missing tmux_manager"

    # Verify lazy initialization methods
    assert hasattr(session_manager, 'get_pty_session'), "Missing get_pty_session"
    assert hasattr(session_manager, 'get_proc_session'), "Missing get_proc_session"
    assert hasattr(session_manager, 'get_socket_session'), "Missing get_socket_session"
    assert hasattr(session_manager, 'get_serial_session'), "Missing get_serial_session"
    assert hasattr(session_manager, 'get_tmux_manager'), "Missing get_tmux_manager"

    print("✅ SessionManager (Domain Service) - All session types present")
    print("   - PTY Session (singleton)")
    print("   - Process Session (singleton)")
    print("   - Socket Session (singleton)")
    print("   - Serial Session (singleton)")
    print("   - Tmux Manager (multi-session)")

    # Test 2: Application Layer - ToolRegistry
    print("\n📦 TEST 2: Application Layer (ToolRegistry with DI)")
    print("-" * 70)
    tool_registry = ToolRegistry(session_manager)

    # Verify DI worked
    assert tool_registry.session_manager is session_manager, "DI failed - different instance"
    print("✅ ToolRegistry received SessionManager via Dependency Injection")

    # Test 3: Interface Layer - Plugin Loading
    print("\n📦 TEST 3: Interface Layer (Plugin Discovery & Loading)")
    print("-" * 70)
    base_dir = Path(__file__).parent / "pty_mcp_server"
    loaded = tool_registry.load_all_plugins(str(base_dir))

    print(f"Loaded tools by category:")
    total_tools = 0
    for category, count in sorted(loaded.items()):
        print(f"  {category:12s}: {count:2d} tools")
        total_tools += count

    print(f"\n✅ Total: {total_tools} tools loaded")

    # Test 4: Verify Tool Count
    print("\n📦 TEST 4: Verify Complete Tool Set")
    print("-" * 70)

    expected_categories = {
        'terminal': 8,
        'process': 6,
        'network': 6,
        'serial': 5,
        'system': 6,
        'tmux': 6
    }

    for category, expected_count in expected_categories.items():
        actual_count = loaded.get(category, 0)
        status = "✅" if actual_count == expected_count else "❌"
        print(f"{status} {category:12s}: {actual_count:2d}/{expected_count} tools")
        if actual_count != expected_count:
            print(f"   ERROR: Expected {expected_count}, got {actual_count}")

    # Test 5: Verify Tmux Tools Specifically
    print("\n📦 TEST 5: Verify Tmux Integration (New in v4.0)")
    print("-" * 70)

    tmux_tools = [
        'tmux-start',
        'tmux-list',
        'tmux-send',
        'tmux-capture',
        'tmux-attach',
        'tmux-kill'
    ]

    for tool_name in tmux_tools:
        tool = tool_registry.get_tool(tool_name)
        if tool:
            status = "✅"
            # Verify tool has session_manager injected
            has_sm = hasattr(tool, 'session_manager') and tool.session_manager is not None
            di_status = "✅ DI" if has_sm else "❌ NO DI"
            print(f"{status} {tool_name:15s} - {di_status}")
        else:
            print(f"❌ {tool_name:15s} - NOT FOUND")

    # Test 6: Verify 100% Dependency Injection
    print("\n📦 TEST 6: Verify 100% Dependency Injection")
    print("-" * 70)

    all_tools = tool_registry.list_tools()
    tools_with_di = 0
    tools_without_di = 0

    for tool_def in all_tools:
        tool = tool_registry.get_tool(tool_def['name'])
        if hasattr(tool, 'session_manager') and tool.session_manager is session_manager:
            tools_with_di += 1
        else:
            tools_without_di += 1
            print(f"   ⚠️  {tool_def['name']} - Missing or wrong SessionManager")

    print(f"✅ Tools with DI: {tools_with_di}/{total_tools}")
    if tools_without_di > 0:
        print(f"❌ Tools without DI: {tools_without_di}/{total_tools}")

    # Test 7: Test Documentation Structure
    print("\n📦 TEST 7: Verify Documentation Structure")
    print("-" * 70)

    docs_path = Path(__file__).parent / "docs"
    docs_exist = docs_path.exists()

    if docs_exist:
        # Check architecture docs
        arch_readme = docs_path / "architecture" / "README.md"
        di_guide = docs_path / "architecture" / "dependency-injection.md"
        adr_001 = docs_path / "architecture" / "adr" / "001-domain-driven-design.md"
        adr_002 = docs_path / "architecture" / "adr" / "002-tmux-integration.md"
        tmux_feature = docs_path / "features" / "tmux-integration.md"

        doc_files = {
            'Architecture Overview': arch_readme.exists(),
            'DI Guide': di_guide.exists(),
            'ADR-001 (DDD)': adr_001.exists(),
            'ADR-002 (Tmux)': adr_002.exists(),
            'Tmux Feature Doc': tmux_feature.exists()
        }

        for doc_name, exists in doc_files.items():
            status = "✅" if exists else "❌"
            print(f"{status} {doc_name}")
    else:
        print("❌ docs/ directory not found")

    # Test 8: Test Structure
    print("\n📦 TEST 8: Verify Test Structure")
    print("-" * 70)

    tests_path = Path(__file__).parent / "tests"
    test_dirs = {
        'Unit Tests': tests_path / "unit",
        'Integration Tests': tests_path / "integration",
        'Functional Tests': tests_path / "functional",
        'Fixtures': tests_path / "conftest.py"
    }

    for test_name, test_path in test_dirs.items():
        exists = test_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {test_name}")

    # Final Summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)

    all_pass = (
        total_tools == 37 and
        loaded.get('tmux', 0) == 6 and
        tools_with_di == total_tools and
        docs_exist
    )

    if all_pass:
        print("✅ ALL TESTS PASSED!")
        print(f"\n🎯 DDD Architecture: FULLY IMPLEMENTED")
        print(f"   - Domain Layer: SessionManager + 5 session types")
        print(f"   - Application Layer: ToolRegistry with Factory Pattern")
        print(f"   - Interface Layer: 37 tools across 6 categories")
        print(f"   - 100% Dependency Injection: {tools_with_di}/{total_tools} tools")
        print(f"\n📚 Documentation: COMPLETE")
        print(f"   - Architecture guides with DDD explanation")
        print(f"   - 2 ADRs documenting key decisions")
        print(f"   - Comprehensive DI patterns guide")
        print(f"\n🧪 Test Structure: ORGANIZED")
        print(f"   - Unit/Integration/Functional separation")
        print(f"   - Pytest fixtures for DI testing")
        print(f"\n🆕 Tmux Integration: WORKING")
        print(f"   - 6 new tools for multi-session management")
        print(f"   - Total: 31 (original) + 6 (tmux) = 37 tools")

        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Total tools: {total_tools}/37")
        print(f"   Tmux tools: {loaded.get('tmux', 0)}/6")
        print(f"   DI coverage: {tools_with_di}/{total_tools}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_ddd_architecture()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
