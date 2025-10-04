"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def session_manager():
    """Provide a SessionManager instance for tests"""
    from pty_mcp_server.core.manager import SessionManager
    return SessionManager()

@pytest.fixture
def tool_registry(session_manager):
    """Provide a ToolRegistry instance for tests"""
    from pty_mcp_server.lib.registry import ToolRegistry
    return ToolRegistry(session_manager)

@pytest.fixture
def base_dir():
    """Provide the base directory for plugin loading"""
    return Path(__file__).parent.parent / "pty_mcp_server"
