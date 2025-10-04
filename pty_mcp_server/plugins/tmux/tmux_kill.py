"""
Tmux Kill tool - Kill a tmux session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxKillTool(BaseTool):
    """Kill a tmux session and stop its process"""

    @property
    def name(self) -> str:
        return "tmux-kill"

    @property
    def description(self) -> str:
        return ("Kill a tmux session and stop its process. "
                "Terminates the session and all processes running in it. "
                "Use this to clean up when done.")

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
                    "description": "Session to kill"
                }
            },
            "required": ["session_name"]
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Kill tmux session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        session_name = arguments.get("session_name")

        try:
            result = tmux_manager.kill_session(session_name)

            if not result["success"]:
                return ToolResult(
                    success=False,
                    content="",
                    error=result.get("error", "Unknown error")
                )

            return ToolResult(
                success=True,
                content=f"✅ Killed session '{session_name}'"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
