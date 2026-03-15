"""Analysis Tools - Statistical analysis and anomaly detection"""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class AnalysisTools:
    """
    Statistical analysis and anomaly detection tools.

    Provides the agent with ability to:
    - Detect performance anomalies
    - Calculate statistical metrics
    - Identify patterns and trends
    """

    def __init__(self, anomaly_multiplier: float = 1.5, min_history: int = 10):
        """
        Initialize analysis tools.

        Args:
            anomaly_multiplier: Multiplier for anomaly threshold (default: 1.5x P90)
            min_history: Minimum historical runs required for analysis
        """
        self.anomaly_multiplier = anomaly_multiplier
        self.min_history = min_history
        logger.info(
            f"Analysis tools initialized (anomaly threshold: {anomaly_multiplier}x P90)"
        )

    def detect_anomalies(
        self,
        recent_runs: List[Dict[str, Any]],
        baselines: List[Dict[str, Any]],
        sensitivity: str = "medium",
        focus_area: str = "duration",
    ) -> List[Dict[str, Any]]:
        """
        Detect performance anomalies using statistical analysis.

        Args:
            recent_runs: Recent DAG runs from query_dag_runs
            baselines: Baseline statistics from analyze_performance_baseline
            sensitivity: Detection sensitivity (low/medium/high)
            focus_area: What to analyze (duration/failures/resources)

        Returns:
            List of detected anomalies with details
        """
        try:
            if not recent_runs or not baselines:
                logger.warning("Insufficient data for anomaly detection")
                return []

            # Convert to DataFrames for easier analysis
            recent_df = pd.DataFrame(recent_runs)
            baseline_df = pd.DataFrame(baselines)

            # Merge recent runs with baselines
            merged = recent_df.merge(
                baseline_df[["dag_id", "p90", "p95", "run_count"]],
                on="dag_id",
                how="left",
            )

            # Set threshold based on sensitivity
            threshold_map = {
                "low": 2.0,  # >2x P90
                "medium": 1.5,  # >1.5x P90
                "high": 1.2,  # >1.2x P90
            }
            threshold = threshold_map.get(sensitivity, 1.5)

            # Focus area specific analysis
            if focus_area == "duration":
                # Detect duration anomalies
                merged["is_anomaly"] = (
                    (merged["run_count"] >= self.min_history)
                    & (merged["p90"].notna())
                    & (merged["duration_seconds"] > threshold * merged["p90"])
                )

                merged["deviation_factor"] = merged["duration_seconds"] / merged["p90"]

            elif focus_area == "failures":
                # Focus on failed runs
                merged["is_anomaly"] = merged["state"] == "failed"
                merged["deviation_factor"] = 1.0

            else:  # resources or other
                # General anomaly detection
                merged["is_anomaly"] = (merged["run_count"] >= self.min_history) & (
                    merged["duration_seconds"] > threshold * merged["p90"]
                )
                merged["deviation_factor"] = merged["duration_seconds"] / merged["p90"]

            # Filter to anomalies only
            anomalies = merged[merged["is_anomaly"]].copy()

            # Sort by severity (deviation factor)
            anomalies = anomalies.sort_values("deviation_factor", ascending=False)

            # Convert to list of dicts
            result = []
            for _, row in anomalies.iterrows():
                result.append(
                    {
                        "dag_id": row["dag_id"],
                        "run_id": row["run_id"],
                        "state": row["state"],
                        "duration_seconds": float(row["duration_seconds"]),
                        "baseline_p90": (
                            float(row["p90"]) if pd.notna(row["p90"]) else None
                        ),
                        "deviation_factor": float(row["deviation_factor"]),
                        "severity": self._calculate_severity(row["deviation_factor"]),
                        "confidence": self._calculate_confidence(row["run_count"]),
                    }
                )

            logger.info(
                f"Detected {len(result)} anomalies (sensitivity: {sensitivity})"
            )
            return result

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return []

    def _calculate_severity(self, deviation_factor: float) -> str:
        """Calculate severity level based on deviation."""
        if deviation_factor >= 2.0:
            return "critical"
        elif deviation_factor >= 1.5:
            return "high"
        elif deviation_factor >= 1.2:
            return "medium"
        else:
            return "low"

    def _calculate_confidence(self, sample_size: int) -> float:
        """Calculate confidence score based on sample size."""
        if sample_size >= 30:
            return 0.95
        elif sample_size >= 20:
            return 0.90
        elif sample_size >= 10:
            return 0.85
        else:
            return 0.75


# Tool registry for easy access
