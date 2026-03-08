"""Database Tools - PostgreSQL access to Airflow database"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class DatabaseTools:
    """
    Direct access tools for querying Airflow PostgreSQL database.

    These tools provide the agent with ability to:
    - Query DAG run history
    - Calculate performance baselines
    - Get task-level breakdowns
    - Assess overall system health
    """

    def __init__(self, db_url: str, query_timeout: int = 30):
        """
        Initialize database connection.

        Args:
            db_url: PostgreSQL connection string
            query_timeout: Query timeout in seconds
        """
        self.db_url = db_url
        self.query_timeout = query_timeout
        try:
            self.engine = create_engine(
                db_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,  # Recycle connections after 1 hour
                connect_args={"connect_timeout": 10},
            )
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def _serialize_row(self, row_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert database row to JSON-serializable format.

        Converts:
        - datetime objects to ISO format strings
        - Decimal objects to floats
        - None values are preserved

        Args:
            row_dict: Dictionary from database row

        Returns:
            JSON-serializable dictionary
        """
        serialized = {}
        for key, value in row_dict.items():
            if value is None:
                serialized[key] = None
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                serialized[key] = float(value)
            else:
                serialized[key] = value
        return serialized

    def query_dag_runs(
        self,
        window_hours: int = 24,
        dag_id_pattern: Optional[str] = None,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query recent DAG runs from Airflow database.

        Args:
            window_hours: Hours of history to retrieve
            dag_id_pattern: Optional SQL LIKE pattern for DAG IDs
            state: Optional state filter (success, failed, running)

        Returns:
            List of DAG run dictionaries with execution details
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

            # Build query dynamically based on filters
            query = """
                SELECT
                    dag_id,
                    run_id,
                    state,
                    start_date,
                    end_date,
                    execution_date,
                    EXTRACT(EPOCH FROM (
                        COALESCE(end_date, NOW()) - start_date
                    )) as duration_seconds
                FROM dag_run
                WHERE start_date >= :cutoff
            """

            params = {"cutoff": cutoff}

            if dag_id_pattern:
                query += " AND dag_id LIKE :pattern"
                params["pattern"] = dag_id_pattern

            if state:
                query += " AND state = :state"
                params["state"] = state

            query += " ORDER BY start_date DESC LIMIT 100"

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query).execution_options(timeout=self.query_timeout), params
                )
                rows = [self._serialize_row(dict(row._mapping)) for row in result]

            logger.info(f"Retrieved {len(rows)} DAG runs (window: {window_hours}h)")
            return rows

        except SQLAlchemyError as e:
            logger.error(f"Database error in query_dag_runs: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in query_dag_runs: {e}")
            return []

    def analyze_performance_baseline(
        self, days: int = 14, dag_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate performance baselines (percentiles) for DAG runs.

        Args:
            days: Days of historical data to analyze
            dag_id: Optional specific DAG to analyze

        Returns:
            List of baseline statistics per DAG
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)

            query = """
                WITH dag_durations AS (
                    SELECT
                        dag_id,
                        EXTRACT(EPOCH FROM (end_date - start_date)) as duration_seconds
                    FROM dag_run
                    WHERE start_date >= :cutoff
                      AND state = 'success'
                      AND end_date IS NOT NULL
                      AND start_date IS NOT NULL
                      {dag_filter}
                )
                SELECT
                    dag_id,
                    COUNT(*) as run_count,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as p50,
                    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duration_seconds) as p90,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_seconds) as p95,
                    AVG(duration_seconds) as mean_duration,
                    STDDEV(duration_seconds) as stddev_duration,
                    MIN(duration_seconds) as min_duration,
                    MAX(duration_seconds) as max_duration
                FROM dag_durations
                GROUP BY dag_id
                HAVING COUNT(*) >= 5
                ORDER BY dag_id
            """

            dag_filter = "AND dag_id = :dag_id" if dag_id else ""
            query = query.format(dag_filter=dag_filter)

            params = {"cutoff": cutoff}
            if dag_id:
                params["dag_id"] = dag_id

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query).execution_options(timeout=self.query_timeout), params
                )
                rows = [self._serialize_row(dict(row._mapping)) for row in result]

            logger.info(f"Calculated baselines for {len(rows)} DAGs ({days} days)")
            return rows

        except SQLAlchemyError as e:
            logger.error(f"Database error in analyze_performance_baseline: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in analyze_performance_baseline: {e}")
            return []

    def get_task_breakdown(self, dag_id: str, run_id: str) -> List[Dict[str, Any]]:
        """
        Get task-level breakdown for a specific DAG run.

        Args:
            dag_id: DAG identifier
            run_id: Run identifier (or 'latest' for most recent)

        Returns:
            List of task execution details
        """
        try:
            # If run_id is 'latest', get the most recent run_id
            if run_id.lower() == "latest":
                latest_query = """
                    SELECT run_id
                    FROM dag_run
                    WHERE dag_id = :dag_id
                    ORDER BY start_date DESC
                    LIMIT 1
                """
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text(latest_query), {"dag_id": dag_id}
                    ).fetchone()

                    if not result:
                        logger.warning(f"No runs found for DAG: {dag_id}")
                        return []

                    run_id = result[0]
                    logger.info(f"Using latest run_id: {run_id}")

            # Get task breakdown
            query = """
                SELECT
                    task_id,
                    state,
                    start_date,
                    end_date,
                    EXTRACT(EPOCH FROM (
                        COALESCE(end_date, NOW()) - start_date
                    )) as duration_seconds,
                    try_number,
                    max_tries,
                    queue,
                    pool,
                    operator
                FROM task_instance
                WHERE dag_id = :dag_id
                  AND run_id = :run_id
                ORDER BY start_date
            """

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query).execution_options(timeout=self.query_timeout),
                    {"dag_id": dag_id, "run_id": run_id},
                )
                rows = [self._serialize_row(dict(row._mapping)) for row in result]

            logger.info(f"Retrieved {len(rows)} tasks for {dag_id}/{run_id}")
            return rows

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_task_breakdown: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_task_breakdown: {e}")
            return []

    def get_dag_health_summary(self, include_stale: bool = True) -> Dict[str, Any]:
        """
        Get high-level health summary for all DAGs.

        Args:
            include_stale: Include stale/inactive DAGs in analysis

        Returns:
            Dictionary with health metrics
        """
        try:
            # Get total DAG count and states
            summary_query = """
                WITH recent_runs AS (
                    SELECT DISTINCT ON (dag_id)
                        dag_id,
                        state,
                        start_date,
                        end_date
                    FROM dag_run
                    WHERE start_date >= NOW() - INTERVAL '7 days'
                    ORDER BY dag_id, start_date DESC
                ),
                all_dags AS (
                    SELECT DISTINCT dag_id FROM dag_run
                )
                SELECT
                    (SELECT COUNT(DISTINCT dag_id) FROM all_dags) as total_dags,
                    (SELECT COUNT(*) FROM recent_runs WHERE state = 'success') as success_count,
                    (SELECT COUNT(*) FROM recent_runs WHERE state = 'failed') as failed_count,
                    (SELECT COUNT(*) FROM recent_runs WHERE state = 'running') as running_count,
                    (SELECT COUNT(*) FROM recent_runs) as active_dags
            """

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(summary_query).execution_options(timeout=self.query_timeout)
                ).fetchone()

                if not result:
                    return {"error": "No data available"}

                summary = self._serialize_row(dict(result._mapping))

                # Calculate health percentage
                total = summary["success_count"] + summary["failed_count"]
                health_pct = (
                    (summary["success_count"] / total * 100) if total > 0 else 0
                )

                summary["health_percentage"] = round(health_pct, 2)

                logger.info(
                    f"Health summary: {summary['active_dags']}/{summary['total_dags']} active, "
                    f"{health_pct:.1f}% healthy"
                )

                return summary

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_dag_health_summary: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in get_dag_health_summary: {e}")
            return {"error": str(e)}
