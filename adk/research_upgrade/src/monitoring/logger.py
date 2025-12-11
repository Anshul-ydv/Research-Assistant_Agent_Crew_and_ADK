"""
Logging and Monitoring System
"""
import logging
from datetime import datetime
from pathlib import Path

class WorkflowLogger:
    """Advanced logging system for tracking workflow execution."""
    
    def __init__(self, log_file: str = "logs/workflow.log", verbose: bool = False):
        self.log_file = log_file
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Using basic print for simplicity in this environment
        self.verbose = verbose
        print(f"Logging to {log_file}")

    def _log(self, level, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"{timestamp} | {level.upper()} | {message}"
        print(log_message)
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")

    def info(self, message: str):
        self._log("info", message)

    def warning(self, message: str):
        self._log("warning", message)

    def error(self, message: str, exc_info: bool = False):
        self._log("error", message)

    def agent_start(self, agent_name: str, task: str):
        self.info(f"🤖 Agent START: {agent_name} | Task: {task}")

    def agent_complete(self, agent_name: str, status: str, summary: str):
        emoji = "✅" if status == "success" else "❌"
        self.info(f"{emoji} Agent COMPLETE: {agent_name} | Status: {status.upper()} | Output: {summary}")

    def log_error(self, agent_name: str, error: str):
        self.error(f"ERROR in {agent_name}: {error}")