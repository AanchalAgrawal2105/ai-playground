"""Tool Registry - Coordinates all tools"""

import logging
from typing import Any, Dict, Optional

from .analysis import AnalysisTools
from .database import DatabaseTools
from .slack import SlackTools

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all tools.

    This maps tool names (from agent) to actual implementations.
    """

    def __init__(
        self,
        db_url: str,
        slack_token: Optional[str] = None,
        slack_channel: str = "#airflow-monitoring",
        anomaly_multiplier: float = 1.5,
    ):
        """
        Initialize all tools.

        Args:
            db_url: Database connection string
            slack_token: Slack bot token (optional)
            slack_channel: Default Slack channel
            anomaly_multiplier: Anomaly detection threshold
        """
        # Initialize tools
        self.db_tools = DatabaseTools(db_url)
        self.slack_tools = (
            SlackTools(slack_token, slack_channel) if slack_token else None
        )
        self.analysis_tools = AnalysisTools(anomaly_multiplier)

        logger.info("Tool registry initialized")

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        try:
            # Map tool names to implementations
            if tool_name == "query_dag_runs":
                result = self.db_tools.query_dag_runs(**tool_input)
                return {"success": True, "result": result}

            elif tool_name == "analyze_performance_baseline":
                result = self.db_tools.analyze_performance_baseline(**tool_input)
                return {"success": True, "result": result}

            elif tool_name == "get_task_breakdown":
                result = self.db_tools.get_task_breakdown(**tool_input)
                return {"success": True, "result": result}

            elif tool_name == "get_dag_health_summary":
                result = self.db_tools.get_dag_health_summary(**tool_input)
                return {"success": True, "result": result}

            elif tool_name == "send_slack_alert":
                if not self.slack_tools:
                    return {"success": False, "error": "Slack not configured"}
                result = self.slack_tools.send_slack_alert(**tool_input)
                return result

            elif tool_name == "send_health_report":
                if not self.slack_tools:
                    return {"success": False, "error": "Slack not configured"}
                # Extract data, handling anomalies field
                anomalies = tool_input.get(
                    "anomalies", tool_input.get("critical_issues", [])
                )
                result = self.slack_tools.send_health_report(
                    overall_health=tool_input["overall_health"],
                    active_dags=tool_input["active_dags"],
                    critical_issues=tool_input["critical_issues"],
                    failures=tool_input["failures"],
                    anomalies=anomalies,
                    recommendations=tool_input["recommendations"],
                    consistently_failing_dags=tool_input.get(
                        "consistently_failing_dags"
                    ),
                    confidence_level=tool_input.get("confidence_level", "High"),
                    channel=tool_input.get("channel"),
                )
                return result

            elif tool_name == "detect_anomalies":
                # This needs data from previous tool calls
                # Should be handled by orchestrator
                return {
                    "success": False,
                    "error": "detect_anomalies requires orchestrator context",
                }

            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    """Test tool implementations."""
    print("🔧 Tool Implementations Module")
    print("\n✅ Available Tools:")
    print("   1. DatabaseTools - PostgreSQL access")
    print("   2. SlackTools - Slack notifications")
    print("   3. AnalysisTools - Anomaly detection")
    print("   4. ToolRegistry - Unified interface")
    print("\n💡 Ready for orchestrator integration!")
