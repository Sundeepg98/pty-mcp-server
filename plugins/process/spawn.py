"""
Process Spawn tool - Start a process without PTY
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SpawnTool(BaseTool):
    """Start a process without PTY"""
    
    @property
    def name(self) -> str:
        return "spawn"
    
    @property
    def description(self) -> str:
        return "Launch a process without PTY"
    
    @property
    def category(self) -> str:
        return "process"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to spawn"
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
        """Start a process"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        proc_session = self.session_manager.get_proc_session()
        
        # Clean up any completed process
        if proc_session.process and proc_session.process.poll() is not None:
            proc_session.process = None
        
        # Check if already active
        if proc_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="Process already active. Kill it first."
            )
        
        command = arguments.get("command")
        args = arguments.get("args", [])
        working_dir = arguments.get("working_dir")
        
        # Use active project directory if available
        if not working_dir and self.session_manager.active_project:
            working_dir = self.session_manager.active_project.get("path")
        
        try:
            proc_session.start(command, args, working_dir)
            
            # Read initial output
            output = proc_session.read(timeout=0.5)
            
            # Check if process completed
            if proc_session.process and proc_session.process.poll() is not None:
                # Process completed, clean it up
                return_code = proc_session.process.returncode
                proc_session.process = None  # Clear the completed process
                return ToolResult(
                    success=True,
                    content=f"Process completed: {command} (exit code: {return_code})\n{output}"
                )
            else:
                return ToolResult(
                    success=True,
                    content=f"Process started: {command}\n{output}"
                )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )