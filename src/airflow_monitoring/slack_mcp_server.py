#!/usr/bin/env python3

import os
import asyncio
import logging
from typing import Any, Dict, List
from datetime import datetime

from fastmcp import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Slack client
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not SLACK_BOT_TOKEN:  # pragma: no cover
    raise ValueError("SLACK_BOT_TOKEN environment variable is required")

slack_client = WebClient(token=SLACK_BOT_TOKEN)  # pragma: no cover

# Create FastMCP server
mcp = FastMCP("Slack Notification MCP Server")

@mcp.tool()
def send_message(channel: str, message: str, username: str = "Airflow Monitor") -> Dict[str, Any]:
    """
    Send a message to a Slack channel.
    
    Args:
        channel: Slack channel ID or name (e.g., "#alerts", "C1234567890")
        message: The message text to send
        username: Bot username to display (default: "Airflow Monitor")
    
    Returns:
        Dict containing success status and response details
    """
    return _send_message(channel, message, username)

def _send_message(channel: str, message: str, username: str = "Airflow Monitor") -> Dict[str, Any]:
    """Internal implementation of send_message for testing."""
    try:
        # Ensure channel starts with # if it's a channel name
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"
        
        logger.info(f"Sending message to channel: {channel}")
        
        response = slack_client.chat_postMessage(
            channel=channel,
            text=message,
            username=username,
            icon_emoji=":robot_face:"
        )
        
        logger.info(f"Message sent successfully. Timestamp: {response['ts']}")
        
        return {
            "success": True,
            "timestamp": response['ts'],
            "channel": response['channel'],
            "message": "Message sent successfully"
        }
        
    except SlackApiError as e:
        error_msg = f"Slack API error: {e.response['error']}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "error_code": e.response['error']
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

@mcp.tool()
def send_rich_message(
    channel: str, 
    title: str, 
    message: str, 
    color: str = "good", 
    username: str = "Airflow Monitor"
) -> Dict[str, Any]:
    """
    Send a rich formatted message with attachments to Slack.
    
    Args:
        channel: Slack channel ID or name
        title: Message title
        message: Main message content
        color: Message color bar ("good", "warning", "danger", or hex code)
        username: Bot username to display
    
    Returns:
        Dict containing success status and response details
    """
    return _send_rich_message(channel, title, message, color, username)

def _send_rich_message(
    channel: str, 
    title: str, 
    message: str, 
    color: str = "good", 
    username: str = "Airflow Monitor"
) -> Dict[str, Any]:
    """Internal implementation of send_rich_message for testing."""
    try:
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"
        
        logger.info(f"Sending rich message to channel: {channel}")
        
        # Create attachment with rich formatting
        attachments = [{
            "color": color,
            "title": title,
            "text": message,
            "footer": "Airflow Runtime Monitor",
            "footer_icon": ":airflow:",
            "ts": int(datetime.now().timestamp())
        }]
        
        response = slack_client.chat_postMessage(
            channel=channel,
            attachments=attachments,
            username=username,
            icon_emoji=":chart_with_upwards_trend:"
        )
        
        logger.info(f"Rich message sent successfully. Timestamp: {response['ts']}")
        
        return {
            "success": True,
            "timestamp": response['ts'],
            "channel": response['channel'],
            "message": "Rich message sent successfully"
        }
        
    except SlackApiError as e:
        error_msg = f"Slack API error: {e.response['error']}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "error_code": e.response['error']
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """
    Test the Slack connection and bot permissions.
    
    Returns:
        Dict containing connection status and bot info
    """
    return _test_connection()

def _test_connection() -> Dict[str, Any]:
    """Internal implementation of test_connection for testing."""
    try:
        logger.info("Testing Slack connection...")
        
        # Test auth and get bot info
        auth_response = slack_client.auth_test()
        
        logger.info("Slack connection successful")
        
        return {
            "success": True,
            "bot_user_id": auth_response["user_id"],
            "bot_user": auth_response["user"],
            "team": auth_response["team"],
            "team_id": auth_response["team_id"],
            "message": "Slack connection successful"
        }
        
    except SlackApiError as e:
        error_msg = f"Slack API error: {e.response['error']}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "error_code": e.response['error']
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def main():  # pragma: no cover
    """Main entry point for the Slack MCP server"""
    logger.info("Starting Slack MCP Server...")  # pragma: no cover
    mcp.run()  # pragma: no cover

if __name__ == "__main__":
    main()