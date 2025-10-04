"""
Tmux List tool - List all active tmux sessions
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxListTool(BaseTool):
    """List all active tmux sessions"""

    @property
    def name(self) -> str:
        return "tmux-list"

    @property
    def description(self) -> str:
        return "List all active tmux sessions. Shows session names, creation time, and attachment status."

    @property
    def category(self) -> str:
        return "tmux"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """List tmux sessions"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        try:
            sessions = tmux_manager.list_sessions()

            if not sessions:
                return ToolResult(
                    success=True,
                    content="No active tmux sessions found."
                )

            output = "Active tmux sessions:\n\n"
            for session in sessions:
                status = "🔒 Attached" if session.get("attached") else "🔓 Detached"
                output += f"• {session['name']} - {status}\n"
                output += f"  Created: {session.get('created_at', 'unknown')}\n\n"

            return ToolResult(
                success=True,
                content=output.strip()
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
