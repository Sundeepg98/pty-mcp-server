"""
Session Manager - Domain Service (DDD)

This module implements SessionManager, the core Domain Service that coordinates
all session types in PTY MCP Server.

Domain-Driven Design (DDD) Role:
    - **Layer**: Domain Layer (core/)
    - **Pattern**: Domain Service
    - **Responsibility**: Session lifecycle management and coordination

The SessionManager encapsulates business logic for managing multiple session types
(PTY, process, socket, serial, tmux) while keeping domain concerns separate from
infrastructure and application layers.
"""

import json
from typing import Optional, Dict, Any
import sys
from pathlib import Path

from pty_mcp_server.core.sessions.pty import PTYSession
from pty_mcp_server.core.sessions.process import ProcessSession
from pty_mcp_server.core.sessions.socket import SocketSession
from pty_mcp_server.core.sessions.serial import SerialSession
from pty_mcp_server.core.sessions.tmux import TmuxSessionManager
from pty_mcp_server.lib.config import ProjectConfig
from pty_mcp_server.lib.env_manager import ProjectEnvironmentManager


class SessionManager:
    """
    Domain Service - Coordinates all session types and project context

    **DDD Architecture**:
    - **Type**: Domain Service (orchestrates domain entities)
    - **Injected Into**: ToolRegistry (Application Layer)
    - **Used By**: All 37 tools (Interface Layer)
    - **Manages**: PTYSession, ProcessSession, SocketSession, SerialSession, TmuxSessionManager

    **Session Types**:
    - **Singleton Sessions**: PTY, Process, Socket, Serial (one per type)
    - **Multi-Session Manager**: Tmux (unlimited named sessions)

    **Lazy Initialization**: Sessions created on-demand via get_*_session() methods

    **Dependency Injection**: Injected via constructor into ToolRegistry,
    which propagates it to all tool instances.

    Example:
        >>> session_manager = SessionManager()
        >>> tool_registry = ToolRegistry(session_manager)  # DI here
        >>> # All tools now have access to session_manager
    """

    def __init__(self, config=None):
        """
        Initialize SessionManager with optional configuration

        Args:
            config (ProjectConfig, optional): Project configuration.
                If None, creates default from environment.

        Initializes:
            - All session references to None (lazy initialization)
            - Project environment manager
            - Configuration from environment or provided config
        """
        # Session storage - only one of each type allowed
        self.pty_session: Optional[PTYSession] = None
        self.proc_session: Optional[ProcessSession] = None
        self.socket_session: Optional[SocketSession] = None
        self.serial_session: Optional[SerialSession] = None

        # Tmux session manager - supports multiple named sessions
        self.tmux_manager: Optional[TmuxSessionManager] = None

        # Project management
        self.active_project: Optional[Dict[str, str]] = None
        self.projects_config: Dict[str, Any] = {}

        # Environment manager for project-specific environments
        self.env_manager = ProjectEnvironmentManager()
        
        # Use provided config or create default
        if config is None:
            config = ProjectConfig.from_environment()
        self.config = config
        
        # Load configuration
        self.config.load()
        self.projects_config = self.config.projects

        # Convert loaded project name to dict format
        if self.config.active_project and self.config.active_project in self.projects_config:
            project_name = self.config.active_project
            self.active_project = {
                "name": project_name,
                "path": self.projects_config[project_name]
            }
        else:
            self.active_project = None
    
    def save_active_project(self):
        """Save active project using config"""
        if self.active_project:
            # Save only the project name (string), not the full dict
            project_name = self.active_project.get("name") if isinstance(self.active_project, dict) else self.active_project
            self.config.active_project = project_name
            self.config.save()
    
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

    def get_tmux_manager(self) -> TmuxSessionManager:
        """
        Get or create tmux session manager (lazy initialization)

        Returns:
            TmuxSessionManager: Manager for multiple named tmux sessions

        Note:
            Unlike singleton sessions (PTY, process, socket, serial),
            TmuxSessionManager coordinates multiple concurrent sessions.
        """
        if not self.tmux_manager:
            self.tmux_manager = TmuxSessionManager()
        return self.tmux_manager

    def cleanup_all(self):
        """
        Clean up all active sessions

        Terminates or closes:
            - PTY session (if active)
            - Process session (if active)
            - Socket session (if active)
            - Serial session (if active)
            - All tmux sessions (if tmux manager exists)

        Called when:
            - MCP server shuts down
            - Tests clean up after execution
        """
        if self.pty_session:
            self.pty_session.terminate()
        if self.proc_session:
            self.proc_session.terminate()
        if self.socket_session:
            self.socket_session.close()
        if self.serial_session:
            self.serial_session.close()
        if self.tmux_manager:
            self.tmux_manager.cleanup_all()