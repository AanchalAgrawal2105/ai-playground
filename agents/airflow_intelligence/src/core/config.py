"""Configuration for Airflow Intelligence Agent."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """
    Configuration for the Airflow Intelligence Agent.

    All values are loaded from environment variables (.env file).
    No defaults are hardcoded - everything must be configured in .env.

    This configuration manages all settings for the agent including:
    - Database connections
    - AWS Bedrock settings
    - Slack integration
    - Agent behavior parameters
    - Monitoring thresholds
    """

    # Database
    airflow_db_url: str

    # LLM Provider Configuration
    llm_provider: str  # "bedrock", "anthropic", or "openai"
    model_id: str

    # AWS Bedrock (only if llm_provider = "bedrock")
    aws_region: Optional[str]
    aws_access_key: Optional[str]
    aws_secret_key: Optional[str]

    # API Keys (for anthropic/openai providers)
    anthropic_api_key: Optional[str]
    openai_api_key: Optional[str]

    # Slack
    slack_token: Optional[str]
    slack_channel: str
    slack_username: str
    enable_slack: bool

    # Agent behavior
    temperature: float
    max_tokens: int
    max_iterations: int

    # Monitoring configuration
    window_hours: int
    baseline_days: int
    min_history: int
    anomaly_multiplier: float
    stale_dag_threshold_days: int

    # Performance
    query_timeout: int
    max_results: int

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Load configuration from environment variables (.env file).

        ALL variables are REQUIRED - no defaults provided.
        Configure everything in your .env file before running.

        Required Environment Variables:
            # Database
            AIRFLOW_DB_URL: PostgreSQL connection string

            # LLM Provider
            LLM_PROVIDER: Provider type ("bedrock", "anthropic", or "openai")
            MODEL_ID: Model identifier (provider-specific)

            # AWS Bedrock (only if LLM_PROVIDER=bedrock)
            AWS_REGION: AWS region (e.g., us-east-1, eu-west-1)
            AWS_ACCESS_KEY_ID: AWS access key (optional if using IAM role)
            AWS_SECRET_ACCESS_KEY: AWS secret key (optional if using IAM role)

            # Anthropic API (only if LLM_PROVIDER=anthropic)
            ANTHROPIC_API_KEY: Anthropic API key

            # OpenAI API (only if LLM_PROVIDER=openai)
            OPENAI_API_KEY: OpenAI API key

            # Slack
            SLACK_BOT_TOKEN: Slack bot token (optional if not using Slack)
            SLACK_CHANNEL: Target Slack channel
            SLACK_USERNAME: Bot username for Slack messages
            ENABLE_SLACK_NOTIFICATIONS: Enable Slack (true/false)

            # Agent Behavior
            AGENT_TEMPERATURE: Agent temperature (0.0-1.0)
            AGENT_MAX_TOKENS: Max tokens per response
            AGENT_MAX_ITERATIONS: Max agent reasoning loops

            # Monitoring Configuration
            WINDOW_HOURS: Hours to look back for failures
            BASELINE_DAYS: Days for baseline calculation
            MIN_HISTORY: Minimum history required for baseline
            ANOMALY_MULTIPLIER: Multiplier for anomaly detection
            STALE_DAG_THRESHOLD_DAYS: Days before DAG considered stale

            # Performance
            QUERY_TIMEOUT: Database query timeout in seconds
            MAX_RESULTS: Maximum results per query

        Raises:
            KeyError: If required environment variable is missing
            ValueError: If value cannot be converted to expected type
        """

        # Helper function to get required env var
        def get_required(key: str) -> str:
            value = os.getenv(key)
            if value is None:
                raise KeyError(
                    f"Required environment variable '{key}' not found. "
                    f"Please configure it in your .env file."
                )
            return value

        # Helper function to get optional env var
        def get_optional(key: str) -> Optional[str]:
            return os.getenv(key)

        # Helper to parse boolean
        def parse_bool(value: str) -> bool:
            return value.lower() in ("true", "1", "yes", "on")

        return cls(
            # Database - Required
            airflow_db_url=get_required("AIRFLOW_DB_URL"),
            # LLM Provider - Required
            llm_provider=get_required("LLM_PROVIDER"),
            model_id=get_required("MODEL_ID"),
            # AWS Bedrock - Optional (required if llm_provider=bedrock)
            aws_region=get_optional("AWS_REGION"),
            aws_access_key=get_optional("AWS_ACCESS_KEY_ID"),
            aws_secret_key=get_optional("AWS_SECRET_ACCESS_KEY"),
            # API Keys - Optional (required based on provider)
            anthropic_api_key=get_optional("ANTHROPIC_API_KEY"),
            openai_api_key=get_optional("OPENAI_API_KEY"),
            # Slack - Optional token, required config
            slack_token=get_optional("SLACK_BOT_TOKEN"),
            slack_channel=get_required("SLACK_CHANNEL"),
            slack_username=get_required("SLACK_USERNAME"),
            enable_slack=parse_bool(get_required("ENABLE_SLACK_NOTIFICATIONS")),
            # Agent Behavior - Required
            temperature=float(get_required("AGENT_TEMPERATURE")),
            max_tokens=int(get_required("AGENT_MAX_TOKENS")),
            max_iterations=int(get_required("AGENT_MAX_ITERATIONS")),
            # Monitoring Configuration - Required
            window_hours=int(get_required("WINDOW_HOURS")),
            baseline_days=int(get_required("BASELINE_DAYS")),
            min_history=int(get_required("MIN_HISTORY")),
            anomaly_multiplier=float(get_required("ANOMALY_MULTIPLIER")),
            stale_dag_threshold_days=int(get_required("STALE_DAG_THRESHOLD_DAYS")),
            # Performance - Required
            query_timeout=int(get_required("QUERY_TIMEOUT")),
            max_results=int(get_required("MAX_RESULTS")),
        )

    def validate(self) -> list[str]:
        """
        Validate configuration and return list of errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.airflow_db_url:
            errors.append("AIRFLOW_DB_URL is required")

        if not self.airflow_db_url.startswith("postgresql://"):
            errors.append("AIRFLOW_DB_URL must be a PostgreSQL connection string")

        if self.temperature < 0 or self.temperature > 1:
            errors.append("temperature must be between 0 and 1")

        if self.max_tokens < 100 or self.max_tokens > 8192:
            errors.append("max_tokens must be between 100 and 8192")

        if self.window_hours < 1:
            errors.append("window_hours must be >= 1")

        if self.baseline_days < 1:
            errors.append("baseline_days must be >= 1")

        if self.enable_slack and not self.slack_token:
            errors.append("SLACK_BOT_TOKEN required when Slack notifications enabled")

        # Provider-specific validation
        if not self.llm_provider:
            errors.append("LLM_PROVIDER is required (bedrock, anthropic, or openai)")
        elif self.llm_provider.lower() not in ["bedrock", "anthropic", "openai"]:
            errors.append(
                f"Invalid LLM_PROVIDER: {self.llm_provider}. "
                f"Must be: bedrock, anthropic, or openai"
            )
        else:
            provider = self.llm_provider.lower()

            if provider == "bedrock":
                if not self.aws_region:
                    errors.append("AWS_REGION required when using bedrock provider")
                # AWS credentials are optional - will fallback to IAM role
            elif provider == "anthropic":
                if not self.anthropic_api_key:
                    errors.append(
                        "ANTHROPIC_API_KEY required when using anthropic provider"
                    )
            elif provider == "openai":
                if not self.openai_api_key:
                    errors.append("OPENAI_API_KEY required when using openai provider")

        return errors

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "airflow_db_url": self.airflow_db_url,
            "llm_provider": self.llm_provider,
            "model_id": self.model_id,
            "aws_region": self.aws_region,
            "slack_channel": self.slack_channel,
            "enable_slack": self.enable_slack,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "window_hours": self.window_hours,
            "baseline_days": self.baseline_days,
        }

    def __repr__(self) -> str:
        """String representation (hides sensitive data)."""
        return (
            f"AgentConfig(\n"
            f"  llm_provider={self.llm_provider},\n"
            f"  model_id={self.model_id},\n"
            f"  aws_region={self.aws_region},\n"
            f"  slack_channel={self.slack_channel},\n"
            f"  temperature={self.temperature},\n"
            f"  window_hours={self.window_hours}h,\n"
            f"  baseline_days={self.baseline_days}d\n"
            f")"
        )
