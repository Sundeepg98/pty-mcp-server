"""
Socket Read tool - Read data from socket
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SocketReadTool(BaseTool):
    """Read data from active socket"""
    
    @property
    def name(self) -> str:
        return "socket-read"
    
    @property
    def description(self) -> str:
        return "Read data from the active socket"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "timeout": {
                    "type": "number",
                    "description": "Read timeout in seconds (default: 2.0)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Read from the socket"""
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
                error="No active socket. Open one with socket-open first."
            )
        
        timeout = arguments.get("timeout", 2.0)
        
        try:
            data = socket_session.read(timeout)
            
            return ToolResult(
                success=True,
                content=data
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )