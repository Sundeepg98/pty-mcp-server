"""
Serial Close tool - Close the active serial connection
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SerialCloseTool(BaseTool):
    """Close the active serial connection"""
    
    @property
    def name(self) -> str:
        return "serial-close"
    
    @property
    def description(self) -> str:
        return "Close the active serial connection"
    
    @property
    def category(self) -> str:
        return "serial"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Close the serial connection"""
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
                error="No active serial connection"
            )
        
        try:
            device = serial_session.device
            serial_session.close()
            
            # Clear the session reference from manager
            self.session_manager.serial_session = None
            
            return ToolResult(
                success=True,
                content=f"Serial connection closed: {device}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )