"""
Socket Message tool - Send message and wait for prompt
"""

from typing import Dict, Any
import time

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SocketMessageTool(BaseTool):
    """Send message through socket and wait for prompt/response"""
    
    @property
    def name(self) -> str:
        return "socket-message"
    
    @property
    def description(self) -> str:
        return "Send message through socket and wait for prompt/response"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to send through the socket"
                },
                "wait_for_prompt": {
                    "type": "boolean",
                    "description": "Whether to wait for a prompt after sending (default: true)"
                },
                "prompt_timeout": {
                    "type": "number",
                    "description": "Timeout in seconds for waiting for prompt (default: 5)"
                },
                "add_newline": {
                    "type": "boolean",
                    "description": "Add newline after message (default: true)"
                }
            },
            "required": ["message"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Send message and optionally wait for prompt"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        socket_session = self.session_manager.get_socket_session()
        
        # Check if socket is open
        if not socket_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active socket connection. Use socket-open first."
            )
        
        message = arguments.get("message", "")
        wait_for_prompt = arguments.get("wait_for_prompt", True)
        prompt_timeout = arguments.get("prompt_timeout", 5.0)
        add_newline = arguments.get("add_newline", True)
        
        try:
            # Prepare message
            if add_newline and not message.endswith('\n'):
                message += '\n'
            
            # Send the message
            bytes_sent = socket_session.send(message)
            
            response = f"Sent {bytes_sent} bytes"
            
            # Wait for prompt/response if requested
            if wait_for_prompt:
                # Small delay to allow server to process
                time.sleep(0.1)
                
                # Read response with timeout
                received = socket_session.read(prompt_timeout)
                
                if received and received != "(no data received within timeout)":
                    response += f"\n\nReceived:\n{received}"
                elif received == "(no data received within timeout)":
                    response += f"\n\n(No response within {prompt_timeout}s timeout)"
                else:
                    response += f"\n\n{received}"
            
            return ToolResult(
                success=True,
                content=response
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to send message: {str(e)}"
            )