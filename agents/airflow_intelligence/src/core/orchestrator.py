"""
Agent Orchestrator - Wires Agent + Tools Together

This module is the "glue" that connects the agent's reasoning with tool execution.
It implements the complete agent loop with real tool execution.

Key responsibilities:
1. Manage agent lifecycle
2. Execute tools when agent requests them
3. Return results back to agent
4. Handle errors gracefully
5. Support both interactive and automated modes
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..tools import AnalysisTools, DatabaseTools, SlackTools, ToolRegistry
from .agent import AirflowIntelligenceAgent, create_agent
from .config import AgentConfig
from .memory import AgentMemory

# Set up logging
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the AI agent's autonomous workflow.

    This is the "brain coordinator" that:
    - Manages the agent instance
    - Executes tools the agent requests
    - Handles the complete reasoning loop
    - Provides both mission and interactive modes
    """

    def __init__(self, config: AgentConfig, max_iterations: int = 10):
        """
        Initialize the orchestrator with configuration.

        Args:
            config: AgentConfig instance with all settings
            max_iterations: Maximum reasoning iterations for the agent (default: 10)
        """
        self.config = config

        # Initialize the agent
        logger.info("Initializing AI agent...")
        self.agent = create_agent(model_id=config.model_id, region=config.aws_region)

        # Override max_iterations if specified
        self.agent.max_iterations = max_iterations

        # Initialize tools
        logger.info("Initializing tool registry...")
        self.tool_registry = ToolRegistry(
            db_url=config.airflow_db_url,
            slack_token=config.slack_token if config.enable_slack else None,
            slack_channel=config.slack_channel,
            anomaly_multiplier=config.anomaly_multiplier,
        )

        # Initialize long-term memory system
        logger.info("Initializing agent memory...")
        self.memory = AgentMemory()

        # Store data for detect_anomalies (needs context from previous calls)
        self._context_cache: Dict[str, Any] = {"recent_runs": None, "baselines": None}

        logger.info("Orchestrator initialized successfully")

    def execute_mission(
        self, objective: str, show_reasoning: bool = True, return_details: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a mission - give the agent an objective and let it work autonomously.

        Examples of objectives:
        - "Find performance anomalies in the last 24 hours"
        - "Investigate why the ETL pipeline is slow"
        - "Generate a health report and send to Slack"

        Args:
            objective: The goal for the agent to achieve
            show_reasoning: Whether to print agent's reasoning steps
            return_details: Whether to return detailed execution info

        Returns:
            Dictionary with agent response and optional execution details
        """
        if show_reasoning:
            print(f"\n{'='*80}")
            print(f"🎯 Mission: {objective}")
            print(f"{'='*80}\n")

        try:
            # Run the agent loop with tool execution
            response_text = self._run_agent_loop(objective, show_reasoning)

            result = {
                "success": True,
                "objective": objective,
                "response": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if return_details:
                result.update(
                    {
                        "tools_used": self.agent.working_memory.get("tools_used", []),
                        "iterations": self.agent.working_memory.get(
                            "iteration_count", 0
                        ),
                        "findings": self.agent.working_memory.get("findings", {}),
                    }
                )

            return result

        except Exception as e:
            error_msg = f"Mission execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            return {
                "success": False,
                "objective": objective,
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _run_agent_loop(self, user_message: str, show_reasoning: bool) -> str:
        """
        Run the agent loop with real tool execution.

        This is the core orchestration logic that:
        1. Gives message to agent
        2. Agent thinks and may request tools
        3. We execute the requested tools
        4. Return results to agent
        5. Agent thinks again
        6. Repeat until agent has final answer

        Args:
            user_message: User's message or objective
            show_reasoning: Whether to show reasoning steps

        Returns:
            Agent's final response text
        """
        # Add user message to agent's conversation history
        self.agent.conversation_history.append(
            {"role": "user", "content": [{"text": user_message}]}
        )

        # Reset context cache for new mission
        self._context_cache = {"recent_runs": None, "baselines": None}

        # THE ORCHESTRATION LOOP
        for iteration in range(self.agent.max_iterations):
            self.agent.working_memory["iteration_count"] = iteration + 1

            if show_reasoning:
                print(
                    f"🤔 Agent thinking (iteration {iteration + 1}/{self.agent.max_iterations})..."
                )

            try:
                # Agent thinks (calls Bedrock)
                response = self.agent._call_bedrock()

                # Check if agent wants to use tools
                if self.agent._has_tool_use(response):
                    if show_reasoning:
                        print(f"🔧 Agent decided to use tools...")

                    # Store the assistant's tool-use message in history FIRST
                    self.agent.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response["output"]["message"]["content"],
                        }
                    )

                    # Extract tool use requests from response
                    tool_results = self._execute_tools_from_response(
                        response, show_reasoning
                    )

                    # Add tool results to agent's conversation
                    self.agent._add_tool_results(tool_results)

                    # Continue loop - agent will think again with new data
                    continue

                else:
                    # Agent has final answer
                    final_text = self.agent._extract_response_text(response)

                    if show_reasoning:
                        print(
                            f"\n✅ Agent reached conclusion after {iteration + 1} iterations"
                        )
                        print(
                            f"🛠️  Tools used: {len(self.agent.working_memory['tools_used'])}"
                        )
                        print(f"{'='*80}\n")

                    # Store assistant's response in history
                    self.agent.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response["output"]["message"]["content"],
                        }
                    )

                    return final_text

            except Exception as e:
                logger.error(f"Error in orchestration loop iteration {iteration}: {e}")
                if show_reasoning:
                    print(f"❌ Error: {e}")
                raise

        # Max iterations reached
        warning = f"Reached maximum iterations ({self.agent.max_iterations})"
        logger.warning(warning)
        return warning

    MAX_RESULT_ITEMS = 50
    MAX_RESULT_JSON_CHARS = 30_000

    def _truncate_tool_result(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Truncate large tool results to stay within model context limits.

        Caps list results and trims oversized JSON payloads so that
        the conversation history doesn't exceed the model's input window.
        """
        result = tool_result.copy()
        data = result.get("result")

        if isinstance(data, list) and len(data) > self.MAX_RESULT_ITEMS:
            total = len(data)
            result["result"] = data[: self.MAX_RESULT_ITEMS]
            result["truncated"] = True
            result["total_count"] = total
            result["shown_count"] = self.MAX_RESULT_ITEMS
            logger.info(
                f"Truncated result list from {total} to {self.MAX_RESULT_ITEMS} items"
            )

        payload = json.dumps(result, default=str)
        if len(payload) > self.MAX_RESULT_JSON_CHARS:
            result = {
                "success": result.get("success", True),
                "summary": f"Result too large ({len(payload)} chars). "
                f"Returned {result.get('total_count') or result.get('count', '?')} items. "
                "Ask a more targeted question or filter by dag_id.",
                "truncated": True,
            }
            logger.info("Truncated oversized JSON payload to summary")

        return result

    def _execute_tools_from_response(
        self, response: Dict[str, Any], show_reasoning: bool
    ) -> List[Dict[str, Any]]:
        """
        Execute tools requested by the agent.

        This is where we actually call the tool implementations!

        Args:
            response: Bedrock response containing tool use requests
            show_reasoning: Whether to show reasoning

        Returns:
            List of tool results in Bedrock format
        """
        content = response.get("output", {}).get("message", {}).get("content", [])
        tool_results = []

        for item in content:
            if isinstance(item, dict) and "toolUse" in item:
                tool_use = item["toolUse"]
                tool_name = tool_use.get("name", "unknown")
                tool_input = tool_use.get("input", {})
                tool_use_id = tool_use.get("toolUseId", "unknown")

                if show_reasoning:
                    print(f"   📞 Calling: {tool_name}")
                    print(f"      Parameters: {json.dumps(tool_input, indent=6)}")

                # Track tool usage
                self.agent.working_memory["tools_used"].append(
                    {
                        "name": tool_name,
                        "input": tool_input,
                        "iteration": self.agent.working_memory["iteration_count"],
                    }
                )

                # EXECUTE THE TOOL (This is the key part!)
                tool_result = self._execute_single_tool(
                    tool_name, tool_input, show_reasoning
                )

                # Truncate large results to prevent context overflow
                tool_result = self._truncate_tool_result(tool_result)

                # Format result for Bedrock
                tool_results.append(
                    {"toolUseId": tool_use_id, "content": [{"json": tool_result}]}
                )

        return tool_results

    def _execute_single_tool(
        self, tool_name: str, tool_input: Dict[str, Any], show_reasoning: bool
    ) -> Dict[str, Any]:
        """
        Execute a single tool and return results.

        This handles the special case of detect_anomalies which needs
        data from previous tool calls (recent_runs + baselines).

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            show_reasoning: Whether to show execution details

        Returns:
            Tool execution result
        """
        try:
            # Special handling for detect_anomalies
            if tool_name == "detect_anomalies":
                # This tool needs data from previous calls
                result = self._execute_detect_anomalies(tool_input)

            # Memory tools
            elif tool_name == "recall_historical_context":
                dag_id = tool_input.get("dag_id")
                context = self.memory.get_dag_context(dag_id)
                result = {
                    "success": True,
                    "result": context,
                    "message": f"Retrieved historical context for {dag_id}",
                }

            elif tool_name == "store_incident":
                incident_id = self.memory.store_incident(
                    dag_id=tool_input.get("dag_id"),
                    issue_type=tool_input.get("issue_type"),
                    root_cause=tool_input.get("root_cause"),
                    resolution=tool_input.get("resolution"),
                    severity=tool_input.get("severity", "medium"),
                )
                result = {
                    "success": True,
                    "result": {
                        "incident_id": incident_id,
                        "message": "Incident stored in long-term memory for future reference",
                    },
                }

            elif tool_name == "analyze_failure_patterns":
                dag_id = tool_input.get("dag_id")
                schedule_type = tool_input.get("schedule_type", "daily")
                analysis = self.memory.analyze_failure_patterns(dag_id, schedule_type)
                result = {
                    "success": True,
                    "result": analysis,
                    "message": f"Failure pattern analysis complete for {dag_id}",
                }

            else:
                # Execute tool via registry
                result = self.tool_registry.execute(tool_name, tool_input)

                # Cache results for detect_anomalies
                if tool_name == "query_dag_runs" and result.get("success"):
                    self._context_cache["recent_runs"] = result.get("result", [])
                elif tool_name == "analyze_performance_baseline" and result.get(
                    "success"
                ):
                    self._context_cache["baselines"] = result.get("result", [])

            if show_reasoning:
                if result.get("success"):
                    result_count = (
                        len(result.get("result", []))
                        if isinstance(result.get("result"), list)
                        else 1
                    )
                    print(f"      ✅ Success: {result_count} results")
                else:
                    print(f"      ❌ Error: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            logger.error(f"{tool_name} failed: {error_msg}")
            return {"success": False, "error": error_msg}

    def _execute_detect_anomalies(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute anomaly detection using cached data from previous tool calls.

        Args:
            tool_input: Parameters for anomaly detection

        Returns:
            Anomaly detection results
        """
        try:
            recent_runs = self._context_cache.get("recent_runs")
            baselines = self._context_cache.get("baselines")

            if not recent_runs or not baselines:
                return {
                    "success": False,
                    "error": "Missing data: Agent must call query_dag_runs and analyze_performance_baseline first",
                }

            # Execute anomaly detection
            anomalies = self.tool_registry.analysis_tools.detect_anomalies(
                recent_runs=recent_runs,
                baselines=baselines,
                sensitivity=tool_input.get("sensitivity", "medium"),
                focus_area=tool_input.get("focus_area", "duration"),
            )

            return {"success": True, "result": anomalies, "count": len(anomalies)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def interactive_mode(self):
        """
        Run the agent in interactive chat mode.

        This allows users to have a conversation with the agent,
        asking questions and getting intelligent responses.
        """
        print("\n" + "=" * 80)
        print("🤖 Airflow Intelligence Agent - Interactive Mode")
        print("=" * 80)
        print(
            "\nI'm an autonomous AI agent that can investigate your Airflow pipelines!"
        )
        print("\n💡 Example questions:")
        print("   • 'What DAGs failed in the last 24 hours?'")
        print("   • 'Investigate the performance of etl_daily pipeline'")
        print("   • 'Find slow running pipelines and send report to Slack'")
        print("   • 'Give me a health summary of all pipelines'")
        print("\n📝 Commands:")
        print("   • 'reset' - Clear conversation history")
        print("   • 'exit' or 'quit' - Exit interactive mode")
        print("\n" + "=" * 80 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye! Thanks for using Airflow Intelligence Agent!")
                    break

                if user_input.lower() == "reset":
                    self.agent.reset_conversation()
                    self._context_cache = {"recent_runs": None, "baselines": None}
                    print("✅ Conversation reset. Starting fresh!\n")
                    continue

                # Execute mission
                result = self.execute_mission(
                    objective=user_input,
                    show_reasoning=False,  # Less verbose in interactive mode
                )

                # Display response
                if result["success"]:
                    print(f"\n🤖 Agent:\n{result['response']}\n")
                else:
                    print(f"\n❌ Error: {result.get('error', 'Unknown error')}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
                print(f"\n❌ Error: {str(e)}\n")

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate an automated monitoring report.

        This is the equivalent of the old MCP-based scheduled job,
        but with agentic intelligence instead of fixed workflow.

        Note: Comprehensive reports may need more iterations than default.
        If the agent is analyzing multiple failed DAGs, it may hit the iteration
        limit. The orchestrator is configured with appropriate max_iterations.

        Returns:
            Report generation result
        """
        objective = (
            "Analyze the last 24 hours of Airflow pipeline execution. "
            "Identify any performance anomalies, failures, or concerning patterns. "
            "Focus on CRITICAL and CHRONIC failures (use analyze_failure_patterns). "
            "Generate a comprehensive health report with prioritized recommendations. "
            "If you find critical chronic failures, send an alert to Slack using send_health_report. "
            "Be efficient: analyze patterns for top priority failures first, don't analyze every single failure individually."
        )

        return self.execute_mission(
            objective=objective, show_reasoning=True, return_details=True
        )

    def reset(self):
        """Reset agent state and clear caches."""
        self.agent.reset_conversation()
        self._context_cache = {"recent_runs": None, "baselines": None}
        logger.info("Orchestrator reset complete")


def create_orchestrator(
    config: Optional[AgentConfig] = None, max_iterations: int = 10
) -> AgentOrchestrator:
    """
    Factory function to create an orchestrator.

    Args:
        config: Optional AgentConfig. If None, loads from environment.
        max_iterations: Maximum reasoning iterations (default: 10)
                       Use higher values (15-20) for comprehensive reports

    Returns:
        Configured AgentOrchestrator instance
    """
    if config is None:
        config = AgentConfig.from_env()

    # Validate configuration
    errors = config.validate()
    if errors:
        error_msg = f"Configuration validation failed: {', '.join(errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return AgentOrchestrator(config, max_iterations=max_iterations)


if __name__ == "__main__":
    """
    Test the orchestrator.

    This demonstrates the complete agent system in action.
    """
    print("🤖 Airflow Intelligence Agent - Orchestrator Test\n")

    try:
        # Create orchestrator (requires valid config)
        print("Initializing orchestrator...")
        orchestrator = create_orchestrator()

        print("✅ Orchestrator created successfully!")
        print(f"   Agent model: {orchestrator.config.model_id}")
        print(f"   Database: Connected")
        print(
            f"   Slack: {'Enabled' if orchestrator.config.enable_slack else 'Disabled'}"
        )

        print("\n📋 Available modes:")
        print("   1. execute_mission(objective) - Single objective execution")
        print("   2. interactive_mode() - Chat with the agent")
        print("   3. generate_report() - Automated monitoring report")

        print("\n💡 Example usage:")
        print("   orchestrator.execute_mission('Find failed DAGs')")
        print("   orchestrator.interactive_mode()")

        print("\n✅ Ready to use!")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure your .env file is configured correctly.")
        print("   Required: AIRFLOW_DB_URL")
        print("   Optional: AWS credentials, SLACK_BOT_TOKEN")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Check your configuration and try again.")
