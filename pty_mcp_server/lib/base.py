"""
Base Tool Interface - Application Layer (DDD)

This module defines BaseTool, the abstract interface that all MCP tools implement.

Domain-Driven Design (DDD) Role:
    - **Layer**: Application Layer (lib/)
    - **Pattern**: Interface Definition
    - **Responsibility**: Defines tool contract and standard responses

BaseTool serves as the common interface between:
    - Domain Layer (SessionManager)
    - Interface Layer (37 tool implementations in plugins/)
    - Infrastructure Layer (MCP protocol in server.py)

Key Features:
    - 100% Dependency Injection (receives SessionManager via constructor)
    - Standard ToolResult format for all tools
    - MCP protocol conversion (to_mcp_definition, to_mcp_response)
    - Input validation against JSON Schema
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
    """
    Abstract base class for all MCP tools (Interface Layer)

    **DDD Architecture**:
    - **Type**: Interface Definition (contract for all tools)
    - **Implemented By**: 37 tool classes in plugins/ directory
    - **Receives**: SessionManager via constructor (Dependency Injection)

    **100% Dependency Injection Pattern**:
    All tools receive SessionManager through constructor injection:

    Example:
        >>> class MyTool(BaseTool):
        ...     def __init__(self, session_manager=None):
        ...         super().__init__(session_manager)  # DI
        ...
        ...     def execute(self, arguments):
        ...         manager = self.session_manager.get_pty_session()
        ...         return ToolResult(...)

    **Tool Contract**:
    Subclasses must implement:
        - name: Tool identifier
        - description: Human-readable description
        - category: Tool category (terminal, process, network, etc.)
        - input_schema: JSON Schema for parameters
        - execute(arguments): Main tool logic

    **Standard Response**:
    All tools return ToolResult, converted to MCP protocol via to_mcp_response()
    """

    def __init__(self, session_manager=None):
        """
        Initialize tool with dependency injection

        Args:
            session_manager (SessionManager, optional): Domain service injected
                by ToolRegistry during tool instantiation. Provides access to
                all session types (PTY, process, socket, serial, tmux).

        Note:
            This constructor enables 100% Dependency Injection pattern.
            Tools NEVER create SessionManager - it's injected by ToolRegistry.
        """
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