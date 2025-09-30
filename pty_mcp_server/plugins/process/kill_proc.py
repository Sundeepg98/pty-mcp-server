"""
Process Kill tool - Terminate active process
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class KillProcTool(BaseTool):
    """Terminate active process"""
    
    @property
    def name(self) -> str:
        return "kill-proc"
    
    @property
    def description(self) -> str:
        return "Kill the active process"
    
    @property
    def category(self) -> str:
        return "process"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Kill the process"""
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
                error="No active process to kill"
            )
        
        try:
            proc_session.terminate()
            
            # Clear the session reference from manager
            self.session_manager.proc_session = None
            
            return ToolResult(
                success=True,
                content="Process terminated"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )