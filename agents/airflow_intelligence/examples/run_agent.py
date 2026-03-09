#!/usr/bin/env python3
"""
Standalone entry point for Airflow Intelligence Agent.

This script provides an easy way to run the agent without module syntax.

Usage:
    cd agents/airflow_intelligence
    python examples/run_agent.py interactive
    python examples/run_agent.py mission "Find slow pipelines"
    python examples/run_agent.py report
    python examples/run_agent.py test
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
