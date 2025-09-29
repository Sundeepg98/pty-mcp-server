#!/usr/bin/env python3
"""
PTY MCP Server - MCP SDK Adapter for existing PTY architecture
This preserves all existing tools and just adds proper MCP protocol
"""
import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

# MCP SDK imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import existing PTY architecture
from .core.manager import SessionManager
from .lib.registry import ToolRegistry
from .lib.base import ToolResult

# Set up logging - redirect to file to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('/tmp/pty-mcp.log')]
)
logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("pty-mcp-server")

# Global session manager and registry (initialized in main)
session_manager: Optional[SessionManager] = None
tool_registry: Optional[ToolRegistry] = None

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools from the existing plugin architecture"""
    global tool_registry
    
    if not tool_registry:
        return []
    
    tools = []
    
    # Convert existing tools to MCP format
    for tool_name, tool_instance in tool_registry._tools.items():
        try:
            # Get tool metadata from existing architecture
            mcp_tool = types.Tool(
                name=tool_instance.name,
                description=tool_instance.description,
                inputSchema=tool_instance.input_schema
            )
            tools.append(mcp_tool)
            logger.info(f"Registered tool: {tool_instance.name}")
        except Exception as e:
            logger.error(f"Error registering tool {tool_name}: {e}")
    
    logger.info(f"Listed {len(tools)} tools")
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute a tool using the existing plugin architecture"""
    global tool_registry, session_manager
    
    try:
        if not tool_registry:
            return [types.TextContent(
                type="text",
                text="Error: Tool registry not initialized"
            )]
        
        # Execute using existing tool infrastructure
        result = tool_registry.execute(name, arguments)
        
        if result is None:
            return [types.TextContent(
                type="text",
                text=f"Error: Tool '{name}' not found"
            )]
        
        # Handle different result types
        if isinstance(result, ToolResult):
            # Standard ToolResult from existing architecture
            if result.success:
                return [types.TextContent(
                    type="text",
                    text=result.content
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: {result.error}"
                )]
        elif isinstance(result, dict):
            # Some tools return dicts directly
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            # Plain string result
            return [types.TextContent(
                type="text",
                text=str(result)
            )]
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server"""
    global session_manager, tool_registry
    
    try:
        # Initialize the existing architecture components
        session_manager = SessionManager()
        logger.info("Session manager initialized")
        
        tool_registry = ToolRegistry(session_manager)
        
        # Load all plugins from the existing architecture
        base_dir = Path(__file__).parent
        loaded_categories = tool_registry.load_all_plugins(base_dir)
        
        total_tools = sum(loaded_categories.values())  # values are already counts
        logger.info(f"Loaded {total_tools} tools from {len(loaded_categories)} categories")
        
        for category, count in loaded_categories.items():
            logger.info(f"  {category}: {count} tools")
        
        # Run the MCP server with stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("PTY MCP Server starting with proper MCP SDK...")
            
            # Get server capabilities
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
            
            # Create initialization options with capabilities
            init_options = InitializationOptions(
                server_name="pty-mcp-server",
                server_version="4.0.0",
                capabilities=capabilities
            )
            
            # Run the server with initialization options
            await server.run(
                read_stream,
                write_stream,
                init_options
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise
    finally:
        # Cleanup sessions
        if session_manager:
            try:
                if hasattr(session_manager, 'cleanup'):
                    session_manager.cleanup()
                logger.info("Cleanup complete")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())