"""
PTY Connect tool - Start a PTY session
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class ConnectTool(BaseTool):
    """Start a PTY session with a command"""
    
    @property
    def name(self) -> str:
        return "connect"
    
    @property
    def description(self) -> str:
        return "Start a new PTY session with a specified command"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to run in PTY"
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Command arguments"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory"
                }
            },
            "required": ["command"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Start a PTY session"""
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
        
        command = arguments.get("command", "bash")
        args = arguments.get("args", [])
        working_dir = arguments.get("working_dir")
        
        # Use active project directory if available
        if not working_dir and self.session_manager.active_project:
            working_dir = self.session_manager.active_project.get("path")
        
        try:
            pty_session.start(command, args, working_dir)
            
            # Read initial output
            output = pty_session.read(timeout=1.0)
            
            return ToolResult(
                success=True,
                content=f"PTY session started with command: {command}\n{output}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )