"""
Network socket connection management
"""

import socket
from typing import Optional


class SocketSession:
    """Manages network socket connections"""
    
    def __init__(self):
        self.socket = None
        self.host = None
        self.port = None
        
    def open(self, host: str, port: int, protocol: str = 'tcp'):
        """Open a socket connection"""
        if self.socket:
            raise RuntimeError("Socket already open")
        
        if protocol.lower() == 'tcp':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif protocol.lower() == 'udp':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise ValueError(f"Unknown protocol: {protocol}")
        
        self.socket.connect((host, port))
        self.host = host
        self.port = port
        return True
    
    def send(self, data: str):
        """Send data through the socket"""
        if not self.socket:
            raise RuntimeError("Socket not open")
        
        sent = self.socket.send(data.encode('utf-8'))
        return sent
    
    def read(self, timeout: float = 2.0) -> str:
        """Read from the socket"""
        if not self.socket:
            raise RuntimeError("Socket not open")
        
        self.socket.settimeout(timeout)
        try:
            data = self.socket.recv(4096)
            if data:
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    return data.hex()
            else:
                return "(socket closed by remote)"
        except socket.timeout:
            return "(no data received within timeout)"
    
    def close(self):
        """Close the socket"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.host = None
            self.port = None
        return True
    
    def is_active(self) -> bool:
        """Check if socket is open"""
        return self.socket is not None