"""
Process CMD tool - Launch Windows Command Prompt
"""

from typing import Dict, Any
import platform

from pty_mcp_server.lib.base import BaseTool, ToolResult

class ProcCmdTool(BaseTool):
    """Launch Windows Command Prompt (cmd.exe) as a subprocess"""
    
    @property
    def name(self) -> str:
        return "proc-cmd"
    
    @property
    def description(self) -> str:
        return "Launch Windows Command Prompt (cmd.exe) as a subprocess"
    
    @property
    def category(self) -> str:
        return "process"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "working_dir": {
                    "type": "string",
                    "description": "Working directory (optional)"
                },
                "keep_open": {
                    "type": "boolean",
                    "description": "Keep cmd.exe open after commands (default: true)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Spawn Windows Command Prompt"""
        if platform.system() != "Windows":
            return ToolResult(
                success=False,
                content="",
                error="proc-cmd is only available on Windows. Use 'spawn' with 'bash' on Unix systems."
            )
        
        if not self.session_manager:
            return ToolResult(
                success=False,
                content="",
                error="No session manager available"
            )
        
        proc_session = self.session_manager.get_process_session()
        
        # Check if already running
        if proc_session.is_active():
            return ToolResult(
                success=False,
                content="",
                error="Process already running. Kill it first with kill-proc."
            )
        
        working_dir = arguments.get("working_dir")
        keep_open = arguments.get("keep_open", True)
        
        # Build command
        command = "cmd.exe"
        args = []
        
        if keep_open:
            args.append("/K")  # Keep cmd open
        else:
            args.append("/C")  # Close after running
        
        try:
            # Spawn the process
            proc_session.spawn(command, args, working_dir)
            
            # Read initial output
            initial_output = proc_session.read(timeout=1)
            
            result = f"Windows Command Prompt started (PID: {proc_session.process.pid})"
            if initial_output:
                result += f"\n\nInitial output:\n{initial_output}"
            
            return ToolResult(
                success=True,
                content=result
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"Failed to spawn cmd.exe: {str(e)}"
            )