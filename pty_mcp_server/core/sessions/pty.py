"""
PTY (Pseudo-Terminal) session management
"""

import os
import pty
import subprocess
import select
import fcntl
import re
from typing import List, Optional


class PTYSession:
    """Manages a PTY (pseudo-terminal) session"""
    
    def __init__(self):
        self.master_fd = None
        self.slave_fd = None
        self.process = None
    
    @staticmethod
    def clean_output(text: str) -> str:
        """Remove common terminal escape sequences for cleaner output"""
        # Remove bracketed paste mode sequences
        text = text.replace('\x1b[?2004h', '')  # Enable bracketed paste
        text = text.replace('\x1b[?2004l', '')  # Disable bracketed paste
        
        # Remove other common escape sequences but keep colors
        text = re.sub(r'\x1b\[\?[0-9]+[hl]', '', text)  # Mode sequences
        text = re.sub(r'\x1b\[K', '', text)  # Clear line
        text = re.sub(r'\x1b\[J', '', text)  # Clear screen
        text = re.sub(r'\x1b\[H', '', text)  # Home cursor
        
        return text
        
    def start(self, command: str, args: List[str] = None, working_dir: str = None):
        """Start a PTY session with the given command"""
        if self.process:
            raise RuntimeError("PTY session already active")
        
        # Create PTY
        self.master_fd, self.slave_fd = pty.openpty()
        
        # Make master non-blocking
        flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Prepare command
        if args:
            cmd_list = [command] + args
        else:
            cmd_list = [command] if command != 'bash' else ['/bin/bash']
        
        # Start process
        self.process = subprocess.Popen(
            cmd_list,
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            cwd=working_dir,
            preexec_fn=os.setsid
        )
        
        return True
    
    def send(self, data: str):
        """Send data to the PTY"""
        if not self.process:
            raise RuntimeError("No active PTY session")
        
        # Ensure newline
        if not data.endswith('\n'):
            data += '\n'
        
        os.write(self.master_fd, data.encode('utf-8'))
        return True
    
    def read(self, timeout: float = 0.5) -> str:
        """Read from the PTY with timeout"""
        if not self.process:
            raise RuntimeError("No active PTY session")
        
        output = ""
        while True:
            ready, _, _ = select.select([self.master_fd], [], [], timeout)
            if not ready:
                break
            
            try:
                data = os.read(self.master_fd, 4096)
                if data:
                    output += data.decode('utf-8', errors='replace')
                else:
                    break
            except OSError:
                break
        
        # Clean escape sequences from output
        return self.clean_output(output)
    
    def terminate(self):
        """Terminate the PTY session"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        
        if self.master_fd:
            os.close(self.master_fd)
            self.master_fd = None
        
        if self.slave_fd:
            os.close(self.slave_fd)
            self.slave_fd = None
        
        return True
    
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.process is not None and self.process.poll() is None
    
    def close(self) -> bool:
        """Close the PTY session (alias for terminate)"""
        return self.terminate()