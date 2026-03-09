"""
Long-Term Memory System for Airflow Intelligence Agent

This gives the agent the ability to remember past investigations,
incidents, and patterns - making it truly agentic with context
across sessions.

Quick Implementation: Just add this to your agent TODAY!
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    Persistent memory storage for the agent.

    Stores:
    - Historical incidents (what went wrong)
    - Root causes found
    - Patterns discovered
    - Recommendations made
    - Investigation context

    Usage:
        memory = AgentMemory()

        # Store an incident
        memory.store_incident(
            dag_id="etl_daily",
            issue_type="performance_degradation",
            root_cause="Spark memory overflow",
            resolution="Increased memory to 24GB"
        )

        # Recall similar incidents
        past = memory.recall_similar_incidents("etl_daily")
        # Agent now knows: "I've seen this 3 times before!"
    """

    def __init__(self, memory_dir: str = ".agent_memory"):
        """
        Initialize memory system.

        Args:
            memory_dir: Directory to store memory files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # Memory files
        self.incidents_file = self.memory_dir / "incidents.jsonl"
        self.patterns_file = self.memory_dir / "patterns.jsonl"
        self.context_file = self.memory_dir / "context.json"

        logger.info(f"Agent memory initialized at {self.memory_dir}")

    def store_incident(
        self,
        dag_id: str,
        issue_type: str,
        root_cause: str,
        resolution: Optional[str] = None,
        severity: str = "medium",
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Store an incident for future reference.

        Args:
            dag_id: DAG identifier
            issue_type: Type of issue (performance, failure, etc.)
            root_cause: Root cause description
            resolution: How it was resolved (if known)
            severity: low/medium/high/critical
            metadata: Additional context

        Returns:
            Incident ID
        """
        incident_id = f"{dag_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        incident = {
            "id": incident_id,
            "timestamp": datetime.utcnow().isoformat(),
            "dag_id": dag_id,
            "issue_type": issue_type,
            "root_cause": root_cause,
            "resolution": resolution,
            "severity": severity,
            "metadata": metadata or {},
        }

        with open(self.incidents_file, "a") as f:
            f.write(json.dumps(incident) + "\n")

        logger.info(f"Stored incident: {incident_id}")
        return incident_id

    def recall_similar_incidents(
        self, dag_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall similar past incidents for a DAG.

        Args:
            dag_id: DAG to recall incidents for
            limit: Maximum number of incidents to return

        Returns:
            List of past incidents, most recent first
        """
        if not self.incidents_file.exists():
            return []

        incidents = []
        try:
            with open(self.incidents_file, "r") as f:
                for line in f:
                    if line.strip():
                        incident = json.loads(line)
                        if incident["dag_id"] == dag_id:
                            incidents.append(incident)

            # Sort by timestamp, most recent first
            incidents.sort(key=lambda x: x["timestamp"], reverse=True)

            return incidents[:limit]

        except Exception as e:
            logger.error(f"Error recalling incidents: {e}")
            return []

    def get_dag_context(self, dag_id: str) -> Dict[str, Any]:
        """
        Get all relevant context for a DAG.

        Returns:
            Dictionary with:
            - previous_incidents: List of past incidents
            - incident_count: Total incidents
            - most_common_root_cause: Most frequent root cause
            - last_incident_date: When last incident occurred
            - severity_distribution: Count by severity
        """
        incidents = self.recall_similar_incidents(dag_id, limit=100)

        if not incidents:
            return {
                "dag_id": dag_id,
                "has_history": False,
                "message": "No previous incidents found",
            }

        # Calculate statistics
        root_causes = [i["root_cause"] for i in incidents]
        most_common_root_cause = max(set(root_causes), key=root_causes.count)

        severities = [i.get("severity", "medium") for i in incidents]
        severity_counts = {s: severities.count(s) for s in set(severities)}

        return {
            "dag_id": dag_id,
            "has_history": True,
            "incident_count": len(incidents),
            "most_common_root_cause": most_common_root_cause,
            "last_incident_date": incidents[0]["timestamp"],
            "severity_distribution": severity_counts,
            "recent_incidents": incidents[:3],  # Last 3
            "patterns": self._detect_patterns(incidents),
        }

    def _detect_patterns(self, incidents: List[Dict]) -> List[str]:
        """Detect patterns in incidents."""
        if len(incidents) < 2:
            return []

        patterns = []

        # Check for recurring issues
        root_causes = [i["root_cause"] for i in incidents]
        if len(set(root_causes)) == 1:
            patterns.append(
                f"Recurring issue: '{root_causes[0]}' happened {len(root_causes)} times"
            )

        # Check for increasing frequency
        if len(incidents) >= 3:
            recent = incidents[:3]
            if self._is_increasing_frequency(recent):
                patterns.append("Incidents are becoming more frequent")

        return patterns

    def _is_increasing_frequency(self, recent_incidents: List[Dict]) -> bool:
        """Check if incidents are increasing in frequency."""
        try:
            timestamps = [
                datetime.fromisoformat(i["timestamp"]) for i in recent_incidents
            ]
            timestamps.sort()

            # Check if time between incidents is decreasing
            interval1 = (timestamps[1] - timestamps[0]).total_seconds()
            interval2 = (timestamps[2] - timestamps[1]).total_seconds()

            return interval2 < interval1 * 0.7  # 30% faster
        except Exception:
            return False

    def store_pattern(
        self,
        pattern_type: str,
        description: str,
        affected_dags: List[str],
        confidence: float,
    ) -> str:
        """
        Store a discovered pattern.

        Args:
            pattern_type: Type of pattern (e.g., "performance_degradation")
            description: Pattern description
            affected_dags: List of affected DAG IDs
            confidence: Confidence score (0.0-1.0)

        Returns:
            Pattern ID
        """
        pattern_id = f"pattern_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        pattern = {
            "id": pattern_id,
            "timestamp": datetime.utcnow().isoformat(),
            "pattern_type": pattern_type,
            "description": description,
            "affected_dags": affected_dags,
            "confidence": confidence,
        }

        with open(self.patterns_file, "a") as f:
            f.write(json.dumps(pattern) + "\n")

        logger.info(f"Stored pattern: {pattern_id}")
        return pattern_id

    def get_known_patterns(self, dag_id: Optional[str] = None) -> List[Dict]:
        """
        Get known patterns.

        Args:
            dag_id: Optional DAG ID to filter patterns

        Returns:
            List of patterns
        """
        if not self.patterns_file.exists():
            return []

        patterns = []
        try:
            with open(self.patterns_file, "r") as f:
                for line in f:
                    if line.strip():
                        pattern = json.loads(line)
                        if dag_id is None or dag_id in pattern["affected_dags"]:
                            patterns.append(pattern)

            # Sort by timestamp, most recent first
            patterns.sort(key=lambda x: x["timestamp"], reverse=True)

            return patterns

        except Exception as e:
            logger.error(f"Error getting patterns: {e}")
            return []

    def save_context(self, key: str, value: Any):
        """Save arbitrary context data."""
        try:
            # Load existing context
            context = {}
            if self.context_file.exists():
                with open(self.context_file, "r") as f:
                    context = json.load(f)

            # Update context
            context[key] = {"value": value, "timestamp": datetime.utcnow().isoformat()}

            # Save context
            with open(self.context_file, "w") as f:
                json.dump(context, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving context: {e}")

    def get_context(self, key: str) -> Optional[Any]:
        """Get saved context data."""
        try:
            if not self.context_file.exists():
                return None

            with open(self.context_file, "r") as f:
                context = json.load(f)

            return context.get(key, {}).get("value")

        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return None

    def analyze_failure_patterns(
        self, dag_id: str, schedule_type: str = "daily"
    ) -> Dict[str, Any]:
        """
        Analyze failure patterns based on DAG schedule.

        For daily DAGs: Analyzes failures over 7 days
        For weekly/monthly DAGs: Analyzes last 3 consecutive runs

        Args:
            dag_id: DAG identifier to analyze
            schedule_type: 'daily', 'weekly', or 'monthly'

        Returns:
            Dictionary with failure pattern analysis including:
            - is_chronic_failure: Boolean indicating if DAG is chronically failing
            - failure_count: Number of failures in the analysis window
            - analysis_window: Description of the time window analyzed
            - consecutive_failures: Number of consecutive failures
            - failure_rate: Percentage of failures
            - severity: low/medium/high/critical
            - recommendation: Action recommendation
            - incidents: List of relevant incidents
        """
        if not self.incidents_file.exists():
            return {
                "dag_id": dag_id,
                "is_chronic_failure": False,
                "failure_count": 0,
                "message": "No historical data available",
            }

        try:
            # Load all incidents for this DAG
            incidents = []
            with open(self.incidents_file, "r") as f:
                for line in f:
                    if line.strip():
                        incident = json.loads(line)
                        if incident["dag_id"] == dag_id:
                            incidents.append(incident)

            if not incidents:
                return {
                    "dag_id": dag_id,
                    "schedule_type": schedule_type,
                    "is_chronic_failure": False,
                    "failure_count": 0,
                    "message": "No incidents found for this DAG",
                }

            # Sort by timestamp, most recent first
            incidents.sort(key=lambda x: x["timestamp"], reverse=True)

            # Analyze based on schedule type
            if schedule_type.lower() == "daily":
                return self._analyze_daily_failures(dag_id, incidents)
            elif schedule_type.lower() in ["weekly", "monthly"]:
                return self._analyze_consecutive_failures(
                    dag_id, incidents, schedule_type
                )
            else:
                # Default to daily analysis
                return self._analyze_daily_failures(dag_id, incidents)

        except Exception as e:
            logger.error(f"Error analyzing failure patterns: {e}")
            return {"dag_id": dag_id, "error": str(e), "is_chronic_failure": False}

    def _analyze_daily_failures(
        self, dag_id: str, incidents: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze failures for daily DAGs (7-day window).

        A daily DAG is considered chronically failing if it has:
        - 3 or more failures in 7 days (>40% failure rate)
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=7)

        # Filter incidents within last 7 days
        recent_incidents = []
        failure_incidents = []

        for incident in incidents:
            try:
                incident_date = datetime.fromisoformat(incident["timestamp"])
                if incident_date >= cutoff_date:
                    recent_incidents.append(incident)
                    if incident.get("issue_type") == "failure":
                        failure_incidents.append(incident)
            except Exception:
                continue

        failure_count = len(failure_incidents)
        total_incidents = len(recent_incidents)

        # Determine if chronic failure
        # Daily DAG should run 7 times in 7 days
        expected_runs = 7
        failure_rate = (failure_count / expected_runs) * 100 if expected_runs > 0 else 0

        is_chronic = failure_count >= 3  # 3+ failures in 7 days

        # Determine severity
        if failure_count >= 5:
            severity = "critical"
        elif failure_count >= 3:
            severity = "high"
        elif failure_count >= 2:
            severity = "medium"
        else:
            severity = "low"

        # Generate recommendation
        if is_chronic:
            recommendation = f"URGENT: DAG is chronically failing ({failure_count} failures in 7 days). Immediate investigation required."
        elif failure_count >= 2:
            recommendation = (
                f"Monitor closely: {failure_count} failures detected in the last week."
            )
        else:
            recommendation = "No immediate action required."

        # Check for consecutive failures
        consecutive = self._count_consecutive_failures(failure_incidents)

        return {
            "dag_id": dag_id,
            "schedule_type": "daily",
            "analysis_window": "Last 7 days",
            "is_chronic_failure": is_chronic,
            "failure_count": failure_count,
            "total_incidents": total_incidents,
            "failure_rate": round(failure_rate, 1),
            "consecutive_failures": consecutive,
            "severity": severity,
            "recommendation": recommendation,
            "recent_incidents": failure_incidents[:5],  # Return up to 5 most recent
        }

    def _analyze_consecutive_failures(
        self, dag_id: str, incidents: List[Dict], schedule_type: str
    ) -> Dict[str, Any]:
        """
        Analyze failures for weekly/monthly DAGs (last 3 runs).

        A weekly/monthly DAG is considered chronically failing if:
        - All 3 of the last 3 runs failed
        """
        # Take the 3 most recent incidents
        recent_incidents = incidents[:3]
        failure_incidents = [
            i for i in recent_incidents if i.get("issue_type") == "failure"
        ]

        failure_count = len(failure_incidents)
        total_analyzed = len(recent_incidents)

        # Check if all are consecutive failures
        is_chronic = failure_count == 3 and total_analyzed == 3

        # Determine severity
        if failure_count == 3:
            severity = "critical"
        elif failure_count == 2:
            severity = "high"
        elif failure_count == 1:
            severity = "medium"
        else:
            severity = "low"

        # Generate recommendation
        if is_chronic:
            recommendation = "CRITICAL: All 3 consecutive runs failed. DAG is completely broken. Immediate action required."
        elif failure_count >= 2:
            recommendation = f"HIGH PRIORITY: {failure_count} of last 3 runs failed. Investigation needed."
        elif failure_count == 1:
            recommendation = "Monitor: Recent failure detected in last 3 runs."
        else:
            recommendation = "No failures in last 3 runs."

        consecutive = self._count_consecutive_failures(recent_incidents)

        return {
            "dag_id": dag_id,
            "schedule_type": schedule_type,
            "analysis_window": "Last 3 runs",
            "is_chronic_failure": is_chronic,
            "failure_count": failure_count,
            "total_runs_analyzed": total_analyzed,
            "failure_rate": round(
                (failure_count / total_analyzed * 100) if total_analyzed > 0 else 0, 1
            ),
            "consecutive_failures": consecutive,
            "severity": severity,
            "recommendation": recommendation,
            "recent_incidents": failure_incidents,
        }

    def _count_consecutive_failures(self, incidents: List[Dict]) -> int:
        """Count consecutive failures from most recent incident."""
        consecutive = 0
        for incident in incidents:
            if incident.get("issue_type") == "failure":
                consecutive += 1
            else:
                break
        return consecutive


# Convenience function for tools
def create_memory() -> AgentMemory:
    """Create agent memory instance."""
    return AgentMemory()


# Example usage
if __name__ == "__main__":
    """Demo the memory system."""

    print("🧠 Agent Memory System Demo\n")

    # Create memory
    memory = AgentMemory()

    # Store some incidents
    print("1. Storing incidents...")
    memory.store_incident(
        dag_id="etl_daily",
        issue_type="performance_degradation",
        root_cause="Spark memory overflow - heap space exhausted",
        resolution="Increased memory allocation from 8GB to 24GB",
        severity="high",
        metadata={"duration_increase": "3.5x", "baseline": "45m", "actual": "3.5h"},
    )

    memory.store_incident(
        dag_id="etl_daily",
        issue_type="performance_degradation",
        root_cause="Spark memory overflow - heap space exhausted",
        resolution="Optimized data partitioning",
        severity="medium",
        metadata={"duration_increase": "2.1x"},
    )

    print("✅ Incidents stored\n")

    # Recall incidents
    print("2. Recalling incidents for etl_daily...")
    past_incidents = memory.recall_similar_incidents("etl_daily")

    for incident in past_incidents:
        print(f"\n   📅 {incident['timestamp']}")
        print(f"   🔍 Root Cause: {incident['root_cause']}")
        print(f"   ✅ Resolution: {incident.get('resolution', 'Unknown')}")

    print("\n3. Getting full context...")
    context = memory.get_dag_context("etl_daily")

    print(f"\n   📊 Total Incidents: {context['incident_count']}")
    print(f"   🎯 Most Common: {context['most_common_root_cause']}")
    print(f"   ⚠️  Patterns: {context['patterns']}")

    # Store a pattern
    print("\n4. Storing pattern...")
    memory.store_pattern(
        pattern_type="memory_overflow",
        description="ETL pipelines experiencing memory issues during peak hours",
        affected_dags=["etl_daily", "etl_hourly"],
        confidence=0.92,
    )

    print("\n✅ Memory system working!\n")
    print("💡 Now the agent can learn from history!")
