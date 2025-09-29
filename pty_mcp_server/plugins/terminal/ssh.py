"""
SSH tool - SSH connections via PTY
"""

from typing import Dict, Any

import sys
from pathlib import Path
# Add parent directory dynamically
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SSHTool(BaseTool):
    """Connect to remote host via SSH"""
    
    @property
    def name(self) -> str:
        return "ssh"
    
    @property
    def description(self) -> str:
        return "Connect to a remote host via SSH"
    
    @property
    def category(self) -> str:
        return "terminal"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "SSH host to connect to"
                },
                "user": {
                    "type": "string",
                    "description": "SSH username"
                },
                "port": {
                    "type": "number",
                    "description": "SSH port (default: 22)"
                },
                "key_file": {
                    "type": "string",
                    "description": "Path to SSH private key file (optional)"
                }
            },
            "required": ["host"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Start SSH session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        pty_session = self.session_manager.get_pty_session()
        
        # Check if already active
        if pty_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="PTY session already active. Disconnect first."
            )
        
        host = arguments.get("host")
        user = arguments.get("user", "")
        port = arguments.get("port", 22)
        key_file = arguments.get("key_file")
        
        # Build SSH command
        ssh_cmd = "ssh"
        ssh_args = [
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-p", str(port)
        ]
        
        if key_file:
            ssh_args.extend(["-i", key_file])
        
        # Add user@host
        if user:
            ssh_args.append(f"{user}@{host}")
        else:
            ssh_args.append(host)
        
        try:
            pty_session.start(ssh_cmd, ssh_args)
            
            # Read initial output
            output = pty_session.read(timeout=2.0)
            
            return ToolResult(
                success=True,
                content=f"SSH session started to {user}@{host}:{port}\n{output}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )