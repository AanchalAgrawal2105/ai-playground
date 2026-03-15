"""
Entry point for running the agent as a module.

Usage:
    python -m agents.airflow_intelligence interactive
    python -m agents.airflow_intelligence mission "Your objective"
    python -m agents.airflow_intelligence report
"""

from .cli import main

if __name__ == "__main__":
    exit(main())
