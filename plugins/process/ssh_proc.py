"""
SSH subprocess tool - Run SSH commands without PTY
Useful for non-interactive SSH operations
"""

import subprocess
import json
from typing import Dict, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SSHProcTool(BaseTool):
    """SSH client as subprocess (non-PTY)"""
    
    @property
    def name(self) -> str:
        return "ssh-proc"
    
    @property
    def description(self) -> str:
        return "Run SSH command as subprocess (non-interactive)"
    
    @property
    def category(self) -> str:
        return "process"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "SSH host (user@host or host)"
                },
                "command": {
                    "type": "string",
                    "description": "Command to execute on remote host"
                },
                "port": {
                    "type": "number",
                    "description": "SSH port (default: 22)"
                },
                "key_file": {
                    "type": "string",
                    "description": "Path to SSH private key file (optional)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Command timeout in seconds (default: 30)"
                }
            },
            "required": ["host", "command"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute SSH command as subprocess"""
        host = arguments.get("host")
        command = arguments.get("command")
        port = arguments.get("port", 22)
        key_file = arguments.get("key_file")
        timeout = arguments.get("timeout", 30)
        
        # Build SSH command
        ssh_cmd = ["ssh"]
        
        # Add port if not default
        if port != 22:
            ssh_cmd.extend(["-p", str(port)])
        
        # Add key file if specified
        if key_file:
            ssh_cmd.extend(["-i", key_file])
        
        # Add common options for non-interactive use
        ssh_cmd.extend([
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=10"
        ])
        
        # Add host and command
        ssh_cmd.append(host)
        ssh_cmd.append(command)
        
        try:
            # Execute SSH command
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    content=result.stdout,
                    metadata={
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                        "host": host
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    content="",
                    error=f"SSH command failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                content="",
                error=f"SSH command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"SSH execution failed: {str(e)}"
            )