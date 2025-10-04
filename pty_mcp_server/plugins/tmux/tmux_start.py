"""
Tmux Start tool - Start a new tmux session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxStartTool(BaseTool):
    """Start a new detached tmux session"""

    @property
    def name(self) -> str:
        return "tmux-start"

    @property
    def description(self) -> str:
        return ("Start a new tmux session with a command. "
                "The session runs in background and can be attached/detached anytime. "
                "Use this for servers, databases, REPLs, or any long-running process. "
                "True mid-execution backgrounding with Ctrl+B, D")

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
                    "description": "Unique name for the tmux session"
                },
                "command": {
                    "type": "string",
                    "description": "Command to run in the session"
                }
            },
            "required": ["session_name", "command"]
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Start a tmux session"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        # Check if tmux is installed
        if not tmux_manager.check_tmux_installed():
            return ToolResult(
                success=False,
                content="",
                error="tmux is not installed. Install with: sudo apt install tmux"
            )

        session_name = arguments.get("session_name")
        command = arguments.get("command")

        try:
            result = tmux_manager.start_session(session_name, command)

            if not result["success"]:
                return ToolResult(
                    success=False,
                    content="",
                    error=result.get("error", "Unknown error")
                )

            output = f"""✅ Started tmux session '{session_name}'

Session: {session_name}
Command: {command}

The process is running in background.
• To attach: tmux attach -t {session_name}
• To detach: Press Ctrl+B, then D
• To capture output: Use tmux-capture tool
• To send commands: Use tmux-send tool"""

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
