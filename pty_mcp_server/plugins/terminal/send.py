"""
PTY Send tool - Send input to active PTY session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SendTool(BaseTool):
    """Send input to active PTY session"""
    
    @property
    def name(self) -> str:
        return "send"
    
    @property
    def description(self) -> str:
        return "Send input to the active PTY session"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Text to send to PTY"
                }
            },
            "required": ["message"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Send input to PTY session"""
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
                error="No active PTY session. Use 'connect' or 'bash' first."
            )
        
        message = arguments.get("message", "")
        
        try:
            # Send the message
            pty_session.send(message)
            
            # Read response
            output = pty_session.read(timeout=2.0)
            
            return ToolResult(
                success=True,
                content=output
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )