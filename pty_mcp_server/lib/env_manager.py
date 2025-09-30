"""
Project Environment Manager - Handles project-specific environment loading
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any


class ProjectEnvironmentManager:
    """Manages project-specific environment variables for exec commands"""
    
    def __init__(self):
        """Initialize with base environment"""
        # Store the base environment from when the server started
        self.base_env = os.environ.copy()
        
        # Project-specific environments
        self.project_envs: Dict[str, Dict[str, str]] = {}
        
        # Currently active project
        self.active_project: Optional[str] = None
        
        # Project configurations
        self.project_configs: Dict[str, Any] = {}
    
    def load_project_env(self, project_name: str, project_path: str) -> Dict[str, Any]:
        """
        Load environment variables for a project from its .env file
        
        Args:
            project_name: Name of the project
            project_path: Path to the project directory
            
        Returns:
            Status information about the load operation
        """
        env_loaded = {}
        env_file_path = Path(project_path) / ".env"
        
        # Try to load .env file if it exists
        if env_file_path.exists():
            try:
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            # Parse KEY=VALUE format
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                # Remove quotes if present
                                value = value.strip().strip('"').strip("'")
                                env_loaded[key] = value
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to load .env: {str(e)}",
                    "env_count": 0
                }
        
        # Add project identification variables
        env_loaded["PROJECT_NAME"] = project_name
        env_loaded["PROJECT_PATH"] = project_path
        
        # Store the loaded environment
        self.project_envs[project_name] = env_loaded
        self.active_project = project_name
        
        # Store project config
        self.project_configs[project_name] = {
            "path": project_path,
            "env_file": str(env_file_path),
            "env_count": len(env_loaded)
        }
        
        return {
            "success": True,
            "project": project_name,
            "env_file_found": env_file_path.exists(),
            "env_count": len(env_loaded),
            "env_file": str(env_file_path) if env_file_path.exists() else None
        }
    
    def get_merged_env(self) -> Dict[str, str]:
        """
        Get the merged environment (base + project-specific)
        This is used for exec commands
        
        Returns:
            Merged environment dictionary
        """
        # Start with base environment
        merged = self.base_env.copy()
        
        # If we have an active project, merge its environment
        if self.active_project and self.active_project in self.project_envs:
            project_env = self.project_envs[self.active_project]
            merged.update(project_env)
        
        return merged
    
    def get_project_env(self, project_name: Optional[str] = None) -> Dict[str, str]:
        """
        Get environment variables for a specific project
        
        Args:
            project_name: Name of project, or None for active project
            
        Returns:
            Project environment variables
        """
        if project_name is None:
            project_name = self.active_project
        
        if project_name and project_name in self.project_envs:
            return self.project_envs[project_name]
        
        return {}
    
    def clear_project_env(self, project_name: str):
        """
        Clear cached environment for a project
        
        Args:
            project_name: Name of project to clear
        """
        if project_name in self.project_envs:
            del self.project_envs[project_name]
        
        if project_name in self.project_configs:
            del self.project_configs[project_name]
        
        if self.active_project == project_name:
            self.active_project = None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current environment manager status
        
        Returns:
            Status information
        """
        return {
            "active_project": self.active_project,
            "loaded_projects": list(self.project_envs.keys()),
            "base_env_count": len(self.base_env),
            "active_env_count": len(self.get_project_env()) if self.active_project else 0,
            "configs": self.project_configs
        }