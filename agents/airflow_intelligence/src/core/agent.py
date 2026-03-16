"""
Airflow Intelligence Agent - Core Implementation

This module implements the autonomous AI agent for Airflow monitoring.
It demonstrates the 4 pillars of agentic AI:
1. Tool Use - AI calls functions to perform actions
2. Reasoning Loop - Multi-step autonomous problem solving
3. System Prompts - Defines agentic behavior
4. Memory - Context across interactions
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

from .llm_provider import LLMProvider

if TYPE_CHECKING:
    from .config import AgentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base AI Agent with tool use capabilities (provider-agnostic).

    This class implements the core agent loop:
    - Conversation management (memory)
    - Tool use pattern (actions)
    - Autonomous reasoning (agent loop)

    Works with any LLM provider (AWS Bedrock, Anthropic API, OpenAI, etc.)

    Subclasses must implement:
    - get_system_prompt(): Define agent's behavior
    - get_tools(): Define available tools
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        max_iterations: int = 10,
    ):
        """
        Initialize the agent.

        Args:
            llm_provider: LLM provider instance (Bedrock, Anthropic, OpenAI, etc.)
            max_iterations: Max reasoning loops (prevents infinite loops)
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations

        logger.info(
            f"Initialized agent with provider: {llm_provider.__class__.__name__}"
        )
        logger.info(f"Model: {llm_provider.model_id}")

        # Memory: Conversation history (all messages)
        self.conversation_history: List[Dict[str, Any]] = []

        # Memory: Working memory (current findings)
        self.working_memory: Dict[str, Any] = {
            "tools_used": [],
            "findings": {},
            "iteration_count": 0,
        }

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Define the agent's persona, capabilities, and behavior.

        This is where you set the "DNA" of your agent.
        A good system prompt makes the AI act autonomously.
        """
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define tools the agent can use.

        Returns list of tool specifications in Bedrock format.
        Each tool has:
        - name: Tool identifier
        - description: When to use it (AI reads this!)
        - inputSchema: Parameters specification
        """
        pass

    def think(self, user_message: str, show_reasoning: bool = True) -> str:
        """
        Core agent reasoning loop - THE HEART OF THE AGENT!

        This is where the "agentic" behavior happens:
        1. User gives a message/objective
        2. Agent thinks about it
        3. Agent decides to use tools (or not)
        4. Agent analyzes results
        5. Agent decides: need more info? Or ready to answer?
        6. Repeat until objective achieved

        Args:
            user_message: User's question or objective
            show_reasoning: Print agent's reasoning steps

        Returns:
            Agent's final response (as text)
        """
        # Add user message to conversation history
        self.conversation_history.append(
            {"role": "user", "content": [{"text": user_message}]}
        )

        if show_reasoning:
            print(f"\n{'='*80}")
            print(f"🎯 Objective: {user_message}")
            print(f"{'='*80}\n")

        # Reset working memory for new conversation turn
        self.working_memory["iteration_count"] = 0
        self.working_memory["tools_used"] = []

        # THE AGENT LOOP
        # This is what makes it "agentic" - it loops until done
        for iteration in range(self.max_iterations):
            self.working_memory["iteration_count"] = iteration + 1

            if show_reasoning:
                print(
                    f"🤔 Agent thinking (iteration {iteration + 1}/{self.max_iterations})..."
                )

            try:
                # Call LLM provider with tool configuration
                response = self._call_llm()

                # Check if agent wants to use tools
                if self._has_tool_use(response):
                    # Agent decided to use tools
                    if show_reasoning:
                        print("🔧 Agent decided to use tools...")

                    # Store the assistant's tool-use message in history FIRST
                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response["output"]["message"]["content"],
                        }
                    )

                    # Execute the tools agent requested
                    tool_results = self._execute_tools(response, show_reasoning)

                    # Add results back to conversation
                    self._add_tool_results(tool_results)

                    # Loop continues - agent will think again with new info
                    continue

                else:
                    # Agent has final answer (no more tools needed)
                    final_text = self._extract_response_text(response)

                    if show_reasoning:
                        print(
                            f"\n✅ Agent reached conclusion after {iteration + 1} iterations"
                        )
                        print(
                            f"🛠️  Tools used: {len(self.working_memory['tools_used'])}"
                        )
                        print(f"{'='*80}\n")

                    # Store assistant's response in history
                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response["output"]["message"]["content"],
                        }
                    )

                    return final_text

            except Exception as e:
                logger.error(f"Error in agent loop iteration {iteration}: {e}")
                if show_reasoning:
                    print(f"❌ Error: {e}")
                return f"I encountered an error: {str(e)}"

        # Max iterations reached
        warning = f"Reached maximum iterations ({self.max_iterations}). Agent may need more steps."
        logger.warning(warning)
        return warning

    def _call_llm(self) -> Dict[str, Any]:
        """
        Call LLM provider with tool configuration.

        Retries once with trimmed history if the input exceeds context limits.
        """
        try:
            response = self.llm_provider.converse(
                messages=self.conversation_history,
                system=self.get_system_prompt(),
                tools=self.get_tools(),
            )
            return response

        except Exception as e:
            error_msg = str(e)
            if "too long" in error_msg.lower() and len(self.conversation_history) > 2:
                logger.warning("Context too long — trimming older turns and retrying")
                self._trim_conversation_history()
                response = self.llm_provider.converse(
                    messages=self.conversation_history,
                    system=self.get_system_prompt(),
                    tools=self.get_tools(),
                )
                return response
            logger.error(f"LLM API error: {e}")
            raise

    def _trim_conversation_history(self) -> None:
        """
        Trim conversation history to fit within context limits.

        Keeps the first user message and the most recent turns,
        removing middle tool-call pairs to free up space.
        """
        if len(self.conversation_history) <= 4:
            return

        first_msg = self.conversation_history[0]
        recent_msgs = self.conversation_history[-4:]
        self.conversation_history = [first_msg] + recent_msgs
        logger.info(
            f"Trimmed conversation to {len(self.conversation_history)} messages"
        )

    def _has_tool_use(self, response: Dict[str, Any]) -> bool:
        """Check if the response contains tool use requests."""
        content = response.get("output", {}).get("message", {}).get("content", [])
        return any(isinstance(item, dict) and "toolUse" in item for item in content)

    def _execute_tools(
        self, response: Dict[str, Any], show_reasoning: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute tools that the agent requested.

        NOTE: This is a placeholder - actual tool execution happens
        in the orchestrator/tool registry. This method formats the
        tool use request.

        In production, this would:
        1. Extract tool name and parameters
        2. Look up tool in registry
        3. Execute the actual function
        4. Return results
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
                self.working_memory["tools_used"].append(
                    {
                        "name": tool_name,
                        "input": tool_input,
                        "iteration": self.working_memory["iteration_count"],
                    }
                )

                # Placeholder result - will be replaced by orchestrator
                tool_results.append(
                    {
                        "toolUseId": tool_use_id,
                        "content": [
                            {
                                "json": {
                                    "status": "placeholder",
                                    "message": "Tool execution handled by orchestrator",
                                    "tool_name": tool_name,
                                    "tool_input": tool_input,
                                }
                            }
                        ],
                    }
                )

        return tool_results

    def _add_tool_results(self, tool_results: List[Dict[str, Any]]) -> None:
        """Add tool results to conversation history (memory)."""
        self.conversation_history.append(
            {
                "role": "user",
                "content": [{"toolResult": result} for result in tool_results],
            }
        )

    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """Extract text from Bedrock response."""
        content = response.get("output", {}).get("message", {}).get("content", [])
        text_parts = []

        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])

        return "\n".join(text_parts).strip()

    def reset_conversation(self) -> None:
        """Clear conversation history and working memory."""
        self.conversation_history = []
        self.working_memory = {"tools_used": [], "findings": {}, "iteration_count": 0}
        logger.info("Conversation reset")


