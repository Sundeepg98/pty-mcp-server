"""
Process Send tool - Send input to active process
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SendProcTool(BaseTool):
    """Send input to active process"""
    
    @property
    def name(self) -> str:
        return "send-proc"
    
    @property
    def description(self) -> str:
        return "Send input to the active process"
    
    @property
    def category(self) -> str:
        return "process"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Text to send to process"
                }
            },
            "required": ["message"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Send input to process"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        proc_session = self.session_manager.get_proc_session()
        
        # Check if active
        if not proc_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active process. Use 'spawn' first."
            )
        
        message = arguments.get("message", "")
        
        try:
            # Send the message
            proc_session.send(message)
            
            # Read response
            output = proc_session.read(timeout=1.0)
            
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