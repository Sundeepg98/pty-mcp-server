"""
Environment variable management tool
"""

import os
import json
from typing import Dict, Any

import sys

from pty_mcp_server.lib.base import BaseTool, ToolResult

class EnvTool(BaseTool):
    """Manage environment variables"""
    
    @property
    def name(self) -> str:
        return "env"
    
    @property
    def description(self) -> str:
        return "Get or set environment variables"
    
    @property
    def category(self) -> str:
        return "system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "set", "list", "unset"],
                    "description": "Action to perform"
                },
                "name": {
                    "type": "string",
                    "description": "Environment variable name"
                },
                "value": {
                    "type": "string",
                    "description": "Value to set (for set action)"
                },
                "filter": {
                    "type": "string",
                    "description": "Filter pattern for list action"
                }
            },
            "required": ["action"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute environment variable operation"""
        action = arguments.get("action")
        name = arguments.get("name", "")
        
        try:
            if action == "get":
                if not name:
                    return ToolResult(
                        success=False,
                        content="",
                        error="Variable name required for get action"
                    )
                value = os.environ.get(name)
                if value is None:
                    return ToolResult(
                        success=False,
                        content="",
                        error=f"Environment variable '{name}' not found"
                    )
                return ToolResult(
                    success=True,
                    content=value
                )
            
            elif action == "set":
                if not name:
                    return ToolResult(
                        success=False,
                        content="",
                        error="Variable name required for set action"
                    )
                value = arguments.get("value", "")
                os.environ[name] = value
                return ToolResult(
                    success=True,
                    content=f"Set {name}={value}"
                )
            
            elif action == "unset":
                if not name:
                    return ToolResult(
                        success=False,
                        content="",
                        error="Variable name required for unset action"
                    )
                if name in os.environ:
                    del os.environ[name]
                    return ToolResult(
                        success=True,
                        content=f"Unset {name}"
                    )
                else:
                    return ToolResult(
                        success=False,
                        content="",
                        error=f"Variable '{name}' not found"
                    )
            
            elif action == "list":
                filter_pattern = arguments.get("filter", "")
                env_vars = {}
                
                for key, value in os.environ.items():
                    if not filter_pattern or filter_pattern.lower() in key.lower():
                        # Truncate very long values
                        if len(value) > 100:
                            value = value[:97] + "..."
                        env_vars[key] = value
                
                if not env_vars:
                    return ToolResult(
                        success=True,
                        content="No matching environment variables found"
                    )
                
                # Sort by key for readability
                sorted_vars = dict(sorted(env_vars.items()))
                return ToolResult(
                    success=True,
                    content=json.dumps(sorted_vars, indent=2)
                )
            
            else:
                return ToolResult(
                    success=False,
                    content="",
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )