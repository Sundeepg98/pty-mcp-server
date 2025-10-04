"""
Tmux Attach tool - Get the command to manually attach to a session
"""

from typing import Dict, Any

from pty_mcp_server.lib.base import BaseTool, ToolResult


class TmuxAttachTool(BaseTool):
    """Get the command to manually attach to a tmux session"""

    @property
    def name(self) -> str:
        return "tmux-attach"

    @property
    def description(self) -> str:
        return ("Get the command to manually attach to a tmux session. "
                "Returns the 'tmux attach' command you can run. "
                "Once attached, use Ctrl+B, D to detach (process keeps running). "
                "This provides TRUE mid-execution backgrounding!")

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
                    "description": "Session to get attach command for"
                }
            },
            "required": ["session_name"]
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get attach command"""
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )

        tmux_manager = self.session_manager.get_tmux_manager()

        session_name = arguments.get("session_name")

        try:
            result = tmux_manager.get_attach_command(session_name)

            if not result["success"]:
                return ToolResult(
                    success=False,
                    content="",
                    error=result.get("error", "Unknown error")
                )

            output = f"""To attach to session '{session_name}', run:

  {result['command']}

Once attached:
• Interact normally with the process
• Press Ctrl+B, then D to detach (process keeps running)
• You can re-attach anytime with the same command

This is TRUE mid-execution backgrounding!"""

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
