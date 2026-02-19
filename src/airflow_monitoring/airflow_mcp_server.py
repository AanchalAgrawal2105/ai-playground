import sys
import logging
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from sqlalchemy import create_engine, text
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta


# Load environment variables from .env file
load_dotenv()  # pragma: no cover

# Create a server instance with a descriptive name
mcp = FastMCP(name="Airflow Runtime MCP Server")  # pragma: no cover

AIRFLOW_DB_URL = os.environ["AIRFLOW_DB_URL"]  # e.g. postgresql+psycopg2://user:pass@host:5432/airflow  # pragma: no cover
engine = create_engine(AIRFLOW_DB_URL, pool_pre_ping=True)  # pragma: no cover

def _rows_to_dicts(result) -> List[Dict[str, Any]]:
    columns = result.keys()
    rows_data = []
    for row in result.fetchall():
        row_dict = {}
        for i, column in enumerate(columns):
            value = row[i]
            # Convert datetime objects to ISO strings for JSON serialization
            if hasattr(value, 'isoformat'):
                row_dict[column] = value.isoformat()
            elif value is None:
                row_dict[column] = None
            else:
                row_dict[column] = str(value) if not isinstance(value, (int, float, bool)) else value
        rows_data.append(row_dict)
    return rows_data

def _test_db_connection() -> Dict[str, Any]:
    """Internal function to test the Airflow database connection"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            # Get database version
            version_result = conn.execute(text("SELECT version()"))
            db_version = version_result.fetchone()[0]
            
            # Check if this looks like an Airflow DB by checking for key tables
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('dag', 'dag_run', 'task_instance')
            """))
            airflow_tables = [row[0] for row in tables_result.fetchall()]
            
            return {
                "status": "success",
                "connection_test": test_value == 1,
                "database_version": db_version,
                "airflow_tables_found": airflow_tables,
                "is_airflow_db": len(airflow_tables) >= 2,  # Should have at least dag and dag_run tables
                "connection_url_masked": AIRFLOW_DB_URL.split('@')[1] if '@' in AIRFLOW_DB_URL else "N/A"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__,
            "connection_url_masked": AIRFLOW_DB_URL.split('@')[1] if '@' in AIRFLOW_DB_URL else "N/A"
        }

@mcp.tool
def test_db_connection() -> Dict[str, Any]:
    """Test the Airflow database connection and return connection details"""
    return _test_db_connection()

@mcp.tool
def get_dag_runs(window_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Fetch DAG runs started within the last `window_hours`.
    Includes running + completed. Excludes backfill run_id.
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=window_hours)

    # NOTE: For Airflow 2.x this is usually correct: dag_run has dag_id, run_id, state, start_date, end_date.
    sql = text("""
        SELECT dag_id, run_id, state, start_date, end_date
        FROM dag_run
        WHERE start_date >= :since
          AND start_date IS NOT NULL
          AND dag_id IS NOT NULL
          AND (run_id NOT LIKE 'backfill%')
        ORDER BY start_date DESC
        LIMIT 5000
    """)

    # Log the query being executed
    logging.info(f"Executing get_dag_runs query:")
    logging.info(f"SQL: {sql}")
    logging.info(f"Parameters: since={since}, window_hours={window_hours}")

    with engine.connect() as conn:
        res = conn.execute(sql, {"since": since})
        rows = _rows_to_dicts(res)
        logging.info(f"Query returned {len(rows)} rows")
        
        return rows


@mcp.tool
def get_baseline_durations(days: int = 14) -> List[Dict[str, Any]]:
    """
    Fetch completed successful DAG runs within the last `days`
    for baseline duration calculations.
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    sql = text("""
        SELECT dag_id, start_date, end_date
        FROM dag_run
        WHERE start_date >= :since
          AND start_date IS NOT NULL
          AND end_date IS NOT NULL
          AND dag_id IS NOT NULL
          AND state = 'success'
          AND (run_id NOT LIKE 'backfill%')
        LIMIT 200000
    """)

    # Log the query being executed
    logging.info(f"Executing get_baseline_durations query:")
    logging.info(f"SQL: {sql}")
    logging.info(f"Parameters: since={since}, days={days}")

    with engine.connect() as conn:
        res = conn.execute(sql, {"since": since})
        rows = _rows_to_dicts(res)
        logging.info(f"Query returned {len(rows)} baseline rows")
        
        return rows


@mcp.tool
def get_paused_dags() -> List[Dict[str, Any]]:
    """
    Fetch all paused DAGs that are currently inactive.
    """
    sql = text("""
        SELECT 
            dag_id,
            is_paused,
            is_active,
            last_parsed_time,
            last_pickled,
            description,
            schedule_interval,
            fileloc
        FROM dag
        WHERE is_paused = true
          AND is_active = true
        ORDER BY dag_id
    """)

    logging.info("Executing get_paused_dags query:")
    logging.info(f"SQL: {sql}")

    with engine.connect() as conn:
        res = conn.execute(sql)
        rows = _rows_to_dicts(res)
        logging.info(f"Query returned {len(rows)} paused DAGs")
        
        return rows


@mcp.tool
def get_stale_dags(days_inactive: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch DAGs that haven't run for longer than expected based on their schedule.
    Uses schedule-aware thresholds:
    - Daily DAGs: stale if no run in 10+ days
    - Weekly DAGs: stale if no run in 14+ days (2 weeks)
    - Monthly DAGs: stale if no run in 35+ days
    - Hourly DAGs: stale if no run in 2+ days
    
    Args:
        days_inactive: Base threshold for unknown/custom schedules (default: 10)
    """
    now = datetime.now(timezone.utc)
    
    sql = text("""
        WITH latest_dag_runs AS (
            SELECT 
                dag_id,
                MAX(start_date) as last_run_date,
                MAX(execution_date) as last_execution_date,
                COUNT(*) as total_runs
            FROM dag_run 
            WHERE start_date IS NOT NULL
            GROUP BY dag_id
        ),
        active_dags AS (
            SELECT 
                dag_id,
                is_paused,
                is_active,
                schedule_interval,
                last_parsed_time,
                description
            FROM dag 
            WHERE is_active = true
        ),
        dag_staleness AS (
            SELECT 
                ad.dag_id,
                ad.is_paused,
                ad.schedule_interval,
                ad.description,
                ad.last_parsed_time,
                ldr.last_run_date,
                ldr.last_execution_date,
                ldr.total_runs,
                EXTRACT(days FROM (:now - COALESCE(ldr.last_run_date, ad.last_parsed_time))) as days_since_last_run,
                CASE 
                    -- Weekly schedules: stale if no run in 14+ days (2 weeks)
                    WHEN ad.schedule_interval IN ('@weekly', '0 0 * * 0', '0 0 * * SUN') 
                        THEN 14
                    -- Monthly schedules: stale if no run in 35+ days (monthly + 5 day buffer)  
                    WHEN ad.schedule_interval IN ('@monthly', '0 0 1 * *')
                        THEN 35
                    -- Daily schedules: stale if no run in 10+ days
                    WHEN ad.schedule_interval IN ('@daily', '0 0 * * *')
                        THEN 10
                    -- Hourly schedules: stale if no run in 2+ days
                    WHEN ad.schedule_interval IN ('@hourly', '0 * * * *')
                        THEN 2
                    -- @once schedules: never considered stale (they run once)
                    WHEN ad.schedule_interval = '@once'
                        THEN 99999
                    -- Cron expressions with weekly patterns (every Sunday, etc.)
                    WHEN ad.schedule_interval SIMILAR TO '0 [0-9]+ \* \* (0|SUN|7)'
                        THEN 14
                    -- Other cron expressions: use 10 days as default for unknown schedules
                    ELSE 10
                END as staleness_threshold_days
            FROM active_dags ad
            LEFT JOIN latest_dag_runs ldr ON ad.dag_id = ldr.dag_id
        )
        SELECT 
            dag_id,
            is_paused,
            schedule_interval,
            description,
            last_parsed_time,
            last_run_date,
            last_execution_date,
            total_runs,
            days_since_last_run,
            staleness_threshold_days,
            CASE 
                WHEN schedule_interval = '@weekly' THEN 'Weekly'
                WHEN schedule_interval = '@monthly' THEN 'Monthly' 
                WHEN schedule_interval = '@daily' THEN 'Daily'
                WHEN schedule_interval = '@hourly' THEN 'Hourly'
                ELSE 'Custom'
            END as schedule_type
        FROM dag_staleness
        WHERE (
            last_run_date IS NULL 
            OR days_since_last_run > staleness_threshold_days
        )
        AND schedule_interval != '@once'  -- Exclude one-time DAGs
        AND schedule_interval IS NOT NULL -- Exclude manually triggered DAGs
        AND is_paused = false  -- Exclude paused DAGs (they have their own category)
        ORDER BY days_since_last_run DESC
    """)

    logging.info(f"Executing get_stale_dags query with schedule-aware detection:")
    logging.info(f"SQL: {sql}")
    logging.info(f"Parameters: days_inactive={days_inactive}")

    with engine.connect() as conn:
        res = conn.execute(sql, {
            "days_inactive": days_inactive,
            "now": now
        })
        rows = _rows_to_dicts(res)
        logging.info(f"Query returned {len(rows)} schedule-aware stale DAGs")
        
        return rows


