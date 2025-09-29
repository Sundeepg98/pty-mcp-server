#!/usr/bin/env python3
"""
PTY MCP Server - Main Entry Point
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.registry import ToolRegistry
from core.manager import SessionManager
from lib.base import ToolResult


class MCPServer:
    """Main MCP server orchestrator"""
    
    def __init__(self):
        # Create configuration from environment
        from lib.config import PtyConfig
        self.config = PtyConfig.from_environment()
        
        # Create session manager with config (no circular reference!)
        self.session_manager = SessionManager(self.config)
        self.registry = ToolRegistry(self.session_manager)
        
        # Load all plugins
        self._load_plugins()
    
    def _load_plugins(self):
        """Load all plugins from the plugins directory"""
        base_dir = str(Path(__file__).parent)
        loaded_by_category = self.registry.load_all_plugins(base_dir)
        total_loaded = sum(loaded_by_category.values())
        
        # Simple log
        print(f"[PTY MCP] {total_loaded} tools ready", file=sys.stderr)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method", "")
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return self._handle_initialize(request_id)
            elif method == "tools/list":
                return self._handle_list_tools(request_id)
            elif method == "tools/call":
                return await self._handle_tool_call(request)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
        except Exception as e:
            return self._error_response(request_id, -32603, str(e))
    
    def _handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialization request"""
        capabilities = {
            "tools": {
                "listChanged": True  # Support dynamic tool updates
            }
        }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": capabilities,
                "serverInfo": {
                    "name": "pty-mcp-server",
                    "version": "3.0.0"
                }
            }
        }
    
    def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools list request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.registry.list_tools()
            }
        }
    
    async def _handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution request"""
        request_id = request.get("id")
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Execute tool
        result = self.registry.execute(tool_name, arguments)
        
        # Result is already MCP-formatted
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    def cleanup(self):
        """Clean up resources on shutdown"""
        try:
            # Clean up sessions
            self.session_manager.cleanup_all()
            
            print("[PTY MCP] Shutdown complete", file=sys.stderr)
        except:
            pass


async def main():
    """Main entry point - runs the MCP server"""
    server = MCPServer()
    
    try:
        # Read from stdin, write to stdout (MCP protocol)
        while True:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await server.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
            except Exception as e:
                # Log error but continue
                print(f"[Error] {e}", file=sys.stderr)
    
    except KeyboardInterrupt:
        pass
    finally:
        server.cleanup()


if __name__ == "__main__":
    print("[PTY MCP] Started ✓", file=sys.stderr)
    asyncio.run(main())