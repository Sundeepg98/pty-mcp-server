"""
List projects tool
"""

import json
from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult

class ProjectsTool(BaseTool):
    """List all registered projects"""
    
    @property
    def name(self) -> str:
        return "projects"
    
    @property
    def description(self) -> str:
        return "List all registered projects"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """List all projects"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        projects = self.session_manager.projects_config.get("projects", {})
        default_project = self.session_manager.projects_config.get("default_project")
        active = self.session_manager.active_project
        
        result = {
            "projects": projects,
            "default": default_project,
            "active": active.get("name") if active else None
        }
        
        return ToolResult(
            success=True,
            content=json.dumps(result, indent=2),
            metadata=result
        )