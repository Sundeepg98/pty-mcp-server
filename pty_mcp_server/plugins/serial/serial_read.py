"""
Serial Read tool - Read data from serial port
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SerialReadTool(BaseTool):
    """Read data from the active serial port"""
    
    @property
    def name(self) -> str:
        return "serial-read"
    
    @property
    def description(self) -> str:
        return "Read data from the active serial port"
    
    @property
    def category(self) -> str:
        return "serial"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "size": {
                    "type": "number",
                    "description": "Number of bytes to read (optional, reads all available if not specified)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Read timeout in seconds (default: 2.0)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Read from the serial port"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        serial_session = self.session_manager.get_serial_session()
        
        if not serial_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active serial connection. Use serial-open first."
            )
        
        size = arguments.get("size", None)
        timeout = arguments.get("timeout", 2.0)
        
        try:
            data = serial_session.read(size, timeout)
            
            if data and data != "(no data received)":
                return ToolResult(
                    success=True,
                    content=data
                )
            else:
                return ToolResult(
                    success=True,
                    content="(no data received)"
                )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Read error: {str(e)}"
            )