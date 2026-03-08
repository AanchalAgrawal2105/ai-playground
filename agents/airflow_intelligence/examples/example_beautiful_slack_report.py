#!/usr/bin/env python3
"""
Example: Send Beautifully Formatted Slack Reports

This script demonstrates how to use the enhanced Slack formatter
to send professional, well-structured reports to Slack.
"""

import os
from agents.airflow_intelligence.tools import SlackTools

def send_beautiful_report():
    """
    Example: Send a beautifully formatted health report to Slack.
    """

    # Initialize Slack tools
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set. Please set it in your environment.")
        return

    slack_tools = SlackTools(
        slack_token=slack_token,
        default_channel="#airflow-monitoring"
    )

    # Sample data for the report
    critical_issues = [
        {
            'dag_id': 'pricing-service-curated.pipeline-product.product.curated',
            'duration_seconds': 275.2,
            'baseline_p90': 82.2,
            'deviation_factor': 3.35,
            'root_cause': 'Spark job execution time increased from ~30s to 212s',
            'impact': 'Critical pricing data delays'
        },
        {
            'dag_id': 'regional-pricing-curated.pipeline-product-price.product_price.curated',
            'duration_seconds': 243.7,
            'baseline_p90': 82.0,
            'deviation_factor': 2.97,
            'root_cause': 'Spark job execution time increased from ~30s to 182s',
            'impact': 'Regional pricing updates delayed'
        }
    ]

    failures = [
        {'dag_id': 'ops-dap-bi-enriched.pipeline-production_assets.dashboard', 'duration_hours': 1.2},
        {'dag_id': 'ops-dap-bi-enriched.pipeline-production_errors.errors', 'duration_hours': 0.8},
        {'dag_id': 'ops-dap-bi-enriched.pipeline-br-metrics.metrics', 'duration_hours': 0.5},
        {'dag_id': 'loyalty-enriched.pipeline-crm-comms-savings.savings', 'duration_hours': 1.5},
        {'dag_id': 'loyalty-enriched.pipeline-customer-data.customers', 'duration_hours': 0.9},
        {'dag_id': 'loyalty-enriched.pipeline-rewards.rewards', 'duration_hours': 1.1},
    ]

    recommendations = [
        {
            'priority': 'URGENT',
            'action': 'Investigate EMR EKS cluster resource allocation for pricing pipelines'
        },
        {
            'priority': 'HIGH',
            'action': 'Check ops-dap-bi-enriched infrastructure dependencies'
        },
        {
            'priority': 'MEDIUM',
            'action': 'Review loyalty pipeline data sources and connections'
        },
        {
            'priority': 'MEDIUM',
            'action': 'Set up enhanced alerting for pricing pipeline performance'
        }
    ]

    consistently_failing_dags = [
        {
            'dag_id': 'loyalty-enriched.pipeline-crm-comms-savings',
            'failure_count': 6,
            'consecutive_failures': 4,
            'last_success_date': '2026-03-04T10:30:00Z'
        },
        {
            'dag_id': 'ops-dap-bi-enriched.pipeline-production_assets',
            'failure_count': 5,
            'consecutive_failures': 3,
            'last_success_date': '2026-03-03T15:20:00Z'
        },
        {
            'dag_id': 'global-errors-enriched.pipeline-main-cc-errors',
            'failure_count': 3,
            'consecutive_failures': 3,
            'last_success_date': 'Never'
        }
    ]

    # Send the beautifully formatted report
    print("📤 Sending beautifully formatted health report to Slack...")

    result = slack_tools.send_health_report(
        overall_health=97.37,
        active_dags=587,
        critical_issues=critical_issues,
        failures=failures,
        anomalies=critical_issues,  # Same as critical_issues in this example
        recommendations=recommendations,
        consistently_failing_dags=consistently_failing_dags,
        confidence_level="High"
    )

    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   Channel: {result['channel']}")
        print(f"   Timestamp: {result['timestamp']}")
    else:
        print(f"❌ Failed to send report: {result['error']}")


def send_simple_alert():
    """
    Example: Send a simple formatted alert to Slack.
    """

    # Initialize Slack tools
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not set. Please set it in your environment.")
        return

    slack_tools = SlackTools(
        slack_token=slack_token,
        default_channel="#airflow-monitoring"
    )

    print("📤 Sending formatted alert to Slack...")

    result = slack_tools.send_formatted_alert(
        severity="warning",
        title="Performance Degradation Detected",
        message=(
            "The pricing pipeline is experiencing significant slowdown.\n\n"
            "*Analysis:*\n"
            "• Duration increased from 82s to 275s (3.35x slower)\n"
            "• Spark job execution is the bottleneck\n"
            "• Resource contention likely cause\n\n"
            "*Impact:* Critical pricing data is delayed by ~3 minutes"
        ),
        fields={
            "Pipeline": "pricing-service-curated",
            "Duration": "275.2 seconds",
            "Baseline": "82.2 seconds",
            "Deviation": "3.35x"
        }
    )

    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   Channel: {result['channel']}")
        print(f"   Timestamp: {result['timestamp']}")
    else:
        print(f"❌ Failed to send alert: {result['error']}")


if __name__ == "__main__":
    print("✨ Beautiful Slack Report Examples\n")
    print("=" * 60)

    # Example 1: Send comprehensive health report
    print("\n📊 Example 1: Comprehensive Health Report")
    print("-" * 60)
    send_beautiful_report()

    print("\n")

    # Example 2: Send simple alert
    print("⚠️  Example 2: Simple Formatted Alert")
    print("-" * 60)
    send_simple_alert()

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("\n💡 Tips:")
    print("   - Use send_health_report() for comprehensive status updates")
    print("   - Use send_formatted_alert() for quick notifications")
    print("   - Both methods use Slack's Block Kit for beautiful formatting")
    print("   - Customize the formatter in slack_formatter.py if needed")
