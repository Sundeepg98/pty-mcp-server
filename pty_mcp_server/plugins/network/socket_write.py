"""
Socket Write tool - Send data through socket
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SocketWriteTool(BaseTool):
    """Send data through active socket"""
    
    @property
    def name(self) -> str:
        return "socket-write"
    
    @property
    def description(self) -> str:
        return "Send data through the active socket"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data to send through the socket"
                }
            },
            "required": ["data"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Write to the socket"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        socket_session = self.session_manager.get_socket_session()
        
        # Check if open
        if not socket_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active socket. Open one with socket-open first."
            )
        
        original_data = arguments.get("data", "")
        data = original_data
        
        # Check if this looks like an HTTP request
        http_methods = ('GET ', 'POST ', 'PUT ', 'DELETE ', 'HEAD ', 'OPTIONS ', 'PATCH ', 'CONNECT ', 'TRACE ')
        is_http = any(data.startswith(method) for method in http_methods)
        
        debug_info = []
        if is_http:
            debug_info.append(f"Detected HTTP request")
            debug_info.append(f"Original: {len(original_data)} bytes")
            
            # Convert Unix line endings to proper HTTP line endings
            if '\r\n' not in data:
                data = data.replace('\n', '\r\n')
                debug_info.append(f"Converted \\n to \\r\\n")
            
            # Ensure double CRLF at the end for HTTP
            if not data.endswith('\r\n\r\n'):
                if data.endswith('\r\n'):
                    data += '\r\n'
                    debug_info.append(f"Added final \\r\\n")
                elif data.endswith('\n'):
                    # Remove the \n and add proper ending
                    data = data[:-1] + '\r\n\r\n'
                    debug_info.append(f"Fixed ending to \\r\\n\\r\\n")
                else:
                    data += '\r\n\r\n'
                    debug_info.append(f"Added \\r\\n\\r\\n")
            
            debug_info.append(f"Final: {len(data)} bytes")
        
        try:
            bytes_sent = socket_session.send(data)
            
            result = f"Sent {bytes_sent} bytes"
            if debug_info:
                result += "\n" + "\n".join(debug_info)
            
            return ToolResult(
                success=True,
                content=result
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )