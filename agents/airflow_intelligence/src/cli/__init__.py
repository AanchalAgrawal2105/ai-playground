"""
Command-Line Interface

User-facing CLI for interacting with the agent:
- Interactive mode
- Mission mode
- Report mode
- Proactive monitoring mode
- Configuration display
- System tests
"""

from .commands import AgentCLI, main

__all__ = [
    "AgentCLI",
    "main",
]
