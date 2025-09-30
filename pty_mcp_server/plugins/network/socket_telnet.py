"""
Socket Telnet tool - Simple Telnet client with IAC handling
"""

from typing import Dict, Any
import socket
import time

from pty_mcp_server.lib.base import BaseTool, ToolResult

class SocketTelnetTool(BaseTool):
    """Simple Telnet-like communication with IAC sequence handling"""
    
    # Telnet IAC (Interpret As Command) constants
    IAC = 255   # Interpret As Command
    DONT = 254  # You are not to use option
    DO = 253    # Please use option  
    WONT = 252  # I won't use option
    WILL = 251  # I will use option
    SB = 250    # Subnegotiation begin
    SE = 240    # Subnegotiation end
    
    @property
    def name(self) -> str:
        return "socket-telnet"
    
    @property
    def description(self) -> str:
        return "Simple Telnet client over TCP sockets with IAC handling"
    
    @property
    def category(self) -> str:
        return "network"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP address to connect to"
                },
                "port": {
                    "type": "number",
                    "description": "Port number (default: 23 for telnet)"
                },
                "initial_read": {
                    "type": "boolean",
                    "description": "Read initial banner after connection (default: true)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Connection timeout in seconds (default: 10)"
                }
            },
            "required": ["host"]
        }
    
    def remove_iac_sequences(self, data: bytes) -> bytes:
        """Remove Telnet IAC sequences from data"""
        result = bytearray()
        i = 0
        while i < len(data):
            if data[i] == self.IAC:
                # IAC found, skip the command sequence
                if i + 1 < len(data):
                    cmd = data[i + 1]
                    if cmd in [self.DONT, self.DO, self.WONT, self.WILL]:
                        # Skip IAC, command, and option
                        i += 3
                    elif cmd == self.SB:
                        # Skip until SE (subnegotiation end)
                        j = i + 2
                        while j < len(data) - 1:
                            if data[j] == self.IAC and data[j + 1] == self.SE:
                                i = j + 2
                                break
                            j += 1
                        else:
                            i += 2  # Skip incomplete subnegotiation
                    elif cmd == self.IAC:
                        # Double IAC means literal 255
                        result.append(255)
                        i += 2
                    else:
                        # Other commands, skip 2 bytes
                        i += 2
                else:
                    # Incomplete IAC at end
                    i += 1
            else:
                # Normal data
                result.append(data[i])
                i += 1
        
        return bytes(result)
    
    def negotiate_telnet_options(self, sock: socket.socket) -> str:
        """Handle initial Telnet negotiation"""
        responses = []
        sock.settimeout(0.5)  # Short timeout for negotiation
        
        try:
            # Read and respond to initial negotiations
            for _ in range(5):  # Max 5 rounds of negotiation
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    
                    # Look for IAC sequences
                    i = 0
                    while i < len(data):
                        if data[i] == self.IAC and i + 2 < len(data):
                            cmd = data[i + 1]
                            option = data[i + 2]
                            
                            # Respond to negotiations (refuse all for simplicity)
                            if cmd == self.DO:
                                # Server wants us to enable option, we refuse
                                response = bytes([self.IAC, self.WONT, option])
                                sock.send(response)
                                responses.append(f"Refused DO {option}")
                            elif cmd == self.WILL:
                                # Server will enable option, we don't want it
                                response = bytes([self.IAC, self.DONT, option])
                                sock.send(response)
                                responses.append(f"Refused WILL {option}")
                            
                            i += 3
                        else:
                            i += 1
                    
                    # Small delay before next read
                    time.sleep(0.1)
                    
                except socket.timeout:
                    break
                    
        except Exception as e:
            responses.append(f"Negotiation error: {e}")
        
        return ", ".join(responses) if responses else "No negotiation needed"
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Connect to Telnet server and handle IAC sequences"""
        host = arguments.get("host")
        port = arguments.get("port", 23)
        initial_read = arguments.get("initial_read", True)
        timeout = arguments.get("timeout", 10)
        
        # Create a new socket for this telnet session
        sock = None
        try:
            # Create TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Connect to server
            sock.connect((host, port))
            
            result = f"Connected to {host}:{port}\n"
            
            # Handle initial Telnet negotiation
            negotiation = self.negotiate_telnet_options(sock)
            if negotiation:
                result += f"Negotiation: {negotiation}\n"
            
            # Read initial banner if requested
            if initial_read:
                sock.settimeout(2.0)
                try:
                    data = sock.recv(4096)
                    if data:
                        # Remove IAC sequences and decode
                        clean_data = self.remove_iac_sequences(data)
                        try:
                            banner = clean_data.decode('utf-8', errors='replace')
                            result += f"\nBanner:\n{banner}"
                        except:
                            result += f"\nBanner (hex): {clean_data.hex()}"
                except socket.timeout:
                    result += "\n(No banner received)"
            
            # Close the temporary connection
            # The actual telnet session should use the regular socket tools
            sock.close()
            
            result += "\n\nTelnet handshake complete. Use socket-open to establish a persistent session."
            
            return ToolResult(
                success=True,
                content=result
            )
            
        except Exception as e:
            if sock:
                sock.close()
            return ToolResult(
                success=False,
                content="",
                error=f"Telnet connection failed: {str(e)}"
            )