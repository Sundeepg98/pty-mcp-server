"""
Bash PTY tool - Start an interactive bash session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class BashTool(BaseTool):
    """Start an interactive bash PTY session"""
    
    @property
    def name(self) -> str:
        return "bash"
    
    @property
    def description(self) -> str:
        return "Start an interactive bash shell in PTY"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "working_dir": {
                    "type": "string",
                    "description": "Initial working directory"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Start bash PTY session"""
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
        
        working_dir = arguments.get("working_dir")
        
        # Use active project directory if available
        if not working_dir and self.session_manager.active_project:
            working_dir = self.session_manager.active_project.get("path")
        
        try:
            pty_session.start("bash", [], working_dir)
            
            # Read initial prompt
            output = pty_session.read(timeout=1.0)
            
            return ToolResult(
                success=True,
                content=f"Bash PTY session started\n{output}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )