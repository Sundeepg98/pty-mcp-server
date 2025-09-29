#!/usr/bin/env python3
"""
PTY MCP Server - Rewritten with proper MCP SDK
Provides terminal session management for Claude
"""
import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional

# MCP SDK imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import our existing modules
from core.manager import SessionManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("pty-mcp-server")

# Create session manager (will be initialized in main)
session_manager: Optional[SessionManager] = None


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools"""
    tools = []
    
    # Import all plugin modules dynamically
    from plugins.terminal import bash, connect, disconnect, send, clear, resize, ssh, telnet
    from plugins.process import spawn, kill_proc, send_proc, ssh_proc, proc_cmd, proc_ps
    from plugins.system import status, exec, activate, projects, env, file, sessions
    from plugins.network import socket_open, socket_close, socket_write, socket_read, socket_message, socket_telnet
    from plugins.serial import serial_open, serial_close, serial_write, serial_read, serial_message
    
    # Collect all tools
    all_plugins = [
        bash, connect, disconnect, send, clear, resize, ssh, telnet,
        spawn, kill_proc, send_proc, ssh_proc, proc_cmd, proc_ps,
        status, exec, activate, projects, env, file, sessions,
        socket_open, socket_close, socket_write, socket_read, socket_message, socket_telnet,
        serial_open, serial_close, serial_write, serial_read, serial_message
    ]
    
    for plugin in all_plugins:
        if hasattr(plugin, 'TOOL'):
            tool = plugin.TOOL
            tools.append(types.Tool(
                name=tool['name'],
                description=tool.get('description', ''),
                inputSchema=tool.get('inputSchema', {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            ))
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute a tool with given arguments"""
    global session_manager
    
    try:
        # Import plugin modules
        from plugins.terminal import bash, connect, disconnect, send, clear, resize, ssh, telnet
        from plugins.process import spawn, kill_proc, send_proc, ssh_proc, proc_cmd, proc_ps
        from plugins.system import status, exec, activate, projects, env, file, sessions
        from plugins.network import socket_open, socket_close, socket_write, socket_read, socket_message, socket_telnet
        from plugins.serial import serial_open, serial_close, serial_write, serial_read, serial_message
        
        # Map tool names to handlers
        tool_handlers = {
            'bash': bash,
            'connect': connect,
            'disconnect': disconnect,
            'send': send,
            'clear': clear,
            'resize': resize,
            'ssh': ssh,
            'telnet': telnet,
            'spawn': spawn,
            'kill-proc': kill_proc,
            'send-proc': send_proc,
            'ssh-proc': ssh_proc,
            'proc-cmd': proc_cmd,
            'proc-ps': proc_ps,
            'status': status,
            'exec': exec,
            'activate': activate,
            'projects': projects,
            'env': env,
            'file': file,
            'sessions': sessions,
            'socket-open': socket_open,
            'socket-close': socket_close,
            'socket-write': socket_write,
            'socket-read': socket_read,
            'socket-message': socket_message,
            'socket-telnet': socket_telnet,
            'serial-open': serial_open,
            'serial-close': serial_close,
            'serial-write': serial_write,
            'serial-read': serial_read,
            'serial-message': serial_message,
        }
        
        # Get the handler
        handler = tool_handlers.get(name)
        if not handler:
            return [types.TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        
        # Execute the tool
        if hasattr(handler, 'execute'):
            result = await handler.execute(session_manager, arguments)
            return [types.TextContent(
                type="text",
                text=result
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Error: Tool '{name}' has no execute method"
            )]
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point - runs the MCP server with proper stdio handling"""
    global session_manager
    
    try:
        # Initialize session manager
        session_manager = SessionManager()
        logger.info("Session manager initialized")
        
        # Run the server with stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("PTY MCP Server starting with proper MCP SDK...")
            
            # Run the server (simplified - let the server handle initialization)
            await server.run(
                read_stream=read_stream,
                write_stream=write_stream,
                InitializationOptions(
                    server_name="pty-mcp-server",
                    server_version="4.0.0"
                )
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Cleanup
        if session_manager:
            session_manager.cleanup()
            logger.info("Cleanup complete")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())