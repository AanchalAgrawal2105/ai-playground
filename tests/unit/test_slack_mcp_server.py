"""Unit tests for Slack MCP server."""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from slack_sdk.errors import SlackApiError

from airflow_monitoring.slack_mcp_server import _send_message as send_message, _send_rich_message as send_rich_message, _test_connection as test_connection


class TestSlackMCPServer:
    """Test cases for Slack MCP server functions."""

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_message_success(self, mock_slack_client):
        """Test successful message sending."""
        # Mock successful response
        mock_slack_client.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456",
            "channel": "C1234567890",
        }
        
        result = send_message(
            channel="#test",
            message="Test message",
            username="Test Bot"
        )
        
        assert result["success"] is True
        assert result["timestamp"] == "1234567890.123456"
        assert result["channel"] == "C1234567890"
        
        # Verify the API call
        mock_slack_client.chat_postMessage.assert_called_once_with(
            channel="#test",
            text="Test message",
            username="Test Bot",
            icon_emoji=":robot_face:"
        )

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_message_channel_id(self, mock_slack_client):
        """Test sending message with channel ID."""
        mock_slack_client.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456",
            "channel": "C1234567890",
        }
        
        # Test with channel ID (should not be modified)
        send_message(channel="C1234567890", message="Test")
        
        mock_slack_client.chat_postMessage.assert_called_once()
        args, kwargs = mock_slack_client.chat_postMessage.call_args
        assert kwargs["channel"] == "C1234567890"

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_message_plain_channel_name(self, mock_slack_client):
        """Test sending message with plain channel name."""
        mock_slack_client.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456",
            "channel": "C1234567890",
        }
        
        # Test with plain channel name (should add #)
        send_message(channel="general", message="Test")
        
        mock_slack_client.chat_postMessage.assert_called_once()
        args, kwargs = mock_slack_client.chat_postMessage.call_args
        assert kwargs["channel"] == "#general"

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_message_slack_api_error(self, mock_slack_client):
        """Test handling of Slack API errors."""
        # Mock Slack API error
        error_response = {"error": "channel_not_found"}
        mock_slack_client.chat_postMessage.side_effect = SlackApiError(
            message="Channel not found",
            response={"error": "channel_not_found"}
        )
        
        result = send_message(channel="#nonexistent", message="Test")
        
        assert result["success"] is False
        assert "channel_not_found" in result["error"]
        assert result["error_code"] == "channel_not_found"

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_message_unexpected_error(self, mock_slack_client):
        """Test handling of unexpected errors."""
        # Mock unexpected error
        mock_slack_client.chat_postMessage.side_effect = Exception("Network error")
        
        result = send_message(channel="#test", message="Test")
        
        assert result["success"] is False
        assert "Network error" in result["error"]

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_send_rich_message_success(self, mock_slack_client):
        """Test successful rich message sending."""
        mock_slack_client.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456",
            "channel": "C1234567890",
        }
        
        result = send_rich_message(
            channel="#test",
            title="Test Title",
            message="Test message",
            color="good",
            username="Test Bot"
        )
        
        assert result["success"] is True
        mock_slack_client.chat_postMessage.assert_called_once()
        
        # Check attachments format
        args, kwargs = mock_slack_client.chat_postMessage.call_args
        assert "attachments" in kwargs
        attachment = kwargs["attachments"][0]
        assert attachment["title"] == "Test Title"
        assert attachment["text"] == "Test message"
        assert attachment["color"] == "good"

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_test_connection_success(self, mock_slack_client):
        """Test successful connection test."""
        mock_slack_client.auth_test.return_value = {
            "ok": True,
            "user_id": "U123456789",
            "user": "test_bot",
            "team": "Test Team",
            "team_id": "T123456789",
        }
        
        result = test_connection()
        
        assert result["success"] is True
        assert result["bot_user_id"] == "U123456789"
        assert result["bot_user"] == "test_bot"
        assert result["team"] == "Test Team"
        assert result["team_id"] == "T123456789"

    @patch("airflow_monitoring.slack_mcp_server.slack_client")
    def test_test_connection_failure(self, mock_slack_client):
        """Test connection test failure."""
        mock_slack_client.auth_test.side_effect = SlackApiError(
            message="Invalid token",
            response={"error": "invalid_auth"}
        )
        
        result = test_connection()
        
        assert result["success"] is False
        assert "invalid_auth" in result["error"]
        assert result["error_code"] == "invalid_auth"