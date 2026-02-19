"""Unit tests for configuration management."""

import os
import pytest
from airflow_monitoring.config import MonitoringConfig


class TestMonitoringConfig:
    """Test cases for MonitoringConfig."""

    def test_from_env_with_all_variables(self, monkeypatch):
        """Test configuration creation from environment variables."""
        # Set all environment variables
        env_vars = {
            "AIRFLOW_DB_URL": "postgresql://user:pass@localhost/db",
            "AWS_REGION": "eu-west-1",
            "MODEL_ID": "test-model-id",
            "AWS_ACCESS_KEY_ID": "AKIATEST",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "SLACK_BOT_TOKEN": "xoxb-test",
            "SLACK_CHANNEL": "#test",
            "SLACK_USERNAME": "Test Bot",
            "ENABLE_SLACK_NOTIFICATIONS": "true",
            "WINDOW_HOURS": "48",
            "BASELINE_DAYS": "30",
            "MIN_HISTORY": "20",
            "ANOMALY_MULTIPLIER": "2.0",
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        config = MonitoringConfig.from_env()
        
        assert config.airflow_db_url == "postgresql://user:pass@localhost/db"
        assert config.aws_region == "eu-west-1"
        assert config.model_id == "test-model-id"
        assert config.aws_access_key_id == "AKIATEST"
        assert config.aws_secret_access_key == "secret"
        assert config.slack_bot_token == "xoxb-test"
        assert config.slack_channel == "#test"
        assert config.slack_username == "Test Bot"
        assert config.enable_slack_notifications is True
        assert config.window_hours == 48
        assert config.baseline_days == 30
        assert config.min_history == 20
        assert config.anomaly_multiplier == 2.0

    def test_from_env_with_defaults(self, monkeypatch):
        """Test configuration with default values."""
        # Only set required variables
        monkeypatch.setenv("AIRFLOW_DB_URL", "postgresql://test/db")
        
        # Clear optional variables
        for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "SLACK_BOT_TOKEN"]:
            monkeypatch.delenv(var, raising=False)
        
        config = MonitoringConfig.from_env()
        
        assert config.airflow_db_url == "postgresql://test/db"
        assert config.aws_region == "us-east-1"  # default
        assert config.slack_channel == "#test-channel"  # default
        assert config.enable_slack_notifications is False  # default
        assert config.window_hours == 24  # default

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = MonitoringConfig(
            airflow_db_url="postgresql://test/db",
            aws_region="us-east-1",
            model_id="test-model",
            enable_slack_notifications=False,
        )
        
        errors = config.validate()
        assert errors == []

    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        config = MonitoringConfig(
            airflow_db_url="",  # Missing
            aws_region="",      # Missing
            model_id="",        # Missing
            enable_slack_notifications=True,
            slack_bot_token=None,  # Required when slack enabled
        )
        
        errors = config.validate()
        
        assert "AIRFLOW_DB_URL is required" in errors
        assert "AWS_REGION is required" in errors
        assert "MODEL_ID is required" in errors
        assert "SLACK_BOT_TOKEN is required when Slack notifications are enabled" in errors

    def test_validate_invalid_numeric_values(self):
        """Test validation with invalid numeric values."""
        config = MonitoringConfig(
            airflow_db_url="postgresql://test/db",
            aws_region="us-east-1",
            model_id="test-model",
            window_hours=-1,    # Invalid
            baseline_days=0,    # Invalid
        )
        
        errors = config.validate()
        
        assert "WINDOW_HOURS must be positive" in errors
        assert "BASELINE_DAYS must be positive" in errors