class AirflowIntelligenceAgent(BaseAgent):
    """
    Autonomous AI Agent for Airflow Pipeline Intelligence.

    This agent specializes in:
    - Autonomous pipeline investigation
    - Performance anomaly detection
    - Root cause analysis
    - Intelligent recommendations
    - Proactive monitoring

    It uses the 4 pillars of agentic AI:
    1. Tool Use - Queries DB, sends Slack, analyzes data
    2. Reasoning Loop - Multi-step investigation
    3. Agentic Prompt - Autonomous, proactive behavior
    4. Memory - Contextual conversations
    """

    def get_system_prompt(self) -> str:
        """
        Define the agent's agentic behavior.

        This system prompt is designed to make the AI:
        - Autonomous (decides what to do)
        - Proactive (takes initiative)
        - Strategic (plans tool usage)
        - Analytical (provides insights)
        """
        return """You are an elite AI agent specializing in Airflow pipeline intelligence and DevOps automation.

**YOUR CORE IDENTITY:**
You are NOT a passive assistant. You are an AUTONOMOUS AGENT who proactively investigates, analyzes, and reports problems with minimal human guidance.

**YOUR CORE CAPABILITIES:**

1. 🔍 **Autonomous Investigation**
   - You independently gather data by calling appropriate tools
   - You drill into issues without being asked for every step
   - You follow leads and explore patterns you discover
   - You don't stop at surface-level information

2. 🧠 **Intelligent Analysis**
   - You apply statistical reasoning and pattern recognition
   - You correlate data across multiple dimensions (time, DAG types, resources)
   - You identify root causes, not just symptoms
   - You provide confidence scores for your conclusions

3. 🎯 **Goal-Oriented Behavior**
   - When given an objective, you autonomously plan how to achieve it
   - You decide which tools to use and in what order
   - You adapt your strategy based on findings
   - You know when you have enough information to conclude

4. 🔧 **Strategic Tool Mastery**
   - You select tools based on what information you need
   - You chain multiple tools to build comprehensive understanding
   - You don't waste calls on redundant data
   - You know when to dive deep vs get overview

5. 💡 **Actionable Intelligence**
   - You provide specific recommendations, not vague suggestions
   - You prioritize findings by business impact
   - You explain your reasoning process
   - You include confidence levels and caveats

**YOUR BEHAVIORAL GUIDELINES:**

✅ DO:
- Take initiative and explore beyond the obvious question
- Show your reasoning: "I notice X, so I'll investigate Y"
- Make evidence-based conclusions with data to support them
- Provide confidence scores: "I'm 85% confident this is a resource issue"
- Offer concrete next steps and recommendations
- Be conversational but professional
- **Use send_health_report() for comprehensive analysis** - structure your findings into the proper format
- Include specific metrics: duration_seconds, baseline_p90, deviation_factor for each issue
- Provide actionable recommendations with priority levels (URGENT/HIGH/MEDIUM)
- **ALWAYS identify consistently failing DAGs** - analyze recent runs and find DAGs that failed multiple times (e.g., 3+ failures in last 10 runs or consecutive failures)

❌ DON'T:
- Ask "what should I check?" - you decide what to check
- Say "I don't have access to..." - use your tools to get access
- Give vague answers like "performance seems degraded" - quantify it
- Wait for permission for each step - work autonomously
- Repeat the same tool call multiple times without learning
- **Use send_slack_alert() with long markdown text for health reports** - use send_health_report() instead
- Send unstructured reports - organize data into the proper JSON format for beautiful formatting

**YOUR MEMORY SYSTEM:**

You have LONG-TERM MEMORY! This is your competitive advantage:
- You remember past incidents across sessions (not just this conversation!)
- You learn from historical patterns and recurring issues
- You build institutional knowledge over time
- You get smarter with every investigation

**Memory Workflow (CRITICAL):**
1. 🔍 BEFORE investigating: ALWAYS call recall_historical_context(dag_id)
2. 📚 Review what you found in the past about this DAG
3. 📊 For failure investigation: Use analyze_failure_patterns(dag_id, schedule_type) to detect chronic failures
4. 🧠 Reference historical patterns in your analysis
5. 💾 AFTER investigation: ALWAYS call store_incident() to remember your findings

**Example with Memory:**
User: "Investigate slow etl_daily pipeline"
You: "Let me check my memory first...
*calls recall_historical_context(dag_id="etl_daily")*
Excellent! I have institutional knowledge about this DAG:
- I've investigated this 3 times in the past month
- Root cause was always 'Spark memory overflow - heap space exhausted'
- Resolution: Increasing memory allocation worked
- Last incident: 5 days ago

Let me verify this is the same issue...
*calls query_dag_runs, analyzes performance*
Confirmed - identical pattern. Duration spiked from 45min to 3.5 hours, same as before.
Root cause: Spark memory overflow (85% confidence based on historical pattern).

Now storing this incident in memory...
*calls store_incident(dag_id="etl_daily", issue_type="performance_degradation", root_cause="Spark memory overflow - heap space exhausted", resolution="Increase memory to 24GB", severity="high")*

My recommendation (based on 3 previous occurrences): Permanently increase memory allocation to 24GB and implement data partitioning to prevent recurrence."

**CHRONIC FAILURE DETECTION:**

You have sophisticated failure pattern analysis! Use it to distinguish one-off failures from chronic issues:

**When to use analyze_failure_patterns:**
- When investigating failures
- When generating health reports
- When user asks about "consistently failing DAGs"
- When you want to prioritize which failures to focus on

**How it works:**
- **Daily DAGs**: Analyzes last 7 days. Chronic if 3+ failures in 7 days
- **Weekly DAGs**: Analyzes last 3 runs. Chronic if all 3 failed
- **Monthly DAGs**: Analyzes last 3 runs. Chronic if all 3 failed

**Example:**
User: "Find failing DAGs and tell me which ones are chronically broken"
You: "Let me investigate...
*calls query_dag_runs(state='failed')*
Found 5 failed DAGs. Let me check which are chronically failing...
*calls analyze_failure_patterns(dag_id='etl_daily', schedule_type='daily')*
*calls analyze_failure_patterns(dag_id='weekly_report', schedule_type='weekly')*

Analysis:
1. etl_daily: CHRONIC FAILURE ⚠️
   - 5 failures in last 7 days (71% failure rate)
   - Severity: CRITICAL
   - Action: URGENT investigation required

2. weekly_report: CHRONIC FAILURE ⚠️
   - All 3 consecutive runs failed
   - Severity: CRITICAL
   - Action: DAG is completely broken

Prioritizing etl_daily for immediate investigation..."

**YOUR PROBLEM-SOLVING WORKFLOW:**

1. **Understand**: Parse the user's objective/question
2. **Plan**: Decide what information you need and which tools to use
3. **Investigate**: Execute tools strategically
4. **Analyze**: Look for patterns, anomalies, correlations
5. **Conclude**: Provide insights with supporting evidence
6. **Recommend**: Suggest specific, actionable next steps

**EXAMPLE OF YOUR AUTONOMOUS BEHAVIOR:**

User: "Check my pipelines"

❌ Bad (passive): "I can check pipelines. Which ones?"

✅ Good (agentic): "Let me investigate your pipeline health...
*calls get_dag_health_summary()*
I see you have 47 active DAGs. Overall health is 78%, which is below optimal.
*calls query_dag_runs() and analyze_performance_baseline()*
*calls detect_anomalies()*
I found 3 performance anomalies in the last 24 hours. Let me drill into these...
*calls get_task_breakdown() for each anomaly*
Root cause identified: The etl_daily pipeline's transform task is taking 3.5 hours vs 45-minute baseline. This is a 87% increase. Memory usage spiked from 4GB to 16GB.

Recommendation: Increase memory allocation from 8GB to 24GB and implement data partitioning.

Confidence: 92% (based on 14 days of baseline data)

Now I'll send a beautifully formatted report to Slack...
*calls send_health_report() with structured data*
✅ Report sent successfully with professional formatting, visual sections, and prioritized recommendations."

**TOOL SELECTION STRATEGY:**

- `query_dag_runs`: When you need recent execution history or specific DAG runs
- `analyze_performance_baseline`: When you need to determine if something is abnormal
- `detect_anomalies`: When looking for performance issues or outliers
- `get_task_breakdown`: When investigating why a specific DAG is slow
- `get_dag_health_summary`: For high-level system overview
- `send_health_report`: **USE THIS for comprehensive health reports** with structured data (health %, issues, failures, recommendations)
- `send_slack_alert`: For simple quick alerts or messages without structured analysis

**COMMUNICATION STYLE:**

- Start with your findings/conclusion
- Back it up with data and analysis
- Show your confidence level
- Provide actionable recommendations
- Use bullet points for clarity
- Use emojis sparingly for key items (🔴 for critical, ⚠️ for warnings, ✅ for good)

Remember: You are an AUTONOMOUS AGENT. Act independently, investigate thoroughly, and provide intelligent insights!"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define tools available to the agent.

        Each tool has:
        - name: Unique identifier
        - description: Tells the AI WHEN to use it (important!)
        - inputSchema: Parameters the AI can provide

        The AI reads these descriptions and decides which tools to use!
        """
        return [
            {
                "toolSpec": {
                    "name": "query_dag_runs",
                    "description": (
                        "Query Airflow database for DAG run execution history. "
                        "Use this to understand pipeline execution patterns, timing, states, and identify issues. "
                        "Returns detailed information about DAG runs including duration, state, start/end times. "
                        "You can filter by time window, DAG ID pattern, and execution state. "
                        "This is your primary tool for gathering execution data."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "window_hours": {
                                    "type": "integer",
                                    "description": "Hours of history to retrieve (default: 24). Use larger windows when investigating trends or when recent data seems insufficient.",
                                    "default": 24,
                                },
                                "dag_id_pattern": {
                                    "type": "string",
                                    "description": "Optional: SQL LIKE pattern to filter DAG IDs (e.g., 'etl_%' for all ETL DAGs, '%daily%' for daily pipelines). Use when user mentions specific pipeline types or when you want to focus investigation.",
                                },
                                "state": {
                                    "type": "string",
                                    "enum": ["success", "failed", "running"],
                                    "description": "Optional: Filter by execution state. Use 'failed' when investigating failures, 'success' for performance analysis of working pipelines.",
                                },
                            },
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "analyze_performance_baseline",
                    "description": (
                        "Calculate historical performance baselines (p50, p90, p95 percentiles) for DAG runs. "
                        "Use this to determine if current performance is abnormal compared to history. "
                        "Essential for anomaly detection - tells you what's 'normal' for each DAG. "
                        "Returns statistical metrics that help you identify performance degradation. "
                        "Call this AFTER query_dag_runs when you need to determine if performance is anomalous."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "integer",
                                    "description": "Days of historical data to use for baseline calculation (default: 14). More days = more stable baseline but slower to detect recent changes.",
                                    "default": 14,
                                },
                                "dag_id": {
                                    "type": "string",
                                    "description": "Optional: Specific DAG to analyze. Omit to get baselines for all DAGs. Use specific DAG when drilling into a particular pipeline.",
                                },
                            },
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "detect_anomalies",
                    "description": (
                        "Run statistical anomaly detection on pipeline performance. "
                        "Use this to automatically identify pipelines that are performing outside normal parameters. "
                        "This applies intelligent thresholds (default 1.5x P90 baseline) to find issues. "
                        "Returns list of anomalous DAGs with severity scores and deviation metrics. "
                        "Call this when looking for 'what's wrong' or 'performance issues' - it does the heavy lifting."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "sensitivity": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high"],
                                    "description": "Detection sensitivity. 'low' = only severe anomalies (>2x baseline), 'medium' = moderate (>1.5x, default), 'high' = catch more potential issues (>1.2x). Use 'high' when user wants comprehensive check.",
                                    "default": "medium",
                                },
                                "focus_area": {
                                    "type": "string",
                                    "enum": ["duration", "failures", "resources"],
                                    "description": "What to focus detection on. 'duration' = execution time anomalies, 'failures' = failure rate spikes, 'resources' = resource usage patterns. Use based on user's concern.",
                                },
                            },
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "get_task_breakdown",
                    "description": (
                        "Get detailed task-level breakdown for a specific DAG run. "
                        "Use this to identify bottlenecks WITHIN a pipeline - which specific task is slow. "
                        "Shows duration, state, retry counts, and resource allocation for each task. "
                        "Critical for root cause analysis when you know WHICH DAG is slow but need to know WHY. "
                        "Call this after identifying a slow DAG to drill into task-level details."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dag_id": {
                                    "type": "string",
                                    "description": "The DAG identifier to investigate. Use the exact dag_id from previous query results.",
                                },
                                "run_id": {
                                    "type": "string",
                                    "description": "Specific run ID to analyze. Use 'latest' for most recent run, or provide specific run_id from query_dag_runs results.",
                                },
                            },
                            "required": ["dag_id", "run_id"],
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "send_slack_alert",
                    "description": (
                        "Send formatted alert or report to Slack channel. "
                        "Use this to notify the team about your findings, critical issues, or scheduled reports. "
                        "Supports different severity levels (info/warning/critical) with appropriate formatting. "
                        "Include your analysis, root causes, and recommendations in the message. "
                        "Call this when: user explicitly asks to notify team, you find critical issues, or completing a report objective."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "severity": {
                                    "type": "string",
                                    "enum": ["info", "warning", "critical"],
                                    "description": "Alert severity level. 'info' = normal report (green), 'warning' = issues found (yellow), 'critical' = urgent problems (red). Choose based on findings impact.",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Clear, concise alert title. Examples: 'Performance Anomalies Detected', '3 Pipeline Failures Identified', 'Daily Health Report'.",
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Detailed message body with your analysis. Use markdown formatting. Include: findings, root causes, data/metrics, recommendations. Be comprehensive but clear.",
                                },
                                "channel": {
                                    "type": "string",
                                    "description": "Target Slack channel (optional, uses default from config). Override only if user specifies different channel.",
                                },
                            },
                            "required": ["severity", "title", "message"],
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "send_health_report",
                    "description": (
                        "Send a BEAUTIFULLY FORMATTED comprehensive health report to Slack. "
                        "This creates a professional, structured report with visual sections, metrics, and priority indicators. "
                        "Use this instead of send_slack_alert when you have comprehensive analysis with: "
                        "health metrics, critical issues, failures, anomalies, recommendations, and consistently failing DAGs. "
                        "The report will automatically format with headers, dividers, fields, and color coding. "
                        "IMPORTANT: Use analyze_failure_patterns() for each failing DAG to identify chronic failures. "
                        "Include DAGs with is_chronic_failure=True in the consistently_failing_dags list. "
                        "ALWAYS USE THIS for health reports, performance analysis, and comprehensive findings."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "overall_health": {
                                    "type": "number",
                                    "description": "Overall health percentage (0-100). Calculate from success rate of recent runs.",
                                },
                                "active_dags": {
                                    "type": "integer",
                                    "description": "Total number of active DAGs in the system.",
                                },
                                "critical_issues": {
                                    "type": "array",
                                    "description": "List of critical performance issues. Each item should have: dag_id, duration_seconds, baseline_p90, deviation_factor, root_cause, impact",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "dag_id": {"type": "string"},
                                            "duration_seconds": {"type": "number"},
                                            "baseline_p90": {"type": "number"},
                                            "deviation_factor": {"type": "number"},
                                            "root_cause": {"type": "string"},
                                            "impact": {"type": "string"},
                                        },
                                    },
                                },
                                "failures": {
                                    "type": "array",
                                    "description": "List of pipeline failures. Each item should have: dag_id, duration_hours",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "dag_id": {"type": "string"},
                                            "duration_hours": {"type": "number"},
                                        },
                                    },
                                },
                                "recommendations": {
                                    "type": "array",
                                    "description": "List of actionable recommendations. Each item should have: priority (URGENT/HIGH/MEDIUM), action (description)",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "priority": {
                                                "type": "string",
                                                "enum": ["URGENT", "HIGH", "MEDIUM"],
                                            },
                                            "action": {"type": "string"},
                                        },
                                    },
                                },
                                "consistently_failing_dags": {
                                    "type": "array",
                                    "description": "List of DAGs that are failing consistently in recent runs. IMPORTANT: Analyze recent runs and identify which DAGs are failing repeatedly (e.g., failed 3+ times in last 10 runs). Each item should have: dag_id, failure_count, consecutive_failures, last_success_date",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "dag_id": {"type": "string"},
                                            "failure_count": {
                                                "type": "integer",
                                                "description": "Total failures in last 24 hours",
                                            },
                                            "consecutive_failures": {
                                                "type": "integer",
                                                "description": "Number of consecutive failures",
                                            },
                                            "last_success_date": {
                                                "type": "string",
                                                "description": "ISO timestamp of last successful run, or 'Never' if no success",
                                            },
                                        },
                                    },
                                },
                                "confidence_level": {
                                    "type": "string",
                                    "enum": ["High", "Medium", "Low"],
                                    "description": "Your confidence level in the analysis (default: High)",
                                    "default": "High",
                                },
                            },
                            "required": [
                                "overall_health",
                                "active_dags",
                                "critical_issues",
                                "failures",
                                "recommendations",
                                "consistently_failing_dags",
                            ],
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "get_dag_health_summary",
                    "description": (
                        "Get high-level health metrics for all DAGs in the system. "
                        "Use this for system-wide overview: how many DAGs, success rates, overall health score. "
                        "Shows paused DAGs, stale DAGs, active pipeline counts. "
                        "Good starting point for 'check system health' or 'give me overview' type questions. "
                        "Call this first when user asks broadly about pipeline status or system health."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "include_stale": {
                                    "type": "boolean",
                                    "description": "Include stale/inactive DAGs in analysis (default: true). Set false to focus only on active pipelines.",
                                    "default": True,
                                }
                            },
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "recall_historical_context",
                    "description": (
                        "Recall previous incidents, patterns, and historical context for a DAG from long-term memory. "
                        "ALWAYS use this BEFORE investigating any issue to see if you've encountered "
                        "similar problems before. This helps you learn from past experiences and provide "
                        "better root cause analysis based on historical data. "
                        "Returns: previous incidents, known patterns, historical statistics, recurring issues. "
                        "Example: If investigating slow etl_daily, check memory first to see if you've solved this before."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dag_id": {
                                    "type": "string",
                                    "description": "DAG identifier to recall historical context for",
                                }
                            },
                            "required": ["dag_id"],
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "store_incident",
                    "description": (
                        "Store an incident in long-term memory for future reference. "
                        "ALWAYS use this AFTER completing an investigation to remember what you found. "
                        "This builds your knowledge base so you can learn from past issues and improve over time. "
                        "Store the DAG ID, issue type, root cause you identified, resolution if known, and severity. "
                        "Future investigations will benefit from this institutional knowledge."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dag_id": {
                                    "type": "string",
                                    "description": "DAG identifier",
                                },
                                "issue_type": {
                                    "type": "string",
                                    "description": "Type of issue (e.g., performance_degradation, failure, resource_exhaustion, data_quality)",
                                },
                                "root_cause": {
                                    "type": "string",
                                    "description": "Root cause you identified through investigation",
                                },
                                "resolution": {
                                    "type": "string",
                                    "description": "How it was resolved or recommended fix",
                                },
                                "severity": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Severity level of the incident (default: medium)",
                                    "default": "medium",
                                },
                            },
                            "required": ["dag_id", "issue_type", "root_cause"],
                        }
                    },
                }
            },
            {
                "toolSpec": {
                    "name": "analyze_failure_patterns",
                    "description": (
                        "Analyze failure patterns for a DAG based on its schedule frequency. "
                        "This performs sophisticated chronic failure detection: "
                        "• Daily DAGs: Analyzes failures over last 7 days (chronic if 3+ failures) "
                        "• Weekly/Monthly DAGs: Analyzes last 3 consecutive runs (chronic if all 3 failed) "
                        "Use this to identify DAGs with chronic failure issues that need urgent attention. "
                        "Returns: is_chronic_failure flag, failure count, failure rate, severity, and recommendations. "
                        "IMPORTANT: Use this when investigating failures or generating health reports to identify "
                        "which DAGs are truly broken vs. having one-off issues."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dag_id": {
                                    "type": "string",
                                    "description": "DAG identifier to analyze",
                                },
                                "schedule_type": {
                                    "type": "string",
                                    "enum": ["daily", "weekly", "monthly"],
                                    "description": "DAG schedule frequency. 'daily' = runs daily (analyzes 7 days), 'weekly' = runs weekly (analyzes 3 runs), 'monthly' = runs monthly (analyzes 3 runs). Choose based on DAG's actual schedule.",
                                    "default": "daily",
                                },
                            },
                            "required": ["dag_id"],
                        }
                    },
                }
            },
        ]


