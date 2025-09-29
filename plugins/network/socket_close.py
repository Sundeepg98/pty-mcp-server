"""
Socket Close tool - Close active socket
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SocketCloseTool(BaseTool):
    """Close the active socket connection"""
    
    @property
    def name(self) -> str:
        return "socket-close"
    
    @property
    def description(self) -> str:
        return "Close the active socket connection"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Close the socket"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        socket_session = self.session_manager.get_socket_session()
        
        # Check if open
        if not socket_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active socket to close"
            )
        
        try:
            socket_session.close()
            
            # Clear the session reference from manager
            self.session_manager.socket_session = None
            
            return ToolResult(
                success=True,
                content="Socket closed successfully"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )