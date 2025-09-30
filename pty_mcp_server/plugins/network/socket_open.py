"""
Socket Open tool - Open a network socket
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SocketOpenTool(BaseTool):
    """Open a TCP or UDP socket connection"""
    
    @property
    def name(self) -> str:
        return "socket-open"
    
    @property
    def description(self) -> str:
        return "Open a TCP or UDP socket connection"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Host to connect to"
                },
                "port": {
                    "type": "number",
                    "description": "Port number"
                },
                "protocol": {
                    "type": "string",
                    "enum": ["tcp", "udp"],
                    "description": "Protocol (tcp or udp)"
                }
            },
            "required": ["host", "port"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Open a socket connection"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        socket_session = self.session_manager.get_socket_session()
        
        # Check if already open
        if socket_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="Socket already open. Close it first."
            )
        
        host = arguments.get("host")
        port = arguments.get("port")
        protocol = arguments.get("protocol", "tcp")
        
        try:
            socket_session.open(host, port, protocol)
            
            return ToolResult(
                success=True,
                content=f"Socket opened to {host}:{port} ({protocol.upper()})"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )