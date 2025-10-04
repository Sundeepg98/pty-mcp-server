"""
Tmux session management - supports multiple named sessions
"""

import subprocess
import time
from typing import Dict, List, Optional, Any


class TmuxSessionManager:
    """Manages multiple tmux sessions"""

    def __init__(self):
        """Initialize tmux session manager"""
        self.sessions: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def check_tmux_installed() -> bool:
        """Check if tmux is installed"""
        try:
            subprocess.run(["tmux", "-V"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def session_exists(self, session_name: str) -> bool:
        """Check if a tmux session exists"""
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def start_session(self, session_name: str, command: str) -> Dict[str, Any]:
        """
        Start a new detached tmux session

        Args:
            session_name: Unique name for the session
            command: Command to run in the session

        Returns:
            Dict with success status and info
        """
        # Check if session already exists
        if self.session_exists(session_name):
            return {
                "success": False,
                "error": f"Session '{session_name}' already exists"
            }

        # Start new detached session
        result = subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, command],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to create session: {result.stderr}"
            }

        # Track session locally
        self.sessions[session_name] = {
            "command": command,
            "created_at": int(time.time())
        }

        return {
            "success": True,
            "session_name": session_name,
            "command": command,
            "message": f"Started tmux session '{session_name}'"
        }

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active tmux sessions

        Returns:
            List of session info dicts
        """
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}:#{session_created}"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        sessions = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(":")
                if len(parts) >= 2:
                    session_name = parts[0]
                    created = parts[1]

                    # Check if session is attached
                    attached_result = subprocess.run(
                        ["tmux", "list-clients", "-t", session_name],
                        capture_output=True,
                        text=True
                    )
                    is_attached = attached_result.returncode == 0 and attached_result.stdout.strip()

                    sessions.append({
                        "name": session_name,
                        "created_at": created,
                        "attached": is_attached
                    })

        return sessions

    def send_keys(self, session_name: str, keys: str) -> Dict[str, Any]:
        """
        Send keys to a tmux session

        Args:
            session_name: Session to send keys to
            keys: Keys to send (will add Enter automatically)

        Returns:
            Dict with success status
        """
        if not self.session_exists(session_name):
            return {
                "success": False,
                "error": f"Session '{session_name}' not found"
            }

        result = subprocess.run(
            ["tmux", "send-keys", "-t", session_name, keys, "Enter"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to send keys: {result.stderr}"
            }

        return {
            "success": True,
            "message": f"Sent keys to session '{session_name}'"
        }

    def capture_pane(self, session_name: str, lines: Optional[int] = None) -> Dict[str, Any]:
        """
        Capture output from a tmux session pane

        Args:
            session_name: Session to capture from
            lines: Optional number of lines to capture

        Returns:
            Dict with success status and captured output
        """
        if not self.session_exists(session_name):
            return {
                "success": False,
                "error": f"Session '{session_name}' not found"
            }

        cmd = ["tmux", "capture-pane", "-t", session_name, "-p"]
        if lines:
            cmd.extend(["-S", f"-{lines}"])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to capture pane: {result.stderr}"
            }

        return {
            "success": True,
            "output": result.stdout,
            "session_name": session_name
        }

    def get_attach_command(self, session_name: str) -> Dict[str, Any]:
        """
        Get the command to manually attach to a session

        Args:
            session_name: Session name

        Returns:
            Dict with attach command info
        """
        if not self.session_exists(session_name):
            return {
                "success": False,
                "error": f"Session '{session_name}' not found"
            }

        return {
            "success": True,
            "command": f"tmux attach -t {session_name}",
            "session_name": session_name,
            "instructions": "Press Ctrl+B, then D to detach"
        }

    def kill_session(self, session_name: str) -> Dict[str, Any]:
        """
        Kill a tmux session

        Args:
            session_name: Session to kill

        Returns:
            Dict with success status
        """
        if not self.session_exists(session_name):
            return {
                "success": False,
                "error": f"Session '{session_name}' not found"
            }

        result = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Failed to kill session: {result.stderr}"
            }

        # Remove from local tracking
        self.sessions.pop(session_name, None)

        return {
            "success": True,
            "message": f"Killed session '{session_name}'"
        }

    def cleanup_all(self):
        """Clean up all tracked sessions (for shutdown)"""
        # Don't actually kill sessions - they should persist
        # Just clear local tracking
        self.sessions.clear()
