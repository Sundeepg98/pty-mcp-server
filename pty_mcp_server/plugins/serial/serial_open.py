"""
Serial Open tool - Open a serial port connection
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SerialOpenTool(BaseTool):
    """Open a serial port connection"""
    
    @property
    def name(self) -> str:
        return "serial-open"
    
    @property
    def description(self) -> str:
        return "Open a serial port connection to a device"
    
    @property
    def category(self) -> str:
        return "serial"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "Serial device path (e.g., /dev/ttyUSB0, COM3)"
                },
                "baudrate": {
                    "type": "number",
                    "description": "Baud rate (default: 9600)"
                },
                "bytesize": {
                    "type": "number",
                    "enum": [5, 6, 7, 8],
                    "description": "Number of data bits (default: 8)"
                },
                "parity": {
                    "type": "string",
                    "enum": ["none", "even", "odd", "mark", "space"],
                    "description": "Parity checking (default: none)"
                },
                "stopbits": {
                    "type": "number",
                    "enum": [1, 1.5, 2],
                    "description": "Number of stop bits (default: 1)"
                }
            },
            "required": ["device"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Open a serial port connection"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        serial_session = self.session_manager.get_serial_session()
        
        # Check if already open
        if serial_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="Serial port already open. Close it first."
            )
        
        device = arguments.get("device")
        baudrate = arguments.get("baudrate", 9600)
        
        # Convert parity string to serial module constant
        parity_map = {
            'none': 'N',
            'even': 'E', 
            'odd': 'O',
            'mark': 'M',
            'space': 'S'
        }
        
        kwargs = {}
        if 'bytesize' in arguments:
            kwargs['bytesize'] = arguments['bytesize']
        if 'parity' in arguments:
            kwargs['parity'] = parity_map.get(arguments['parity'].lower(), 'N')
        if 'stopbits' in arguments:
            kwargs['stopbits'] = arguments['stopbits']
        
        try:
            serial_session.open(device, baudrate, **kwargs)
            
            return ToolResult(
                success=True,
                content=f"Serial port opened: {device} at {baudrate} baud"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to open serial port: {str(e)}"
            )