"""Test configuration and fixtures for Airflow monitoring tests."""

import os
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Generator

# Set test environment variables
os.environ.update({
    "AIRFLOW_DB_URL": "postgresql://test:test@localhost:5433/airflow_test",
    "AWS_REGION": "us-east-1",
    "MODEL_ID": "test-model",
    "SLACK_BOT_TOKEN": "xoxb-test-token",
    "SLACK_CHANNEL": "#test-channel",
    "ENABLE_SLACK_NOTIFICATIONS": "false",
})


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_airflow_db():
    """Mock Airflow database connection."""
    mock = Mock()
    mock.execute.return_value.fetchall.return_value = []
    return mock


@pytest.fixture
def sample_dag_runs() -> list[Dict[str, Any]]:
    """Sample DAG run data for testing."""
    return [
        {
            "dag_id": "test_dag_1",
            "run_id": "scheduled__2026-02-10T10:00:00+00:00",
            "state": "success",
            "start_date": "2026-02-10T10:00:00+00:00",
            "end_date": "2026-02-10T10:30:00+00:00",
        },
        {
            "dag_id": "test_dag_2", 
            "run_id": "scheduled__2026-02-10T10:00:00+00:00",
            "state": "running",
            "start_date": "2026-02-10T10:00:00+00:00",
            "end_date": None,
        },
    ]


@pytest.fixture
def sample_baseline_data() -> list[Dict[str, Any]]:
    """Sample baseline data for testing."""
    return [
        {
            "dag_id": "test_dag_1",
            "start_date": "2026-02-09T10:00:00+00:00",
            "end_date": "2026-02-09T10:15:00+00:00",
        },
        {
            "dag_id": "test_dag_1",
            "start_date": "2026-02-08T10:00:00+00:00", 
            "end_date": "2026-02-08T10:20:00+00:00",
        },
    ]


@pytest.fixture
def mock_slack_client():
    """Mock Slack client."""
    mock = AsyncMock()
    mock.auth_test.return_value = {
        "user_id": "U123456789",
        "user": "test_bot",
        "team": "Test Team",
        "team_id": "T123456789",
    }
    mock.chat_postMessage.return_value = {
        "ok": True,
        "ts": "1234567890.123456",
        "channel": "C123456789",
    }
    return mock


@pytest.fixture
def mock_bedrock_client():
    """Mock AWS Bedrock client."""
    mock = Mock()
    mock.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": "Test AI response"}]
            }
        }
    }
    return mock


@pytest.fixture
def mock_fastmcp_transport():
    """Mock FastMCP transport."""
    mock = Mock()
    return mock


@pytest.fixture
def mock_fastmcp_client():
    """Mock FastMCP client."""
    mock = AsyncMock()
    
    # Mock call_tool responses
    mock.call_tool.return_value = Mock(
        structured_content={
            "success": True,
            "result": [],
        },
        data={
            "success": True,
            "result": [],
        },
    )
    
    return mock