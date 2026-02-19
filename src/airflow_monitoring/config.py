"""Configuration management for Airflow monitoring system."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class MonitoringConfig:
    """Configuration for Airflow runtime monitoring."""
    
    # Database Configuration
    airflow_db_url: str
    
    # AWS Bedrock Configuration
    aws_region: str
    model_id: str
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Slack Configuration
    slack_bot_token: Optional[str] = None
    slack_channel: str = "#test-notification-ai"
    slack_username: str = "Airflow Monitor"
    enable_slack_notifications: bool = False
    
    # Monitoring Parameters
    window_hours: int = 24
    baseline_days: int = 14
    min_history: int = 10
    anomaly_multiplier: float = 1.5
    
    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Create configuration from environment variables."""
        return cls(
            # Database
            airflow_db_url=os.getenv("AIRFLOW_DB_URL", ""),
            
            # AWS
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            model_id=os.getenv("MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            
            # Slack
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
            slack_channel=os.getenv("SLACK_CHANNEL", "#test-notification-ai"),
            slack_username=os.getenv("SLACK_USERNAME", "Airflow Monitor"),
            enable_slack_notifications=os.getenv("ENABLE_SLACK_NOTIFICATIONS", "false").lower() == "true",
            
            # Monitoring
            window_hours=int(os.getenv("WINDOW_HOURS", "24")),
            baseline_days=int(os.getenv("BASELINE_DAYS", "14")),
            min_history=int(os.getenv("MIN_HISTORY", "10")),
            anomaly_multiplier=float(os.getenv("ANOMALY_MULTIPLIER", "1.5"))
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.airflow_db_url:
            errors.append("AIRFLOW_DB_URL is required")
            
        if not self.aws_region:
            errors.append("AWS_REGION is required")
            
        if not self.model_id:
            errors.append("MODEL_ID is required")
            
        if self.enable_slack_notifications and not self.slack_bot_token:
            errors.append("SLACK_BOT_TOKEN is required when Slack notifications are enabled")
            
        if self.window_hours <= 0:
            errors.append("WINDOW_HOURS must be positive")
            
        if self.baseline_days <= 0:
            errors.append("BASELINE_DAYS must be positive")
            
        return errors