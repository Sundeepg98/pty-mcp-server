"""
Serial port connection management
"""

from typing import Optional


class SerialSession:
    """Manages serial port connections"""
    
    def __init__(self):
        self.serial = None
        self.device = None
        self.baudrate = None
    
    def open(self, device: str, baudrate: int = 9600, **kwargs):
        """Open a serial port connection"""
        try:
            import serial
        except ImportError:
            raise RuntimeError("pyserial not installed. Run: pip install pyserial")
        
        if self.serial:
            raise RuntimeError("Serial port already open")
        
        # Default serial parameters
        config = {
            'port': device,
            'baudrate': baudrate,
            'bytesize': kwargs.get('bytesize', serial.EIGHTBITS),
            'parity': kwargs.get('parity', serial.PARITY_NONE),
            'stopbits': kwargs.get('stopbits', serial.STOPBITS_ONE),
            'timeout': kwargs.get('timeout', 1),
            'xonxoff': kwargs.get('xonxoff', False),
            'rtscts': kwargs.get('rtscts', False),
            'dsrdtr': kwargs.get('dsrdtr', False)
        }
        
        self.serial = serial.Serial(**config)
        self.device = device
        self.baudrate = baudrate
        return True
    
    def send(self, data: str):
        """Send data through the serial port"""
        if not self.serial:
            raise RuntimeError("Serial port not open")
        
        sent = self.serial.write(data.encode('utf-8'))
        return sent
    
    def read(self, size: int = None, timeout: float = 1.0) -> str:
        """Read from the serial port"""
        if not self.serial:
            raise RuntimeError("Serial port not open")
        
        old_timeout = self.serial.timeout
        self.serial.timeout = timeout
        
        try:
            if size:
                data = self.serial.read(size)
            else:
                data = self.serial.read_all()
            
            if data:
                try:
                    return data.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    return data.hex()
            else:
                return "(no data received)"
        finally:
            self.serial.timeout = old_timeout
    
    def close(self):
        """Close the serial port"""
        if self.serial:
            self.serial.close()
            self.serial = None
            self.device = None
            self.baudrate = None
        return True
    
    def is_active(self) -> bool:
        """Check if serial port is open"""
        return self.serial is not None and self.serial.is_open