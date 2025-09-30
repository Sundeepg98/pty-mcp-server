"""
Process PowerShell tool - Launch Windows PowerShell
"""

from typing import Dict, Any
import platform

from pty_mcp_server.lib.base import BaseTool, ToolResult

class ProcPsTool(BaseTool):
    """Launch Windows PowerShell as a subprocess"""
    
    @property
    def name(self) -> str:
        return "proc-ps"
    
    @property
    def description(self) -> str:
        return "Launch Windows PowerShell as a subprocess"
    
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
                "no_exit": {
                    "type": "boolean",
                    "description": "Keep PowerShell open after commands (default: true)"
                },
                "execution_policy": {
                    "type": "string",
                    "enum": ["Restricted", "AllSigned", "RemoteSigned", "Unrestricted", "Bypass"],
                    "description": "Execution policy for the session (default: RemoteSigned)"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Spawn Windows PowerShell"""
        if platform.system() != "Windows":
            return ToolResult(
                success=False,
                content="",
                error="proc-ps is only available on Windows. Use 'spawn' with 'bash' on Unix systems."
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
        no_exit = arguments.get("no_exit", True)
        execution_policy = arguments.get("execution_policy", "RemoteSigned")
        
        # Build command
        command = "powershell.exe"
        args = []
        
        # Set execution policy for this session
        args.extend(["-ExecutionPolicy", execution_policy])
        
        # Keep PowerShell open
        if no_exit:
            args.append("-NoExit")
        
        # Interactive mode
        args.append("-Interactive")
        
        try:
            # Spawn the process
            proc_session.spawn(command, args, working_dir)
            
            # Read initial output  
            initial_output = proc_session.read(timeout=2)
            
            result = f"Windows PowerShell started (PID: {proc_session.process.pid})"
            result += f"\nExecution Policy: {execution_policy}"
            
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
                error=f"Failed to spawn PowerShell: {str(e)}"
            )