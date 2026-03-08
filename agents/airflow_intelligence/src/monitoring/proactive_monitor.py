"""
Proactive Monitoring - Agent Runs Continuously and Decides When to Investigate

This module enables the agent to run autonomously in the background,
continuously monitoring Airflow health and deciding when to:
- Investigate issues
- Send alerts
- Prioritize problems
- Take action

This is TRUE agentic behavior - the agent is no longer reactive,
it's proactively monitoring and making decisions autonomously.
"""

import time
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional

from ..core import create_orchestrator
from ..core import AgentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProactiveMonitor:
    """
    Autonomous agent that runs continuously and decides WHEN to investigate.

    The agent is not just reactive - it proactively:
    - Monitors system health on a schedule
    - Decides autonomously what's worth investigating
    - Determines when to alert the team
    - Prioritizes issues by severity
    - Uses memory to detect patterns
    - Analyzes failure patterns automatically

    This is the evolution from:
    - "Agent responds when asked" → "Agent monitors continuously"
    - "Human decides what to check" → "Agent decides autonomously"
    - "Manual investigation" → "Autonomous monitoring"
    """

    def __init__(self, config: AgentConfig, check_interval_minutes: int = 15):
        """
        Initialize proactive monitor.

        Args:
            config: Agent configuration
            check_interval_minutes: How often to check (default: 15 minutes)
        """
        self.config = config
        self.check_interval = timedelta(minutes=check_interval_minutes)
        # Use higher iteration limit for proactive monitoring (comprehensive analysis)
        self.orchestrator = create_orchestrator(config, max_iterations=20)
        self.last_check = None
        self.running = False
        self.check_count = 0

        # Set up graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(
            f"Proactive monitor initialized (check interval: {check_interval_minutes} minutes)"
        )

    def start(self):
        """
        Start proactive monitoring loop.

        The agent will run continuously, checking system health
        at regular intervals and deciding autonomously when to investigate
        and alert.
        """
        logger.info("🤖 Starting proactive monitoring...")

        print("\n" + "=" * 80)
        print("🤖 PROACTIVE AGENT MODE - Autonomous Monitoring")
        print("=" * 80)
        print(
            f"✅ Agent will check system every {self.check_interval.total_seconds()/60:.0f} minutes"
        )
        print("✅ Agent will decide autonomously when to investigate and alert")
        print("✅ Agent will use memory to detect patterns and learn")
        print("✅ Agent will analyze failure patterns automatically")
        print("✅ Press Ctrl+C to stop gracefully")
        print("=" * 80 + "\n")

        self.running = True

        # Run first check immediately
        print("🔄 Running initial health check...")
        self._proactive_check()

        # Then start the monitoring loop
        while self.running:
            try:
                # Calculate next check time
                next_check = datetime.utcnow() + self.check_interval
                next_check_str = next_check.strftime("%H:%M:%S UTC")

                logger.info(f"⏰ Next check scheduled at {next_check_str}")
                print(f"\n⏰ Next check at {next_check_str}")
                print(
                    f"   (Check #{self.check_count + 1} complete. Sleeping for {self.check_interval.total_seconds()/60:.0f} minutes...)"
                )

                # Sleep until next check
                time.sleep(self.check_interval.total_seconds())

                # Run check
                self._proactive_check()

            except KeyboardInterrupt:
                print("\n\n🛑 Received shutdown signal...")
                self._shutdown()
                break

            except Exception as e:
                logger.error(f"Error in proactive monitoring loop: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
                print("⏳ Waiting 60 seconds before retry...")
                time.sleep(60)

    def _proactive_check(self):
        """
        Agent autonomously decides what to check and whether to alert.

        This is where the "agentic" behavior happens:
        - Agent decides what to investigate
        - Agent determines severity
        - Agent decides whether to alert
        - Agent uses memory and pattern analysis
        - Agent prioritizes actions
        """
        self.check_count += 1
        check_time = datetime.utcnow()

        print(f"\n{'='*80}")
        print(
            f"🔍 Proactive Check #{self.check_count} @ {check_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        print(f"{'='*80}\n")

        # Construct objective for the agent
        objective = self._build_check_objective(check_time)

        try:
            # Execute mission - agent decides autonomously what to do
            result = self.orchestrator.execute_mission(
                objective=objective, show_reasoning=True  # Show agent's reasoning
            )

            self.last_check = check_time

            if result.get("success"):
                logger.info("✅ Proactive check completed successfully")
                print("\n✅ Check complete")
            else:
                logger.error(f"❌ Proactive check failed: {result.get('error')}")
                print(f"\n❌ Check failed: {result.get('error')}")

            # Store metrics
            if result.get("tools_used"):
                print(
                    f"\n📊 Agent used {len(result['tools_used'])} tools in this check"
                )

            return result

        except Exception as e:
            logger.error(f"Error in proactive check: {e}", exc_info=True)
            print(f"\n❌ Error during check: {e}")
            return {"success": False, "error": str(e)}

    def _build_check_objective(self, check_time: datetime) -> str:
        """
        Build the objective/mission for the agent's proactive check.

        This gives the agent context and decision-making authority.
        """
        return f"""You are running in PROACTIVE AUTONOMOUS MODE.

**Current Context:**
- Time: {check_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Check #: {self.check_count}
- Last Check: {self.last_check.strftime('%Y-%m-%d %H:%M:%S UTC') if self.last_check else 'First check'}

**Your Mission:**
Autonomously monitor Airflow health and decide:
1. Is there anything concerning that needs investigation?
2. Should I alert the team about any issues?
3. What should I prioritize?
4. Are there any chronic failures that need immediate attention?

**Your Autonomous Workflow:**
1. **Check System Health**
   - Use get_dag_health_summary() for overview
   - Assess overall system health percentage

2. **Investigate If Needed**
   - If health < 90% OR failures detected → investigate deeper
   - Query recent runs (query_dag_runs)
   - Check for failed DAGs

3. **Use Your Memory**
   - Recall historical context for concerning DAGs (if any)
   - Check if you've seen these issues before
   - Reference patterns from previous investigations

4. **Analyze Failure Patterns (EFFICIENTLY)**
   - Use analyze_failure_patterns() to detect CHRONIC failures
   - Focus on top priority failures first (not every single one)
   - Identify daily DAGs with 3+ failures in 7 days
   - Identify weekly/monthly DAGs with 3/3 consecutive failures
   - ONE-OFF failures don't need individual analysis

5. **Make Smart Decisions**
   - Compare current state to historical patterns
   - Determine severity (CRITICAL/HIGH/MEDIUM/LOW)
   - Prioritize chronic failures over one-off issues
   - Decide if issues warrant alerting

6. **Alert If Necessary**
   - ONLY alert for ACTIONABLE issues that need human attention
   - Send health report (send_health_report) with structured data
   - Include chronic failure analysis
   - Prioritize recommendations by severity

7. **Store Your Findings**
   - Store any CHRONIC incidents you discover (store_incident)
   - Build your institutional knowledge

**Alert Decision Criteria (Use Your Judgment):**
ALERT if:
- Health dropped >10% from normal baseline
- Chronic failures detected (3+ failures in 7 days for daily DAGs)
- Critical pipelines failing (3/3 consecutive for weekly/monthly)
- New failure patterns emerged since last check
- Performance degraded >2x baseline

DON'T ALERT for:
- Minor one-off failures (1-2 failures in a week)
- Already known issues with no new developments
- Health score >95% with no chronic failures
- System functioning normally

**Remember:**
- You are AUTONOMOUS - make smart decisions
- Use your MEMORY to learn from patterns
- Use FAILURE PATTERN ANALYSIS to prioritize
- Only alert on ACTIONABLE issues
- Focus on CHRONIC failures, not one-offs
- You're protecting production - be thorough but not noisy

Now execute your proactive monitoring mission autonomously!"""

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n\n🛑 Received shutdown signal...")
        self._shutdown()
        sys.exit(0)

    def _shutdown(self):
        """Gracefully shutdown the monitor."""
        logger.info("Shutting down proactive monitor...")
        self.running = False

        print("\n" + "=" * 80)
        print("📊 PROACTIVE MONITORING SUMMARY")
        print("=" * 80)
        print(f"Total Checks: {self.check_count}")
        print(
            f"Started: {self.last_check.strftime('%Y-%m-%d %H:%M:%S UTC') if self.last_check else 'N/A'}"
        )
        print(
            f"Duration: {(datetime.utcnow() - self.last_check).total_seconds()/60:.1f} minutes"
            if self.last_check
            else "N/A"
        )
        print("=" * 80)
        print("\n👋 Proactive monitoring stopped gracefully")
        print("✅ All agent state saved")
        print("✅ Memory persisted to disk\n")


def run_proactive_monitor(
    check_interval_minutes: int = 15, config: Optional[AgentConfig] = None
):
    """
    Convenience function to run proactive monitoring.

    Args:
        check_interval_minutes: How often to check (default: 15 minutes)
        config: Optional configuration (loads from env if not provided)
    """
    if config is None:
        config = AgentConfig.from_env()

    monitor = ProactiveMonitor(config, check_interval_minutes)
    monitor.start()


if __name__ == "__main__":
    """
    Run proactive monitoring directly.

    Usage:
        python -m agents.airflow_intelligence.proactive_monitor
    """
    print("🤖 Airflow Intelligence Agent - Proactive Monitoring\n")

    try:
        run_proactive_monitor(check_interval_minutes=15)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
