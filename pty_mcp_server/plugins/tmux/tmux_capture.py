"""
Tmux Capture tool - Capture output from a tmux session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxCaptureTool(BaseTool):
    """Capture output from a tmux session without attaching"""

    @property
    def name(self) -> str:
        return "tmux-capture"

    @property
    def description(self) -> str:
        return ("Capture output from a tmux session without attaching. "
                "Gets the terminal output from the session's pane. "
                "Useful for checking status, logs, or output of background processes.")

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
                    "description": "Session to capture output from"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of lines to capture (optional, captures all if not specified)"
                }
            },
            "required": ["session_name"]
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Capture pane output"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        session_name = arguments.get("session_name")
        lines = arguments.get("lines")

        try:
            result = tmux_manager.capture_pane(session_name, lines)

            if not result["success"]:
                return ToolResult(
                    success=False,
                    content="",
                    error=result.get("error", "Unknown error")
                )

            output = f"Output from session '{session_name}':\n\n{result['output']}"

            return ToolResult(
                success=True,
                content=output
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
