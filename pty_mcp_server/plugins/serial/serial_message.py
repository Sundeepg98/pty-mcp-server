"""
Serial Message tool - Send message and wait for response
"""

from typing import Dict, Any
import time

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SerialMessageTool(BaseTool):
    """Send message through serial and wait for prompt/response"""
    
    @property
    def name(self) -> str:
        return "serial-message"
    
    @property
    def description(self) -> str:
        return "Send message through serial port and wait for response"
    
    @property
    def category(self) -> str:
        return "serial"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to send through the serial port"
                },
                "wait_for_prompt": {
                    "type": "boolean",
                    "description": "Whether to wait for a response after sending (default: true)"
                },
                "prompt_timeout": {
                    "type": "number",
                    "description": "Timeout in seconds for waiting for response (default: 5)"
                },
                "add_newline": {
                    "type": "boolean",
                    "description": "Add newline (\\r\\n) after message (default: true)"
                }
            },
            "required": ["message"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Send message and optionally wait for response"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        serial_session = self.session_manager.get_serial_session()
        
        # Check if serial is open
        if not serial_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="No active serial connection. Use serial-open first."
            )
        
        message = arguments.get("message", "")
        wait_for_prompt = arguments.get("wait_for_prompt", True)
        prompt_timeout = arguments.get("prompt_timeout", 5.0)
        add_newline = arguments.get("add_newline", True)
        
        try:
            # Prepare message (serial typically uses \r\n)
            if add_newline and not message.endswith('\r\n'):
                message += '\r\n'
            
            # Send the message
            bytes_sent = serial_session.send(message)
            
            response = f"Sent {bytes_sent} bytes"
            
            # Wait for response if requested
            if wait_for_prompt:
                # Small delay to allow device to process
                time.sleep(0.1)
                
                # Collect response data
                all_data = []
                start_time = time.time()
                
                while (time.time() - start_time) < prompt_timeout:
                    data = serial_session.read(None, 0.5)  # Short timeout for each read
                    if data and data != "(no data received)":
                        all_data.append(data)
                        # Check if we got a prompt (common patterns)
                        if any(prompt in data for prompt in ['>', '#', '$', ':', 'login:', 'Password:']):
                            break
                    time.sleep(0.1)
                
                if all_data:
                    received = ''.join(all_data)
                    response += f"\n\nReceived:\n{received}"
                else:
                    response += f"\n\n(No response within {prompt_timeout}s timeout)"
            
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