"""
Airflow Intelligence Agent - Autonomous Airflow Monitoring

A self-contained AI agent for intelligent Airflow pipeline monitoring,
anomaly detection, and optimization recommendations.

This agent replaces the MCP-based approach with true agentic behavior:
- Autonomous investigation and reasoning
- Dynamic tool selection
- Multi-step problem solving
- Interactive conversation
- Context and memory management

Quick Start:
    >>> from agents.airflow_intelligence import create_orchestrator
    >>> orchestrator = create_orchestrator()
    >>> orchestrator.interactive_mode()
"""

__version__ = "2.0.0"
__author__ = "Aanchal Agrawal"

# Import from new modular structure
from .core import (
    AgentConfig,
    AirflowIntelligenceAgent,
    AgentOrchestrator,
    AgentMemory,
    create_orchestrator,
)
from .tools import DatabaseTools, SlackTools, AnalysisTools, ToolRegistry
from .monitoring import ProactiveMonitor, run_proactive_monitor
from .utils import SlackReportFormatter
from .cli import AgentCLI, main as cli_main

# Backwards compatibility - import from old locations
# These will be deprecated in future versions
try:
    from .agent import BaseAgent, create_agent
except ImportError:
    from .core.agent import BaseAgent, create_agent

__all__ = [
    # Core components
    "AgentConfig",
    "AirflowIntelligenceAgent",
    "AgentOrchestrator",
    "AgentMemory",
    "create_orchestrator",
    # Tools
    "DatabaseTools",
    "SlackTools",
    "AnalysisTools",
    "ToolRegistry",
    # Monitoring
    "ProactiveMonitor",
    "run_proactive_monitor",
    # Utils
    "SlackReportFormatter",
    # CLI
    "AgentCLI",
    "cli_main",
    # Backwards compatibility
    "BaseAgent",
    "create_agent",
]
