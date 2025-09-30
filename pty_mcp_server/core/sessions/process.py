"""
Regular process session management (without PTY)
"""

import subprocess
import select
from typing import List, Optional


class ProcessSession:
    """Manages a regular process (without PTY)"""
    
    def __init__(self):
        self.process = None
        
    def start(self, command: str, args: List[str] = None, working_dir: str = None):
        """Start a process"""
        if self.process:
            raise RuntimeError("Process already active")
        
        # Prepare command
        if args:
            cmd_list = [command] + args
        else:
            cmd_list = [command]
        
        self.process = subprocess.Popen(
            cmd_list,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=working_dir,
            text=True,
            bufsize=1
        )
        
        return True
    
    def send(self, data: str):
        """Send data to the process"""
        if not self.process:
            raise RuntimeError("No active process")
        
        self.process.stdin.write(data)
        if not data.endswith('\n'):
            self.process.stdin.write('\n')
        self.process.stdin.flush()
        return True
    
    def read(self, timeout: float = 0.5) -> str:
        """Read from the process"""
        if not self.process:
            raise RuntimeError("No active process")
        
        # Non-blocking read
        output = ""
        while True:
            ready, _, _ = select.select([self.process.stdout], [], [], timeout)
            if not ready:
                break
            line = self.process.stdout.readline()
            if line:
                output += line
            else:
                break
        
        return output
    
    def terminate(self):
        """Terminate the process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        return True
    
    def is_active(self) -> bool:
        """Check if process is active"""
        return self.process is not None and self.process.poll() is None
    
    def close(self) -> bool:
        """Close the process session (alias for terminate)"""
        return self.terminate()