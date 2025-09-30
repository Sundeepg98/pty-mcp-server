"""
Telnet tool - Telnet connections via PTY
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class TelnetTool(BaseTool):
    """Connect to remote host via Telnet"""
    
    @property
    def name(self) -> str:
        return "telnet"
    
    @property
    def description(self) -> str:
        return "Connect to a remote host via Telnet"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Telnet host to connect to"
                },
                "port": {
                    "type": "number",
                    "description": "Telnet port (default: 23)"
                }
            },
            "required": ["host"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Start Telnet session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        pty_session = self.session_manager.get_pty_session()
        
        # Check if already active
        if pty_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="PTY session already active. Disconnect first."
            )
        
        host = arguments.get("host")
        port = arguments.get("port", 23)
        
        try:
            pty_session.start("telnet", [host, str(port)])
            
            # Read initial output
            output = pty_session.read(timeout=2.0)
            
            return ToolResult(
                success=True,
                content=f"Telnet session started to {host}:{port}\n{output}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )