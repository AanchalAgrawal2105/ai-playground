#!/usr/bin/env python3
"""
Test Script: Failure Pattern Analysis

This script demonstrates the new chronic failure detection capability.
It simulates different failure scenarios and shows how the agent detects patterns.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.airflow_intelligence.src.core.memory import AgentMemory


def get_temp_memory():
    """Create AgentMemory with temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    return AgentMemory(memory_dir=temp_dir), temp_dir


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_analysis_result(result):
    """Pretty print analysis result."""
    print(f"📊 Analysis Result for {result['dag_id']}:")
    print(f"   Schedule: {result.get('schedule_type', 'unknown')}")
    print(f"   Analysis Window: {result.get('analysis_window', 'N/A')}")
    print(f"   Failure Count: {result.get('failure_count', 0)}")
    print(f"   Failure Rate: {result.get('failure_rate', 0)}%")

    if result.get("consecutive_failures"):
        print(f"   Consecutive Failures: {result['consecutive_failures']}")

    is_chronic = result.get("is_chronic_failure", False)
    severity = result.get("severity", "unknown")

    if is_chronic:
        print(f"   Status: ⚠️ CHRONIC FAILURE")
    else:
        print(f"   Status: ✅ Not Chronic")

    print(f"   Severity: {severity.upper()}")
    print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
    print()


def test_daily_dag_chronic_failure():
    """Test chronic failure detection for daily DAG."""
    print_section("Test 1: Daily DAG - Chronic Failure (5 failures in 7 days)")

    memory, temp_dir = get_temp_memory()

    # Simulate 5 failures in the last 7 days
    print("Simulating 5 failures for 'etl_daily' over 7 days...")
    for i in range(5):
        memory.store_incident(
            dag_id="etl_daily",
            issue_type="failure",
            root_cause="Database connection timeout",
            resolution=None,
            severity="high",
        )
    print("✅ Stored 5 failure incidents\n")

    # Analyze
    print("Analyzing failure patterns...")
    result = memory.analyze_failure_patterns("etl_daily", "daily")
    print_analysis_result(result)

    # Verify
    assert result["is_chronic_failure"] == True, "Should detect chronic failure"
    assert result["severity"] in ["high", "critical"], "Should be high severity"
    print("✅ Test passed: Chronic failure correctly detected!\n")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_daily_dag_not_chronic():
    """Test that daily DAG with few failures is not chronic."""
    print_section("Test 2: Daily DAG - Not Chronic (2 failures in 7 days)")

    memory, temp_dir = get_temp_memory()

    # Simulate only 2 failures
    print("Simulating 2 failures for 'data_validation'...")
    for i in range(2):
        memory.store_incident(
            dag_id="data_validation",
            issue_type="failure",
            root_cause="Data quality check failed",
            severity="medium",
        )
    print("✅ Stored 2 failure incidents\n")

    # Analyze
    print("Analyzing failure patterns...")
    result = memory.analyze_failure_patterns("data_validation", "daily")
    print_analysis_result(result)

    # Verify
    assert result["is_chronic_failure"] == False, "Should NOT detect chronic failure"
    print("✅ Test passed: Not chronic (as expected)\n")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_weekly_dag_chronic_failure():
    """Test chronic failure detection for weekly DAG."""
    print_section("Test 3: Weekly DAG - Chronic Failure (3/3 consecutive failures)")

    memory, temp_dir = get_temp_memory()

    # Simulate 3 consecutive failures
    print("Simulating 3 consecutive failures for 'weekly_report'...")
    for i in range(3):
        memory.store_incident(
            dag_id="weekly_report",
            issue_type="failure",
            root_cause="Spark job out of memory",
            severity="critical",
        )
    print("✅ Stored 3 failure incidents\n")

    # Analyze
    print("Analyzing failure patterns...")
    result = memory.analyze_failure_patterns("weekly_report", "weekly")
    print_analysis_result(result)

    # Verify
    assert result["is_chronic_failure"] == True, "Should detect chronic failure"
    assert result["severity"] == "critical", "Should be critical severity"
    assert result["failure_count"] == 3, "Should have 3 failures"
    print("✅ Test passed: Weekly chronic failure correctly detected!\n")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_monthly_dag_partial_failures():
    """Test monthly DAG with partial failures (not chronic)."""
    print_section("Test 4: Monthly DAG - Not Chronic (2/3 failures)")

    memory, temp_dir = get_temp_memory()

    # Simulate 2 failures, 1 success (different issue types)
    print("Simulating 2 failures and 1 non-failure for 'monthly_aggregation'...")

    memory.store_incident(
        dag_id="monthly_aggregation",
        issue_type="failure",
        root_cause="Data source unavailable",
        severity="high",
    )

    memory.store_incident(
        dag_id="monthly_aggregation",
        issue_type="performance_degradation",  # Not a failure
        root_cause="Slow query performance",
        severity="medium",
    )

    memory.store_incident(
        dag_id="monthly_aggregation",
        issue_type="failure",
        root_cause="API timeout",
        severity="high",
    )
    print("✅ Stored 3 incidents (2 failures, 1 other)\n")

    # Analyze
    print("Analyzing failure patterns...")
    result = memory.analyze_failure_patterns("monthly_aggregation", "monthly")
    print_analysis_result(result)

    # Verify
    assert (
        result["is_chronic_failure"] == False
    ), "Should NOT be chronic (only 2/3 failed)"
    assert result["severity"] in ["high", "medium"], "Should be high severity"
    print("✅ Test passed: Not chronic with 2/3 failures (as expected)\n")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_no_history():
    """Test DAG with no historical data."""
    print_section("Test 5: DAG with No Historical Data")

    memory, temp_dir = get_temp_memory()

    print("Analyzing 'new_dag' with no historical incidents...")
    result = memory.analyze_failure_patterns("new_dag", "daily")
    print_analysis_result(result)

    # Verify
    assert result["is_chronic_failure"] == False, "Should not be chronic with no data"
    assert result["failure_count"] == 0, "Should have 0 failures"
    print("✅ Test passed: No false positives with empty history\n")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_mixed_scenarios():
    """Test comprehensive scenario with multiple DAGs."""
    print_section("Test 6: Comprehensive Multi-DAG Analysis")

    memory, temp_dir = get_temp_memory()

    print("Setting up complex scenario with 5 DAGs:\n")

    # DAG 1: Critical daily failure
    print("1. etl_production (daily) - 6 failures in 7 days")
    for i in range(6):
        memory.store_incident(
            dag_id="etl_production",
            issue_type="failure",
            root_cause="Network timeout",
            severity="critical",
        )

    # DAG 2: Medium daily issues
    print("2. data_sync (daily) - 2 failures in 7 days")
    for i in range(2):
        memory.store_incident(
            dag_id="data_sync",
            issue_type="failure",
            root_cause="Rate limit exceeded",
            severity="medium",
        )

    # DAG 3: Weekly complete failure
    print("3. weekly_summary (weekly) - 3/3 consecutive failures")
    for i in range(3):
        memory.store_incident(
            dag_id="weekly_summary",
            issue_type="failure",
            root_cause="Report template broken",
            severity="critical",
        )

    # DAG 4: Performance issue (not failures)
    print("4. analytics_pipeline (daily) - Performance degradation only")
    for i in range(3):
        memory.store_incident(
            dag_id="analytics_pipeline",
            issue_type="performance_degradation",
            root_cause="Slow queries",
            severity="medium",
        )

    # DAG 5: Single failure
    print("5. backup_job (daily) - 1 failure")
    memory.store_incident(
        dag_id="backup_job",
        issue_type="failure",
        root_cause="Disk space",
        severity="low",
    )

    print("\n✅ Setup complete. Analyzing all DAGs...\n")

    # Analyze all
    dags = [
        ("etl_production", "daily"),
        ("data_sync", "daily"),
        ("weekly_summary", "weekly"),
        ("analytics_pipeline", "daily"),
        ("backup_job", "daily"),
    ]

    chronic_dags = []

    print("-" * 80)
    print("ANALYSIS RESULTS:")
    print("-" * 80)

    for dag_id, schedule in dags:
        result = memory.analyze_failure_patterns(dag_id, schedule)
        print(f"\n{dag_id}:")
        print(f"  Failures: {result.get('failure_count', 0)}")
        print(f"  Chronic: {'⚠️ YES' if result.get('is_chronic_failure') else '✅ No'}")
        print(f"  Severity: {result.get('severity', 'unknown').upper()}")

        if result.get("is_chronic_failure"):
            chronic_dags.append(dag_id)

    print("\n" + "-" * 80)
    print(f"SUMMARY: {len(chronic_dags)} chronic failures detected")
    print("-" * 80)

    if chronic_dags:
        print("\n⚠️ CHRONICALLY FAILING DAGs (Require Immediate Attention):")
        for i, dag_id in enumerate(chronic_dags, 1):
            print(f"   {i}. {dag_id}")

    print("\n✅ Test passed: Complex scenario correctly analyzed!\n")

    # Verify
    assert "etl_production" in chronic_dags, "etl_production should be chronic"
    assert "weekly_summary" in chronic_dags, "weekly_summary should be chronic"
    assert (
        "data_sync" not in chronic_dags
    ), "data_sync should NOT be chronic (only 2 failures)"
    assert (
        "analytics_pipeline" not in chronic_dags
    ), "analytics_pipeline should NOT be chronic (no failures)"
    assert (
        "backup_job" not in chronic_dags
    ), "backup_job should NOT be chronic (only 1 failure)"

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all tests."""
    print()
    print("=" * 80)
    print("  🧪 FAILURE PATTERN ANALYSIS - TEST SUITE")
    print("=" * 80)
    print()
    print("This test suite demonstrates the new chronic failure detection capability.")
    print()

    try:
        # Run tests
        test_daily_dag_chronic_failure()
        test_daily_dag_not_chronic()
        test_weekly_dag_chronic_failure()
        test_monthly_dag_partial_failures()
        test_no_history()
        test_mixed_scenarios()

        # Summary
        print_section("✅ ALL TESTS PASSED!")
        print("Your agent can now:")
        print("  ✅ Detect chronic failures for daily DAGs (7-day analysis)")
        print("  ✅ Detect chronic failures for weekly/monthly DAGs (3-run analysis)")
        print("  ✅ Distinguish one-off failures from systematic issues")
        print("  ✅ Provide severity-based recommendations")
        print("  ✅ Prioritize which DAGs need immediate attention")
        print()
        print("🎉 Failure Pattern Analysis is working perfectly!")
        print()
        print("📚 Next Steps:")
        print(
            "  1. Test with real agent: python -m agents.airflow_intelligence.cli chat"
        )
        print("  2. Ask: 'Find chronically failing DAGs'")
        print("  3. Watch agent use analyze_failure_patterns() automatically!")
        print()
        print("📖 Documentation: See FAILURE_PATTERN_ANALYSIS.md")
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
