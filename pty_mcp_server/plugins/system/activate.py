"""
Activate project tool
"""

import os
import json
from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class ActivateTool(BaseTool):
    """Activate a project from the registry"""
    
    @property
    def name(self) -> str:
        return "activate"
    
    @property
    def description(self) -> str:
        return "Activate a project from the registry"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Name of the project to activate"
                }
            },
            "required": ["project_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Activate a project"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        project_name = arguments.get("project_name")
        projects = self.session_manager.projects_config.get("projects", {})
        
        if project_name not in projects:
            available = ", ".join(projects.keys())
            return ToolResult(
                success=False,
                content="",
                error=f"Project '{project_name}' not found. Available: {available}"
            )
        
        project_path = projects[project_name]
        
        # Check if path exists
        if not os.path.exists(project_path):
            return ToolResult(
                success=False,
                content="",
                error=f"Project path does not exist: {project_path}"
            )
        
        # Update active project
        self.session_manager.active_project = {
            "name": project_name,
            "path": project_path
        }
        self.session_manager.save_active_project()
        
        # Load project-specific environment
        env_result = self.session_manager.env_manager.load_project_env(
            project_name, project_path
        )
        
        # Change directory
        os.chdir(project_path)
        
        result = {
            "status": "success",
            "project": project_name,
            "path": project_path,
            "environment": {
                "loaded": env_result.get("success", False),
                "env_count": env_result.get("env_count", 0),
                "env_file": env_result.get("env_file"),
                "note": "Environment applies to 'exec' commands only"
            }
        }
        
        return ToolResult(
            success=True,
            content=json.dumps(result, indent=2),
            metadata=result
        )