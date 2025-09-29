"""
Serial Write tool - Write data to serial port
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SerialWriteTool(BaseTool):
    """Write data to the active serial port"""
    
    @property
    def name(self) -> str:
        return "serial-write"
    
    @property
    def description(self) -> str:
        return "Write data to the active serial port"
    
    @property
    def category(self) -> str:
        return "serial"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data to send through the serial port"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Write to the serial port"""
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
        
        data = arguments.get("data", "")
        
        try:
            bytes_sent = serial_session.send(data)
            
            return ToolResult(
                success=True,
                content=f"Sent {bytes_sent} bytes"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Write error: {str(e)}"
            )