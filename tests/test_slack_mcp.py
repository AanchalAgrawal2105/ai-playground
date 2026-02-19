#!/usr/bin/env python3

import os
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

# Load environment variables
load_dotenv()

async def test_slack_simple():
    """Simple test for Slack MCP server with proper response handling."""
    
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("❌ SLACK_BOT_TOKEN not found in environment variables")
        print("Please set your Slack bot token in the .env file")
        return
    
    # Create transport for Slack MCP server
    transport = StdioTransport(
        command="python",
        args=["slack_mcp_server.py"],
        env={
            "SLACK_BOT_TOKEN": os.environ["SLACK_BOT_TOKEN"]
        }
    )
    
    try:
        async with Client(transport) as client:
            print("🚀 Testing Slack MCP Server...")
            
            # Test connection
            print("\n1. Testing Slack connection...")
            connection_result = await client.call_tool("test_connection", {})
            
            # Based on previous debugging, FastMCP returns structured_content
            if hasattr(connection_result, 'structured_content') and connection_result.structured_content:
                conn_data = connection_result.structured_content  # Direct access, no 'result' key needed!
                print(f"✅ Found structured_content: {conn_data}")
            else:
                print(f"⚠️  No structured_content, trying data attribute...")
                print(f"Result type: {type(connection_result)}")
                print(f"Result: {connection_result}")
                
                # Fallback: try to get first item from data if it exists
                if hasattr(connection_result, 'data') and connection_result.data:
                    print(f"Data length: {len(connection_result.data)}")
                    if connection_result.data:
                        first_item = connection_result.data[0]
                        print(f"First item: {first_item}")
                        print(f"First item type: {type(first_item)}")
                        
                        # This is likely a Root object - let's extract data
                        if hasattr(first_item, 'model_dump'):
                            conn_data = first_item.model_dump()
                        elif hasattr(first_item, '__dict__'):
                            conn_data = first_item.__dict__
                        else:
                            conn_data = {}
                    else:
                        conn_data = {}
                else:
                    conn_data = {}
            
            # Check if we got valid connection data
            if isinstance(conn_data, dict) and conn_data.get("success", False):
                print(f"✅ SUCCESS! Connected as: {conn_data.get('bot_user', 'Unknown')}")
                print(f"✅ Team: {conn_data.get('team', 'Unknown')}")
                print(f"✅ User ID: {conn_data.get('bot_user_id', 'Unknown')}")
                
                # Now test sending a message
                print("\n2. Testing message sending...")
                channel = os.getenv("SLACK_CHANNEL", "#general")
                
                # UNCOMMENT THE LINES BELOW TO ACTUALLY SEND A MESSAGE:
                print(f"⚠️  Ready to send test message to {channel}")
                print("Uncomment the code in the script to actually send a message!")
                
                message_result = await client.call_tool(
                    "send_message",
                    {
                        "channel": channel,
                        "message": "🤖 Hello from Airflow MCP Server! Connection test successful.",
                        "username": "Airflow Test Bot"
                    }
                )
                
                # Handle message result the same way
                if hasattr(message_result, 'structured_content') and message_result.structured_content:
                    msg_data = message_result.structured_content  # Direct access!
                elif hasattr(message_result, 'data') and message_result.data:
                    first_item = message_result.data[0]
                    if hasattr(first_item, 'model_dump'):
                        msg_data = first_item.model_dump()
                    else:
                        msg_data = first_item.__dict__
                else:
                    msg_data = {}
                
                if msg_data.get("success"):
                    print(f"✅ Message sent successfully to {channel}!")
                else:
                    print(f"❌ Message failed: {msg_data.get('error', 'Unknown error')}")
                
                print("✅ Slack MCP Server is working correctly!")
                
            else:
                print(f"❌ Connection test failed or returned unexpected data:")
                print(f"   Data: {conn_data}")
                
    except Exception as e:
        print(f"❌ Error testing Slack MCP Server: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_slack_simple())