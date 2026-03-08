"""Slack Tools - Slack SDK integration"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..utils import SlackReportFormatter

logger = logging.getLogger(__name__)


class SlackTools:
    """
    Direct Slack SDK integration for sending alerts and notifications.

    Provides the agent with ability to:
    - Send formatted alerts to Slack
    - Use different severity levels (info/warning/critical)
    - Rich formatting with markdown
    """

    def __init__(self, slack_token: str, default_channel: str = "#airflow-monitoring"):
        """
        Initialize Slack client.

        Args:
            slack_token: Slack bot token
            default_channel: Default channel for notifications
        """
        self.client = WebClient(token=slack_token)
        self.default_channel = default_channel
        self.formatter = SlackReportFormatter()
        logger.info(f"Slack client initialized (default channel: {default_channel})")

    def send_slack_alert(
        self, severity: str, title: str, message: str, channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send formatted alert to Slack.

        Args:
            severity: Alert severity (info/warning/critical)
            title: Alert title
            message: Message body (supports markdown)
            channel: Target channel (uses default if not provided)

        Returns:
            Result dictionary with success status
        """
        try:
            target_channel = channel or self.default_channel

            # Map severity to color
            color_map = {
                "info": "#36a64f",  # Green
                "warning": "#ff9900",  # Orange
                "critical": "#ff0000",  # Red
            }
            color = color_map.get(severity, "#808080")

            # Build Slack blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": title, "emoji": True},
                },
                {"type": "section", "text": {"type": "mrkdwn", "text": message}},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🤖 *Airflow Intelligence Agent* | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
                        }
                    ],
                },
            ]

            # Send message
            response = self.client.chat_postMessage(
                channel=target_channel,
                blocks=blocks,
                text=title,  # Fallback text for notifications
                attachments=[{"color": color, "fallback": title}],
            )

            logger.info(f"Slack alert sent to {target_channel}: {title}")

            return {
                "success": True,
                "channel": target_channel,
                "timestamp": response["ts"],
                "message": f"Alert sent successfully to {target_channel}",
            }

        except SlackApiError as e:
            error_msg = f"Slack API error: {e.response['error']}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error sending Slack alert: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def send_health_report(
        self,
        overall_health: float,
        active_dags: int,
        critical_issues: List[Dict[str, Any]],
        failures: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        recommendations: List[Dict[str, str]],
        consistently_failing_dags: Optional[List[Dict[str, Any]]] = None,
        confidence_level: str = "High",
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a beautifully formatted health report to Slack.

        Args:
            overall_health: Health percentage (0-100)
            active_dags: Number of active DAGs
            critical_issues: List of critical performance issues
            failures: List of pipeline failures
            anomalies: List of detected anomalies
            recommendations: List of action recommendations with priority
            consistently_failing_dags: List of DAGs failing consistently
            confidence_level: Analysis confidence (High/Medium/Low)
            channel: Target channel (uses default if not provided)

        Returns:
            Result dictionary with success status
        """
        try:
            target_channel = channel or self.default_channel

            # Generate beautifully formatted blocks
            blocks = self.formatter.create_health_report_blocks(
                overall_health=overall_health,
                active_dags=active_dags,
                critical_issues=critical_issues,
                failures=failures,
                anomalies=anomalies,
                recommendations=recommendations,
                consistently_failing_dags=consistently_failing_dags,
                confidence_level=confidence_level,
            )

            # Determine severity for attachment color
            if overall_health >= 95 and len(critical_issues) == 0:
                severity = "info"
            elif overall_health >= 85 or len(critical_issues) <= 2:
                severity = "warning"
            else:
                severity = "critical"

            # Send message
            response = self.client.chat_postMessage(
                channel=target_channel,
                blocks=blocks,
                text=f"Airflow Pipeline Health Report - {overall_health:.1f}% Health",
                attachments=[
                    {
                        "color": self.formatter.get_attachment_color(severity),
                        "fallback": f"Health Report - {overall_health:.1f}%",
                    }
                ],
            )

            logger.info(
                f"Health report sent to {target_channel}: {overall_health:.1f}% health"
            )

            return {
                "success": True,
                "channel": target_channel,
                "timestamp": response["ts"],
                "message": f"Health report sent successfully to {target_channel}",
            }

        except SlackApiError as e:
            error_msg = f"Slack API error: {e.response['error']}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error sending health report: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def send_formatted_alert(
        self,
        severity: str,
        title: str,
        message: str,
        fields: Optional[Dict[str, str]] = None,
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a formatted alert with enhanced visual structure.

        Args:
            severity: Alert severity (info/warning/critical)
            title: Alert title
            message: Message body
            fields: Optional key-value fields to display
            channel: Target channel (uses default if not provided)

        Returns:
            Result dictionary with success status
        """
        try:
            target_channel = channel or self.default_channel

            # Generate formatted blocks
            blocks = self.formatter.create_simple_alert_blocks(
                severity=severity, title=title, message=message, fields=fields
            )

            # Send message
            response = self.client.chat_postMessage(
                channel=target_channel,
                blocks=blocks,
                text=title,
                attachments=[
                    {
                        "color": self.formatter.get_attachment_color(severity),
                        "fallback": title,
                    }
                ],
            )

            logger.info(f"Formatted alert sent to {target_channel}: {title}")

            return {
                "success": True,
                "channel": target_channel,
                "timestamp": response["ts"],
                "message": f"Alert sent successfully to {target_channel}",
            }

        except SlackApiError as e:
            error_msg = f"Slack API error: {e.response['error']}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error sending formatted alert: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
