"""
Enhanced Slack Formatting for Airflow Intelligence Reports

This module provides utilities to create beautifully formatted Slack messages
using Slack's Block Kit API for better visual hierarchy and readability.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SlackReportFormatter:
    """
    Create beautifully formatted Slack reports using Block Kit.

    Features:
    - Rich visual hierarchy with sections, dividers, fields
    - Color-coded severity indicators
    - Structured data presentation
    - Enhanced readability
    """

    @staticmethod
    def create_health_report_blocks(
        overall_health: float,
        active_dags: int,
        critical_issues: List[Dict[str, Any]],
        failures: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        recommendations: List[str],
        consistently_failing_dags: Optional[List[Dict[str, Any]]] = None,
        confidence_level: str = "High",
    ) -> List[Dict[str, Any]]:
        """
        Create a comprehensive health report with beautiful formatting.

        Args:
            overall_health: Health percentage (0-100)
            active_dags: Number of active DAGs
            critical_issues: List of critical performance issues
            failures: List of pipeline failures
            anomalies: List of detected anomalies
            recommendations: List of action recommendations
            consistently_failing_dags: List of DAGs failing consistently (with failure_count, last_success_date)
            confidence_level: Analysis confidence (High/Medium/Low)

        Returns:
            List of Slack blocks for the report
        """
        blocks = []

        # 1. HEADER with status indicator
        health_emoji = (
            "🟢" if overall_health >= 95 else "🟡" if overall_health >= 85 else "🔴"
        )
        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{health_emoji} Critical: Airflow Pipeline Health Report",
                    "emoji": True,
                },
            }
        )

        # 2. EXECUTIVE SUMMARY with key metrics
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Health:*\n{overall_health:.2f}%",
                    },
                    {"type": "mrkdwn", "text": f"*Active DAGs:*\n{active_dags}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Critical Issues:*\n{len(critical_issues)}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Pipeline Failures:*\n{len(failures)}",
                    },
                ],
            }
        )

        blocks.append({"type": "divider"})

        # 3. CRITICAL PERFORMANCE ANOMALIES
        if critical_issues:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🔴 CRITICAL PERFORMANCE ANOMALIES*",
                    },
                }
            )

            for idx, issue in enumerate(critical_issues[:3], 1):  # Show top 3
                dag_id = issue.get("dag_id", "Unknown")
                duration = issue.get("duration_seconds", 0)
                baseline = issue.get("baseline_p90", 0)
                deviation = issue.get("deviation_factor", 0)
                root_cause = issue.get("root_cause", "Unknown")
                impact = issue.get("impact", "Unknown")

                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*{idx}. {dag_id}*\n"
                                f"• Duration: `{duration:.1f}s` (vs `{baseline:.1f}s` baseline P90)\n"
                                f"• Deviation: `{deviation:.2f}x` slower than normal ⚠️\n"
                                f"• Root Cause: {root_cause}\n"
                                f"• Impact: {impact}"
                            ),
                        },
                    }
                )

            blocks.append({"type": "divider"})

        # 4. PIPELINE FAILURES
        if failures:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔥 PIPELINE FAILURES ({len(failures)} in last 4hrs)*",
                    },
                }
            )

            # Group failures by pattern
            failure_summary = SlackReportFormatter._summarize_failures(failures)

            for category, count in failure_summary.items():
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• `{category}` - *{count} failures*",
                        },
                    }
                )

            # Show most critical individual failure
            if failures:
                critical_failure = max(
                    failures, key=lambda x: x.get("duration_hours", 0)
                )
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"\n*Most Critical:*\n"
                                f"• `{critical_failure.get('dag_id', 'Unknown')}` "
                                f"- Failed after {critical_failure.get('duration_hours', 0):.1f} hours"
                            ),
                        },
                    }
                )

            blocks.append({"type": "divider"})

        # 5. CONSISTENTLY FAILING DAGS
        if consistently_failing_dags and len(consistently_failing_dags) > 0:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔁 CONSISTENTLY FAILING DAGS ({len(consistently_failing_dags)} DAGs)*",
                    },
                }
            )

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "The following DAGs have failed multiple times in recent runs:",
                    },
                }
            )

            # Show each consistently failing DAG
            for idx, dag_info in enumerate(
                consistently_failing_dags[:10], 1
            ):  # Show top 10
                dag_id = dag_info.get("dag_id", "Unknown")
                failure_count = dag_info.get("failure_count", 0)
                last_success = dag_info.get("last_success_date", "Never")
                consecutive_failures = dag_info.get(
                    "consecutive_failures", failure_count
                )

                # Format last success date
                if last_success and last_success != "Never":
                    try:
                        last_success_dt = datetime.fromisoformat(
                            last_success.replace("Z", "+00:00")
                        )
                        last_success = last_success_dt.strftime("%Y-%m-%d %H:%M UTC")
                    except Exception:
                        pass

                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*{idx}. `{dag_id}`*\n"
                                f"• Consecutive Failures: `{consecutive_failures}`\n"
                                f"• Total Failures: `{failure_count}` in last 24hrs\n"
                                f"• Last Success: `{last_success}`"
                            ),
                        },
                    }
                )

            blocks.append({"type": "divider"})

        # 6. IMMEDIATE ACTIONS REQUIRED
        if recommendations:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🎯 IMMEDIATE ACTIONS REQUIRED*",
                    },
                }
            )

            for rec in recommendations:
                priority = rec.get("priority", "MEDIUM")
                action = rec.get("action", "")
                priority_emoji = (
                    "🔴"
                    if priority == "URGENT"
                    else "🟡" if priority == "HIGH" else "🟢"
                )

                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{priority_emoji} *{priority}:* {action}",
                        },
                    }
                )

        blocks.append({"type": "divider"})

        # 7. FOOTER with timestamp and attribution
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"🤖 *Airflow Intelligence Agent* | "
                            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
                        ),
                    }
                ],
            }
        )

        return blocks

    @staticmethod
    def _summarize_failures(failures: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group failures by pattern/category."""
        summary = {}
        for failure in failures:
            dag_id = failure.get("dag_id", "Unknown")
            # Extract category (prefix before first dot or hyphen)
            category = dag_id.split(".")[0] if "." in dag_id else dag_id.split("-")[0]
            summary[category] = summary.get(category, 0) + 1
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def _generate_pattern_analysis(anomalies: List[Dict[str, Any]]) -> str:
        """Generate pattern analysis text."""
        if not anomalies:
            return "No significant patterns detected."

        # Analyze common patterns
        patterns = []

        # Check for similar DAG patterns
        dag_prefixes = [a.get("dag_id", "").split(".")[0] for a in anomalies]
        common_prefix = (
            max(set(dag_prefixes), key=dag_prefixes.count) if dag_prefixes else None
        )

        if common_prefix:
            count = dag_prefixes.count(common_prefix)
            patterns.append(
                f"• `{common_prefix}` pipelines showing systematic issues ({count} affected)"
            )

        # Check for resource patterns
        resource_issues = [
            a for a in anomalies if "resource" in str(a.get("root_cause", "")).lower()
        ]
        if resource_issues:
            patterns.append(
                f"• Resource contention detected in {len(resource_issues)} pipelines"
            )

        return (
            "\n".join(patterns)
            if patterns
            else "• Multiple independent issues detected"
        )

    @staticmethod
    def create_simple_alert_blocks(
        severity: str, title: str, message: str, fields: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create a simple formatted alert.

        Args:
            severity: Alert severity (info/warning/critical)
            title: Alert title
            message: Message body
            fields: Optional key-value fields to display

        Returns:
            List of Slack blocks
        """
        blocks = []

        # Header with severity emoji
        emoji_map = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}
        emoji = emoji_map.get(severity, "📢")

        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {title}",
                    "emoji": True,
                },
            }
        )

        # Message body
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": message}})

        # Optional fields
        if fields:
            field_blocks = []
            for key, value in fields.items():
                field_blocks.append({"type": "mrkdwn", "text": f"*{key}:*\n{value}"})

            blocks.append({"type": "section", "fields": field_blocks})

        blocks.append({"type": "divider"})

        # Footer
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🤖 *Airflow Intelligence Agent* | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                    }
                ],
            }
        )

        return blocks

    @staticmethod
    def get_attachment_color(severity: str) -> str:
        """Get color code for attachment based on severity."""
        color_map = {
            "info": "#36a64f",  # Green
            "warning": "#ff9900",  # Orange
            "critical": "#ff0000",  # Red
        }
        return color_map.get(severity, "#808080")


# Example usage for testing
if __name__ == "__main__":
    """Demonstrate the formatter with sample data."""

    formatter = SlackReportFormatter()

    # Sample data
    critical_issues = [
        {
            "dag_id": "pricing-service-curated.pipeline-product.product.curated",
            "duration_seconds": 275.2,
            "baseline_p90": 82.2,
            "deviation_factor": 3.35,
            "root_cause": "Spark job execution time increased from ~30s to 212s",
            "impact": "Critical pricing data delays",
        },
        {
            "dag_id": "regional-pricing-curated.pipeline-product-price.product_price.curated",
            "duration_seconds": 243.7,
            "baseline_p90": 82.0,
            "deviation_factor": 2.97,
            "root_cause": "Spark job execution time increased from ~30s to 182s",
            "impact": "Regional pricing updates delayed",
        },
    ]

    failures = [
        {
            "dag_id": "ops-dap-bi-enriched.pipeline-production_assets.dashboard",
            "duration_hours": 1.2,
        },
        {
            "dag_id": "ops-dap-bi-enriched.pipeline-production_errors.errors",
            "duration_hours": 0.8,
        },
        {
            "dag_id": "loyalty-enriched.pipeline-crm-comms-savings.savings",
            "duration_hours": 1.5,
        },
    ]

    recommendations = [
        {
            "priority": "URGENT",
            "action": "Investigate EMR EKS cluster resource allocation for pricing pipelines",
        },
        {
            "priority": "HIGH",
            "action": "Check ops-dap-bi-enriched infrastructure dependencies",
        },
        {
            "priority": "MEDIUM",
            "action": "Review loyalty pipeline data sources and connections",
        },
    ]

    consistently_failing_dags = [
        {
            "dag_id": "loyalty-enriched.pipeline-crm-comms-savings",
            "failure_count": 6,
            "consecutive_failures": 4,
            "last_success_date": "2026-03-04T10:30:00Z",
        },
        {
            "dag_id": "ops-dap-bi-enriched.pipeline-production_assets",
            "failure_count": 5,
            "consecutive_failures": 3,
            "last_success_date": "2026-03-03T15:20:00Z",
        },
        {
            "dag_id": "global-errors-enriched.pipeline-main-cc-errors",
            "failure_count": 3,
            "consecutive_failures": 3,
            "last_success_date": "Never",
        },
    ]

    # Generate blocks
    blocks = formatter.create_health_report_blocks(
        overall_health=97.37,
        active_dags=587,
        critical_issues=critical_issues,
        failures=failures,
        anomalies=critical_issues,
        recommendations=recommendations,
        consistently_failing_dags=consistently_failing_dags,
        confidence_level="High",
    )

    print("✨ Beautifully Formatted Slack Report Blocks Generated!")
    print(f"📦 Total blocks: {len(blocks)}")
    print("\n💡 Use these blocks with Slack's chat.postMessage API")
    print("\nExample:")
    print("client.chat_postMessage(channel='#airflow-monitoring', blocks=blocks)")
