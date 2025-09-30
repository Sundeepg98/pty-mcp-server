"""
Clear terminal screen tool
"""

import os
from typing import Dict, Any

import sys

from pty_mcp_server.lib.base import BaseTool, ToolResult

class ClearTool(BaseTool):
    """Clear the terminal screen"""
    
    @property
    def name(self) -> str:
        return "clear"
    
    @property
    def description(self) -> str:
        return "Clear the terminal screen"
    
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
        """Clear the terminal"""
        
        if not self.session_manager or not self.session_manager.pty_session:
            # No PTY session - clear using system command
            try:
                os.system('clear' if os.name == 'posix' else 'cls')
                return ToolResult(
                    success=True,
                    content="Terminal cleared"
                )
            except:
                return ToolResult(
                    success=False,
                    content="",
                    error="Failed to clear terminal"
                )
        
        # Have PTY session - send clear command
        try:
            pty = self.session_manager.pty_session
            
            # Send clear escape sequence
            clear_sequence = "\033[2J\033[H"  # Clear screen and move cursor to home
            os.write(pty.master_fd, clear_sequence.encode())
            
            return ToolResult(
                success=True,
                content="PTY terminal cleared"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to clear PTY: {str(e)}"
            )