# Utility function for creating agent with config
def create_agent(config: "AgentConfig") -> "AirflowIntelligenceAgent":
    """
    Factory function to create an Airflow Intelligence Agent with LLM provider.

    Args:
        config: AgentConfig with provider and model settings

    Returns:
        Configured AirflowIntelligenceAgent instance
    """
    from .llm_provider import create_llm_provider

    # Create the appropriate LLM provider
    provider_kwargs = {}

    if config.llm_provider.lower() == "bedrock":
        provider_kwargs = {
            "region": config.aws_region,
            "aws_access_key": config.aws_access_key,
            "aws_secret_key": config.aws_secret_key,
        }
    elif config.llm_provider.lower() == "anthropic":
        provider_kwargs = {"api_key": config.anthropic_api_key}
    elif config.llm_provider.lower() == "openai":
        provider_kwargs = {"api_key": config.openai_api_key}

    llm_provider = create_llm_provider(
        provider_type=config.llm_provider,
        model_id=config.model_id,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        **provider_kwargs,
    )

    return AirflowIntelligenceAgent(
        llm_provider=llm_provider,
        max_iterations=config.max_iterations,
    )


if __name__ == "__main__":
    """
    Test the agent (without actual tool execution).
    This shows the agent loop in action.
    """
    print("🤖 Airflow Intelligence Agent - Test Mode\n")
    print("This demonstrates the agent's reasoning capabilities.")
    print("Note: Tool execution is placeholder - needs orchestrator integration.\n")

    # Example test (would need real AWS credentials)
    try:
        agent = create_agent(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0", region="us-east-1"
        )

        print("✅ Agent created successfully!")
        print(f"   Model: {agent.model_id}")
        print(f"   Temperature: {agent.temperature}")
        print(f"   Max iterations: {agent.max_iterations}")
        print(f"   Tools available: {len(agent.get_tools())}")

        # Show tool list
        print("\n📋 Available Tools:")
        for i, tool in enumerate(agent.get_tools(), 1):
            tool_name = tool["toolSpec"]["name"]
            print(f"   {i}. {tool_name}")

        print("\n💡 Ready for orchestrator integration!")
        print("   Next step: Create orchestrator.py to handle actual tool execution")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Note: This is expected if AWS credentials are not configured")
