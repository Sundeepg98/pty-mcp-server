"""
Resize terminal window tool
"""

import os
import struct
import fcntl
import termios
from typing import Dict, Any


from pty_mcp_server.lib.base import BaseTool, ToolResult

class ResizeTool(BaseTool):
    """Resize the terminal window"""
    
    @property
    def name(self) -> str:
        return "resize"
    
    @property
    def description(self) -> str:
        return "Resize the terminal window dimensions"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "width": {
                    "type": "number",
                    "description": "Terminal width in columns (default: 80)"
                },
                "height": {
                    "type": "number", 
                    "description": "Terminal height in rows (default: 24)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Resize the terminal"""
        width = arguments.get("width", 80)
        height = arguments.get("height", 24)
        
        if not self.session_manager or not self.session_manager.pty_session:
            return ToolResult(
                success=False,
                content="",
                error="No active PTY session to resize"
            )
        
        try:
            # Get the PTY file descriptor
            fd = self.session_manager.pty_session.master_fd
            
            # Set terminal window size using ioctl
            winsize = struct.pack("HHHH", height, width, 0, 0)
            fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
            
            return ToolResult(
                success=True,
                content=f"Terminal resized to {width}x{height} (width x height)"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to resize terminal: {str(e)}"
            )