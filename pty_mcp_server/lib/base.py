"""
Base classes for PTY MCP tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import json


@dataclass
class ToolResult:
    """Standard result format for all tools"""
    success: bool
    content: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_mcp_response(self) -> Dict[str, Any]:
        """Convert to MCP protocol response format"""
        if self.success:
            return {
                "content": [{
                    "type": "text",
                    "text": self.content
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {self.error or self.content}"
                }]
            }


class BaseTool(ABC):
    """Abstract base class for all MCP tools"""

    def __init__(self, session_manager=None):
        """Initialize tool with session manager (injected by ToolRegistry)"""
        self.session_manager = session_manager
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name as it appears in MCP"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Tool category (core, pty, process, network)"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for tool input parameters"""
        pass
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given arguments
        
        Args:
            arguments: Tool-specific arguments
            
        Returns:
            ToolResult with success status and output
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Validate arguments against schema
        
        Returns:
            Error message if validation fails, None if valid
        """
        required = self.input_schema.get("required", [])
        properties = self.input_schema.get("properties", {})
        
        # Check required fields
        for field in required:
            if field not in arguments:
                return f"Missing required field: {field}"
        
        # Check field types (basic validation)
        for field, value in arguments.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type:
                    if expected_type == "string" and not isinstance(value, str):
                        return f"Field '{field}' must be a string"
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        return f"Field '{field}' must be a number"
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        return f"Field '{field}' must be a boolean"
                    elif expected_type == "array" and not isinstance(value, list):
                        return f"Field '{field}' must be an array"
                    elif expected_type == "object" and not isinstance(value, dict):
                        return f"Field '{field}' must be an object"
        
        return None
    
    def to_mcp_definition(self) -> Dict[str, Any]:
        """Convert to MCP tool definition"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }