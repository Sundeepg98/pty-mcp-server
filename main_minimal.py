#!/usr/bin/env python3
"""
PTY MCP Server - Minimal working version with exec tool
"""
import os
import sys
import json
import asyncio
import logging
import subprocess
from typing import Any, Dict, List, Optional

# MCP SDK imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Set up logging - redirect to file to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('/tmp/pty-mcp.log')]
)
logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("pty-mcp-server")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools"""
    return [
        types.Tool(
            name="exec",
            description="Execute a shell command and return structured output",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in seconds (default: 30)"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory (optional)"
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="bash",
            description="Start an interactive bash shell in PTY",
            inputSchema={
                "type": "object",
                "properties": {
                    "working_dir": {
                        "type": "string",
                        "description": "Initial working directory"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="status",
            description="Get status of PTY server",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute a tool with given arguments"""
    
    try:
        if name == "exec":
            command = arguments.get("command")
            timeout = arguments.get("timeout", 30)
            working_dir = arguments.get("working_dir", os.getcwd())
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "cwd": working_dir
                }, indent=2)
            )]
            
        elif name == "bash":
            return [types.TextContent(
                type="text",
                text="Bash PTY session would start here (not implemented in minimal version)"
            )]
            
        elif name == "status":
            return [types.TextContent(
                type="text",
                text="PTY MCP Server (minimal version) is running with MCP SDK"
            )]
            
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except subprocess.TimeoutExpired:
        return [types.TextContent(
            type="text",
            text=f"Error: Command timed out after {timeout} seconds"
        )]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server"""
    try:
        logger.info("PTY MCP Server (minimal) starting...")
        
        # Run the server with stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("PTY MCP Server running with proper MCP SDK...")
            
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
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())