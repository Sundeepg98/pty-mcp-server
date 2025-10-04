"""
Tmux Send tool - Send commands to a tmux session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxSendTool(BaseTool):
    """Send commands to a running tmux session"""

    @property
    def name(self) -> str:
        return "tmux-send"

    @property
    def description(self) -> str:
        return ("Send commands/input to a running tmux session. "
                "Useful for interacting with servers, databases, REPLs without attaching. "
                "Commands are followed by Enter automatically.")

    @property
    def category(self) -> str:
        return "tmux"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_name": {
                    "type": "string",
                    "description": "Target session name"
                },
                "command": {
                    "type": "string",
                    "description": "Command to send to the session"
                }
            },
            "required": ["session_name", "command"]
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Send keys to tmux session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        session_name = arguments.get("session_name")
        command = arguments.get("command")

        try:
            result = tmux_manager.send_keys(session_name, command)

            if not result["success"]:
                return ToolResult(
                    success=False,
                    content="",
                    error=result.get("error", "Unknown error")
                )

            return ToolResult(
                success=True,
                content=f"✅ Sent keys to session '{session_name}'\nSent: {command}"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