@mcp.tool
def get_dag_health_summary() -> Dict[str, Any]:
    """
    Get a comprehensive health summary of all DAGs including paused and stale counts.
    """
    now = datetime.now(timezone.utc)
    
    # Get counts of different DAG states
    summary_sql = text("""
        WITH dag_stats AS (
            SELECT 
                COUNT(*) as total_dags,
                SUM(CASE WHEN is_paused = true THEN 1 ELSE 0 END) as paused_dags,
                SUM(CASE WHEN is_active = false THEN 1 ELSE 0 END) as inactive_dags,
                SUM(CASE WHEN is_active = true AND is_paused = false THEN 1 ELSE 0 END) as active_dags
            FROM dag
        ),
        recent_runs AS (
            SELECT 
                COUNT(DISTINCT dag_id) as dags_with_recent_runs
            FROM dag_run 
            WHERE start_date >= :seven_days_ago
        ),
        stale_runs AS (
            SELECT 
                COUNT(DISTINCT d.dag_id) as stale_dags
            FROM dag d
            LEFT JOIN (
                SELECT dag_id, MAX(start_date) as last_run
                FROM dag_run 
                WHERE start_date IS NOT NULL
                GROUP BY dag_id
            ) lr ON d.dag_id = lr.dag_id
            WHERE d.is_active = true
              AND d.schedule_interval IS NOT NULL 
              AND d.schedule_interval != '@once'
              AND (lr.last_run IS NULL OR lr.last_run < :seven_days_ago)
        )
        SELECT 
            ds.*,
            rr.dags_with_recent_runs,
            sr.stale_dags
        FROM dag_stats ds, recent_runs rr, stale_runs sr
    """)

    seven_days_ago = now - timedelta(days=7)
    
    logging.info("Executing get_dag_health_summary query:")
    logging.info(f"Parameters: seven_days_ago={seven_days_ago}")

    with engine.connect() as conn:
        res = conn.execute(summary_sql, {
            "seven_days_ago": seven_days_ago
        })
        summary_row = res.fetchone()
        
        if summary_row:
            summary = {
                "generated_at": now.isoformat(),
                "total_dags": summary_row[0],
                "paused_dags": summary_row[1], 
                "inactive_dags": summary_row[2],
                "active_dags": summary_row[3],
                "dags_with_recent_runs": summary_row[4],
                "stale_dags": summary_row[5],
                "health_percentage": round((summary_row[4] / summary_row[0]) * 100, 2) if summary_row[0] > 0 else 0
            }
        else:
            summary = {
                "generated_at": now.isoformat(),
                "total_dags": 0,
                "paused_dags": 0,
                "inactive_dags": 0, 
                "active_dags": 0,
                "dags_with_recent_runs": 0,
                "stale_dags": 0,
                "health_percentage": 0
            }
        
        logging.info(f"DAG health summary: {summary}")
        return summary

def main():  # pragma: no cover
    """Main entry point for the Airflow MCP server"""
    # Configure logging to stderr so it doesn't interfere with MCP protocol
    logging.basicConfig(  # pragma: no cover
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    # Test database connection on startup (log to stderr)
    connection_test = _test_db_connection()  # pragma: no cover
    
    # Log connection status to stderr (won't break MCP protocol)
    if connection_test["status"] == "error":  # pragma: no cover
        logging.error(f"Database connection failed: {connection_test['error_message']}")  # pragma: no cover
        logging.info("Starting MCP server anyway - tools will return error responses")  # pragma: no cover
    else:  # pragma: no cover
        logging.info("Database connection successful")  # pragma: no cover
    
    # Start MCP server (only JSON-RPC messages go to stdout)
    mcp.run()  # pragma: no cover

if __name__ == "__main__":
    main()
