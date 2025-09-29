"""
Execute shell command tool
"""

import subprocess
import os
import json
from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class ExecTool(BaseTool):
    """Execute shell commands with structured output"""
    
    @property
    def name(self) -> str:
        return "exec"
    
    @property
    def description(self) -> str:
        return "Execute a shell command and return structured output"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory (optional)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 30)"
                }
            },
            "required": ["command"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the shell command"""
        command = arguments.get("command", "")
        
        # Version check for debugging
        if command == "pty-version":
            return ToolResult(
                success=True,
                content=json.dumps({
                    "version": "PTY MCP v2.2",
                    "status": "Auto-reload verified live",
                    "timestamp": "2025-09-29"
                }, indent=2)
            )
        
        working_dir = arguments.get("working_dir")
        timeout = arguments.get("timeout", 30)
        
        # Use active project directory if available and no working_dir specified
        if not working_dir and self.session_manager and self.session_manager.active_project:
            working_dir = self.session_manager.active_project.get("path")
        
        if not working_dir:
            working_dir = os.getcwd()
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )
            
            # Format output
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "cwd": working_dir
            }
            
            return ToolResult(
                success=True,
                content=json.dumps(output, indent=2),
                metadata=output
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                content="",
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )