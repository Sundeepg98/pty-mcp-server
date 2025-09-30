"""
PTY Disconnect tool - Terminate PTY session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class DisconnectTool(BaseTool):
    """Terminate active PTY session"""
    
    @property
    def name(self) -> str:
        return "disconnect"
    
    @property
    def description(self) -> str:
        return "Terminate the active PTY session"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Terminate PTY session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        pty_session = self.session_manager.get_pty_session()
        
        # Check if active
        if not pty_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active PTY session"
            )
        
        try:
            pty_session.terminate()
            
            # Clear the session reference from manager
            self.session_manager.pty_session = None
            
            return ToolResult(
                success=True,
                content="PTY session terminated"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )