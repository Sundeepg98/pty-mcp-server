"""
Configuration management for PTY MCP
"""

import os
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class PtyConfig:
    """Configuration container for PTY MCP"""
    
    # Paths
    base_dir: str
    config_path: str
    state_path: str
    
    # Settings
    default_timeout: float = 0.5
    max_buffer_size: int = 4096
    
    # Project defaults
    default_projects: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize defaults after dataclass creation"""
        if self.default_projects is None:
            self.default_projects = {
                "ics": "/var/projects/ICS",
                "pty-mcp": "/var/projects/mcp-servers/pty-mcp-server",
                "memory-service": "/var/projects/mcp-servers/memory-service"
            }
    
    @classmethod
    def from_environment(cls) -> 'PtyConfig':
        """Create config from environment variables and defaults"""
        base_dir = os.environ.get('PTY_MCP_BASE_DIR', '/home/sundeep/.claude/mcp/pty')
        
        return cls(
            base_dir=base_dir,
            config_path=os.path.join(base_dir, 'config', 'projects.json'),
            state_path=os.path.join(base_dir, '.active_project'),
            default_timeout=float(os.environ.get('PTY_DEFAULT_TIMEOUT', '0.5')),
            max_buffer_size=int(os.environ.get('PTY_MAX_BUFFER', '4096'))
        )
    
    def load_projects(self) -> Dict[str, Any]:
        """Load projects configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Return defaults if file not found
        return {"projects": self.default_projects}
    
    def load_active_project(self) -> Optional[Dict[str, str]]:
        """Load active project state"""
        try:
            with open(self.state_path, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def save_active_project(self, project: Dict[str, str]) -> None:
        """Save active project state"""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w') as f:
                json.dump(project, f)
        except:
            pass