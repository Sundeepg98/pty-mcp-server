"""
Configuration management for PTY MCP Server
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any

@dataclass
class ProjectConfig:
    """Configuration for PTY MCP projects"""
    base_dir: str
    config_path: str
    state_path: str
    projects: Dict[str, str]
    default_project: Optional[str] = None
    active_project: Optional[str] = None

    @classmethod
    def from_environment(cls) -> 'ProjectConfig':
        """Create config from environment variables and defaults"""
        # Use XDG base directory or fallback to ~/.local/share
        xdg_data_home = os.environ.get('XDG_DATA_HOME', 
                                       os.path.expanduser('~/.local/share'))
        base_dir = os.environ.get('PTY_MCP_BASE_DIR', 
                                  os.path.join(xdg_data_home, 'pty-mcp'))
        
        # Ensure directories exist
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        config_dir = Path(base_dir) / 'config'
        config_dir.mkdir(exist_ok=True)
        
        return cls(
            base_dir=base_dir,
            config_path=os.path.join(config_dir, 'projects.json'),
            state_path=os.path.join(base_dir, '.active_project'),
            projects={},
            default_project=None,
            active_project=None
        )

    def load(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', {})
                    self.default_project = data.get('default')
            except (json.JSONDecodeError, IOError):
                # If config is corrupt, start fresh
                self.projects = {}
                self.default_project = None
        
        # Load active project state
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    self.active_project = f.read().strip()
            except IOError:
                self.active_project = None

    def save(self) -> None:
        """Save configuration to file"""
        config_data = {
            'projects': self.projects,
            'default': self.default_project
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Save active project state
        if self.active_project:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w') as f:
                f.write(self.active_project)
