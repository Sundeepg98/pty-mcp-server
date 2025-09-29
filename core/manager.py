"""
Session Manager - Central coordinator for all session types
"""

import json
from typing import Optional, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.sessions.pty import PTYSession
from core.sessions.process import ProcessSession
from core.sessions.socket import SocketSession
from core.sessions.serial import SerialSession
from lib.config import PtyConfig
from lib.env_manager import ProjectEnvironmentManager


class SessionManager:
    """Manages all active sessions across tools"""
    
    def __init__(self, config=None):
        """Initialize with optional config"""
        # Session storage - only one of each type allowed
        self.pty_session: Optional[PTYSession] = None
        self.proc_session: Optional[ProcessSession] = None
        self.socket_session: Optional[SocketSession] = None
        self.serial_session: Optional[SerialSession] = None
        
        # Project management
        self.active_project: Optional[Dict[str, str]] = None
        self.projects_config: Dict[str, Any] = {}
        
        # Environment manager for project-specific environments
        self.env_manager = ProjectEnvironmentManager()
        
        # Use provided config or create default
        if config is None:
            config = PtyConfig.from_environment()
        self.config = config
        
        # Load configuration
        self._load_projects_config()
        self._load_active_project()
    
    def _load_projects_config(self):
        """Load projects configuration from config object"""
        self.projects_config = self.config.load_projects()
    
    def _load_active_project(self):
        """Load active project from config"""
        self.active_project = self.config.load_active_project()
    
    def save_active_project(self):
        """Save active project using config"""
        if self.active_project:
            self.config.save_active_project(self.active_project)
    
    def get_pty_session(self) -> PTYSession:
        """Get or create PTY session"""
        if not self.pty_session:
            self.pty_session = PTYSession()
        return self.pty_session
    
    def get_proc_session(self) -> ProcessSession:
        """Get or create process session"""
        if not self.proc_session:
            self.proc_session = ProcessSession()
        return self.proc_session
    
    def get_socket_session(self) -> SocketSession:
        """Get or create socket session"""
        if not self.socket_session:
            self.socket_session = SocketSession()
        return self.socket_session
    
    def get_serial_session(self) -> SerialSession:
        """Get or create serial session"""
        if not self.serial_session:
            self.serial_session = SerialSession()
        return self.serial_session
    
    def cleanup_all(self):
        """Clean up all sessions"""
        if self.pty_session:
            self.pty_session.terminate()
        if self.proc_session:
            self.proc_session.terminate()
        if self.socket_session:
            self.socket_session.close()
        if self.serial_session:
            self.serial_session.close()