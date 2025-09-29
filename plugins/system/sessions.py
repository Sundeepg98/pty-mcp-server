"""
List all active sessions tool
"""

import json
import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class SessionsTool(BaseTool):
    """List and manage sessions"""
    
    @property
    def name(self) -> str:
        return "sessions"
    
    @property
    def description(self) -> str:
        return "List all active sessions (PTY, process, socket)"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["json", "table", "summary"],
                    "description": "Output format (default: summary)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """List all sessions"""
        format_type = arguments.get("format", "summary")
        
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="Session manager not available"
            )
        
        sessions = []
        
        # Check PTY session
        if self.session_manager.pty_session:
            pty = self.session_manager.pty_session
            sessions.append({
                "type": "PTY",
                "command": getattr(pty, 'command', 'unknown'),
                "pid": getattr(pty, 'pid', 'unknown'),
                "active": True
            })
        
        # Check process session
        if self.session_manager.proc_session:
            proc = self.session_manager.proc_session
            if hasattr(proc, 'process') and proc.process:
                sessions.append({
                    "type": "Process",
                    "pid": proc.process.pid,
                    "active": proc.process.poll() is None
                })
        
        # Check socket session
        if self.session_manager.socket_session:
            sock = self.session_manager.socket_session
            socket_info = {
                "type": "Socket",
                "active": sock.is_active()
            }
            # Add connection details if available
            if sock.is_active() and hasattr(sock, 'host'):
                socket_info["host"] = getattr(sock, 'host', 'unknown')
                socket_info["port"] = getattr(sock, 'port', 'unknown')
            sessions.append(socket_info)
        
        # Format output
        if format_type == "json":
            content = json.dumps(sessions, indent=2)
        elif format_type == "table":
            if not sessions:
                content = "No active sessions"
            else:
                lines = ["Active Sessions:", "=" * 40]
                for i, session in enumerate(sessions, 1):
                    lines.append(f"{i}. {session['type']} Session")
                    for key, value in session.items():
                        if key != 'type':
                            lines.append(f"   {key}: {value}")
                content = "\n".join(lines)
        else:  # summary
            active_count = len(sessions)
            if active_count == 0:
                content = "No active sessions"
            else:
                types = [s['type'] for s in sessions]
                content = f"{active_count} active session(s): {', '.join(types)}"
        
        return ToolResult(
            success=True,
            content=content
        )