"""
Airflow Intelligence Agent - Autonomous Airflow Monitoring

A self-contained AI agent for intelligent Airflow pipeline monitoring,
anomaly detection, and optimization recommendations.

This agent uses true agentic behavior:
- Autonomous investigation and reasoning
- Dynamic tool selection
- Multi-step problem solving
- Interactive conversation
- Persistent memory and learning

Quick Start:
    >>> from agents.airflow_intelligence import create_orchestrator
    >>> orchestrator = create_orchestrator()
    >>> orchestrator.interactive_mode()
"""

__version__ = "2.0.0"
__author__ = "Aanchal Agrawal"

# Import from src/ package
from .src.core import (
    AgentConfig,
    AirflowIntelligenceAgent,
    AgentOrchestrator,
    AgentMemory,
    create_orchestrator,
)
from .src.core.agent import create_agent
from .src.tools import DatabaseTools, SlackTools, AnalysisTools, ToolRegistry
from .src.monitoring import ProactiveMonitor, run_proactive_monitor
from .src.utils import SlackReportFormatter
from .src.cli import AgentCLI, main as cli_main

__all__ = [
    # Core components
    "AgentConfig",
    "AirflowIntelligenceAgent",
    "AgentOrchestrator",
    "AgentMemory",
    "create_orchestrator",
    "create_agent",
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
]
