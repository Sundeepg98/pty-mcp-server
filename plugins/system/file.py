"""
File operations tool - Read, Write, List files
WITH SAFETY CHECKS
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.base import BaseTool, ToolResult


class FileTool(BaseTool):
    """Simple file operations with safety checks"""
    
    @property
    def name(self) -> str:
        return "file"
    
    @property
    def description(self) -> str:
        return "File operations: read, write, list, delete"
    
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
                    "enum": ["read", "write", "list", "delete", "exists"],
                    "description": "File operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path (relative to active project)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write action)"
                },
                "force": {
                    "type": "boolean",
                    "description": "Force overwrite existing files (default: false)",
                    "default": False
                }
            },
            "required": ["action", "path"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute file operation"""
        action = arguments.get("action", "")
        path = arguments.get("path", "")
        
        # Use active project as base if path is relative
        if not os.path.isabs(path) and self.session_manager and self.session_manager.active_project:
            base_path = self.session_manager.active_project.get("path", "")
            path = os.path.join(base_path, path)
        
        try:
            if action == "read":
                with open(path, 'r') as f:
                    content = f.read()
                return ToolResult(success=True, content=content)
            
            elif action == "write":
                content = arguments.get("content", "")
                force = arguments.get("force", False)
                
                # Safety check: warn if file exists
                file_exists = os.path.exists(path)
                
                if file_exists and not force:
                    # File exists and force not specified - require confirmation
                    file_size = os.path.getsize(path)
                    return ToolResult(
                        success=False,
                        content="",
                        error=f"File already exists at {path} ({file_size} bytes). Use 'force': true to overwrite, or use Claude's Edit tool for safe modifications."
                    )
                
                # Write the file
                with open(path, 'w') as f:
                    f.write(content)
                
                # Return appropriate message
                if file_exists:
                    return ToolResult(success=True, content=f"File overwritten at {path}")
                else:
                    return ToolResult(success=True, content=f"File created at {path}")
            
            elif action == "list":
                if os.path.isdir(path):
                    files = os.listdir(path)
                    return ToolResult(success=True, content="\n".join(files))
                else:
                    return ToolResult(success=False, content="", error=f"Not a directory: {path}")
            
            elif action == "delete":
                if os.path.exists(path):
                    os.remove(path)
                    return ToolResult(success=True, content=f"Deleted {path}")
                else:
                    return ToolResult(success=False, content="", error=f"File not found: {path}")
            
            elif action == "exists":
                exists = os.path.exists(path)
                return ToolResult(success=True, content=str(exists))
            
            else:
                return ToolResult(success=False, content="", error=f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))