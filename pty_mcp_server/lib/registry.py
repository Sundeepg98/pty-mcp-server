"""
Tool Registry - Application Service (DDD)

This module implements ToolRegistry, the Application Service responsible for
plugin discovery, instantiation, and management.

Domain-Driven Design (DDD) Role:
    - **Layer**: Application Layer (lib/)
    - **Pattern**: Application Service + Factory Pattern
    - **Responsibility**: Tool lifecycle and plugin coordination

ToolRegistry serves as the bridge between:
    - Domain Layer (SessionManager) - Receives via constructor
    - Interface Layer (37 tool plugins) - Discovers and instantiates
    - Infrastructure Layer (MCP protocol) - Provides tool definitions

Key Features:
    - **Dynamic Plugin Discovery**: Scans plugins/ directory at runtime
    - **Factory Pattern**: Creates tool instances with DI
    - **100% Dependency Injection**: Injects SessionManager into all tools
    - **Category Organization**: Manages 6 tool categories
"""

import os
import importlib
import inspect
from typing import Dict, List, Optional, Type
from pathlib import Path

from pty_mcp_server.lib.base import BaseTool, ToolResult


class ToolRegistry:
    """
    Application Service - Tool lifecycle manager with dynamic plugin discovery

    **DDD Architecture**:
    - **Type**: Application Service (orchestrates use cases)
    - **Receives**: SessionManager via constructor (Dependency Injection)
    - **Creates**: All 37 tool instances with DI
    - **Provides**: Tool definitions to MCP protocol layer

    **Factory Pattern with 100% DI**:
    ToolRegistry implements the Factory Pattern to ensure all tools receive
    SessionManager via constructor injection:

    Flow:
        1. server.py creates SessionManager
        2. server.py creates ToolRegistry(session_manager) ← DI here
        3. ToolRegistry.load_all_plugins() discovers tool classes
        4. For each tool class: tool = ToolClass(self.session_manager) ← DI here
        5. All 37 tools now have access to SessionManager

    **Plugin Categories**:
    - terminal (8 tools): PTY, SSH, telnet operations
    - process (6 tools): Subprocess management
    - network (6 tools): Socket operations
    - serial (5 tools): Serial port communication
    - system (6 tools): Environment, file, status
    - tmux (6 tools): Multi-session management

    Example:
        >>> session_manager = SessionManager()
        >>> tool_registry = ToolRegistry(session_manager)
        >>> loaded = tool_registry.load_all_plugins("pty_mcp_server")
        >>> # All 37 tools now loaded with session_manager injected
    """

    def __init__(self, session_manager=None):
        """
        Initialize ToolRegistry with SessionManager dependency

        Args:
            session_manager (SessionManager, optional): Domain service to inject
                into all tool instances. Created in server.py and injected here.

        Note:
            **This is the centralized DI injection point.**
            All tools created by this registry receive this SessionManager instance.
        """
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {}
        self.session_manager = session_manager
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
        
        # Track by category
        category = tool.category
        if category not in self._categories:
            self._categories[category] = []
        if tool.name not in self._categories[category]:
            self._categories[category].append(tool.name)
    
    def register_class(self, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class with Dependency Injection (Factory Pattern)

        Args:
            tool_class (Type[BaseTool]): Tool class to instantiate

        This method implements the Factory Pattern:
            1. Creates tool instance: tool_class(self.session_manager)
            2. Injects SessionManager via constructor ← **DI happens here**
            3. Registers the instantiated tool

        Example:
            >>> registry.register_class(TmuxStartTool)
            >>> # TmuxStartTool now has session_manager injected
        """
        tool_instance = tool_class(self.session_manager)  # ← DI injection point
        self.register(tool_instance)
    
    def load_from_directory(self, directory: str, category: str = None) -> int:
        """
        Load all tool plugins from a directory
        
        Args:
            directory: Path to directory containing .py files
            category: Optional category filter
            
        Returns:
            Number of tools loaded
        """
        loaded_count = 0
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists():
            return 0
        
        # Detect if we're running from a package
        import sys
        is_packaged = 'site-packages' in str(plugin_dir) or '.local' in str(plugin_dir)
        
        if not is_packaged:
            # Running from source - add to path for relative imports
            if str(plugin_dir.parent) not in sys.path:
                sys.path.insert(0, str(plugin_dir.parent))
                        
        for py_file in plugin_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip __init__.py and private files
            
            module_name = py_file.stem
            try:
                # Import the module with correct path
                if is_packaged:
                    # Packaged version - use full module path
                    import_path = f"pty_mcp_server.plugins.{plugin_dir.name}.{module_name}"
                else:
                    # Source version - use relative path
                    import_path = f"{plugin_dir.name}.{module_name}"
                
                module = importlib.import_module(import_path)
                
                # Find all BaseTool subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) 
                        and issubclass(obj, BaseTool) 
                        and obj != BaseTool):
                        
                        # Instantiate and register
                        try:
                            tool = obj(self.session_manager)
                            if category is None or tool.category == category:
                                self.register(tool)
                                loaded_count += 1
                        except Exception as e:
                            print(f"Error loading tool {name}: {e}")
            
            except Exception as e:
                print(f"Error loading module {module_name} from {import_path}: {e}")
        
        return loaded_count
    
    def load_all_plugins(self, base_dir: str) -> Dict[str, int]:
        """
        Load all plugins from standard directory structure
        
        Args:
            base_dir: Base directory containing plugins/ folder
            
        Returns:
            Dictionary of category -> count of tools loaded
        """
        counts = {}
        plugins_dir = Path(base_dir) / "plugins"
        
        for category_dir in plugins_dir.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                count = self.load_from_directory(str(category_dir), category)
                counts[category] = count
        
        return counts
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools in MCP format"""
        return [tool.to_mcp_definition() for tool in self._tools.values()]
    
    def list_by_category(self, category: str) -> List[str]:
        """List tool names in a specific category"""
        return self._categories.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return list(self._categories.keys())
    
    def execute(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Execute a tool by name
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            MCP-formatted response
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Tool '{tool_name}' not found"
                }]
            }
        
        # Validate arguments
        error = tool.validate_arguments(arguments)
        if error:
            return {
                "content": [{
                    "type": "text", 
                    "text": f"Invalid arguments: {error}"
                }]
            }
        
        # Execute tool
        try:
            result = tool.execute(arguments)
            return result.to_mcp_response()
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }]
            }
    
    def __len__(self) -> int:
        """Get count of registered tools"""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered"""
        return tool_name in self._tools