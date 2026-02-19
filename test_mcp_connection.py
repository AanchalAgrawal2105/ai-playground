#!/usr/bin/env python3
"""
Simple test script to verify MCP server connections work without real database.
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set minimal environment variables for testing
os.environ["AIRFLOW_DB_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["AWS_REGION"] = "us-west-2"
os.environ["MODEL_ID"] = "test-model"
os.environ["AWS_ACCESS_KEY_ID"] = "test-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret"
os.environ["ENABLE_SLACK_NOTIFICATIONS"] = "false"

# Disable Slack for this test
if "SLACK_BOT_TOKEN" in os.environ:
    del os.environ["SLACK_BOT_TOKEN"]

async def test_airflow_mcp_import():
    """Test that we can import and create the airflow transport."""
    try:
        from fastmcp.client.transports import StdioTransport
        
        # Test the transport configuration
        airflow_transport = StdioTransport(
            command="python",
            args=["-m", "airflow_monitoring.airflow_mcp_server"],
            env={
                "AIRFLOW_DB_URL": os.environ["AIRFLOW_DB_URL"],
            }
        )
        
        print("✅ Airflow MCP transport created successfully")
        print(f"   Command: {airflow_transport.command}")
        print(f"   Args: {airflow_transport.args}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_module_imports():
    """Test that all modules can be imported."""
    try:
        # Test individual module imports
        from airflow_monitoring.airflow_mcp_server import main as airflow_main
        print("✅ airflow_mcp_server imported successfully")
        
        from airflow_monitoring.slack_mcp_server import main as slack_main
        print("✅ slack_mcp_server imported successfully")
        
        from airflow_monitoring.airflow_runtime_agent import main as agent_main
        print("✅ airflow_runtime_agent imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    print("🧪 Testing MCP module imports and transport configuration...")
    print("=" * 60)
    
    # Test module imports
    import_success = await test_module_imports()
    
    if import_success:
        # Test transport creation
        transport_success = await test_airflow_mcp_import()
    else:
        transport_success = False
    
    print("=" * 60)
    if import_success and transport_success:
        print("✅ All tests passed! MCP configuration should work.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))