"""
Get status of active sessions and processes
"""

import os
import json
from typing import Dict, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class StatusTool(BaseTool):
    """Get status of active sessions"""
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def description(self) -> str:
        return "Get status of active PTY, process, and socket sessions"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "verbose": {
                    "type": "boolean",
                    "description": "Include detailed information (default: false)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get session status"""
        verbose = arguments.get("verbose", False)
        
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="Session manager not available"
            )
        
        status = {
            "pty_session": None,
            "proc_session": None,
            "socket_session": None,
            "serial_session": None,
            "active_project": self.session_manager.active_project
        }
        
        # Check PTY session
        if self.session_manager.pty_session:
            pty = self.session_manager.pty_session
            if pty.is_active():
                status["pty_session"] = {
                    "active": True,
                    "pid": pty.process.pid if hasattr(pty.process, 'pid') else "unknown"
                }
            else:
                # Session exists but is not active - clear stale reference
                self.session_manager.pty_session = None
                status["pty_session"] = None
        
        # Check process session
        if self.session_manager.proc_session:
            proc = self.session_manager.proc_session
            if proc.is_active():
                status["proc_session"] = {
                    "active": True,
                    "pid": proc.process.pid if hasattr(proc.process, 'pid') else "unknown"
                }
            else:
                # Session exists but is not active - clear stale reference
                self.session_manager.proc_session = None
                status["proc_session"] = None
        
        # Check socket session
        if self.session_manager.socket_session:
            sock = self.session_manager.socket_session
            if sock.is_active():
                status["socket_session"] = {
                    "active": True,
                    "host": getattr(sock, 'host', 'unknown'),
                    "port": getattr(sock, 'port', 'unknown')
                }
            else:
                # Session exists but is not active - clear stale reference
                self.session_manager.socket_session = None
                status["socket_session"] = None
        
        # Check serial session
        if self.session_manager.serial_session:
            serial = self.session_manager.serial_session
            if serial.is_active():
                status["serial_session"] = {
                    "active": True,
                    "device": getattr(serial, 'device', 'unknown'),
                    "baudrate": getattr(serial, 'baudrate', 'unknown')
                }
            else:
                # Session exists but is not active - clear stale reference
                self.session_manager.serial_session = None
                status["serial_session"] = None
        
        # Return as formatted string for better readability
        # Convert None to "none" for cleaner display
        display_status = []
        display_status.append("=== PTY MCP Status ===")
        display_status.append(f"PTY Session: {'Active' if status['pty_session'] else 'None'}")
        display_status.append(f"Process Session: {'Active' if status['proc_session'] else 'None'}")
        display_status.append(f"Socket Session: {'Active' if status['socket_session'] else 'None'}")
        display_status.append(f"Serial Session: {'Active' if status['serial_session'] else 'None'}")
        if status['active_project']:
            display_status.append(f"Active Project: {status['active_project']['name']} ({status['active_project']['path']})")
        else:
            display_status.append("Active Project: None")
        
        return ToolResult(
            success=True,
            content="\n".join(display_status)
        )