#!/usr/bin/env python3
"""
Quick Slack Connection Test

This script tests if your Slack bot token is working and can send messages.
"""

import os
import sys

def test_slack_connection():
    """Test Slack bot connection."""

    print("🔍 Slack Connection Test\n")
    print("=" * 60)

    # Check for Slack token
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#airflow-monitoring")

    if not slack_token:
        print("\n❌ SLACK_BOT_TOKEN not found!")
        print("\n💡 You need to set your Slack bot token:")
        print("   Option 1: Create .env file:")
        print("   ```")
        print("   cp .env.template .env")
        print("   # Edit .env and add your token")
        print("   ```")
        print("\n   Option 2: Export environment variable:")
        print("   ```")
        print("   export SLACK_BOT_TOKEN='xoxb-your-token-here'")
        print("   export SLACK_CHANNEL='#your-channel'")
        print("   ```")
        print("\n📚 How to get a Slack Bot Token:")
        print("   1. Go to https://api.slack.com/apps")
        print("   2. Create a new app or select existing")
        print("   3. Go to 'OAuth & Permissions'")
        print("   4. Add these scopes: chat:write, chat:write.customize")
        print("   5. Install app to workspace")
        print("   6. Copy 'Bot User OAuth Token'")
        return False

    print(f"✅ SLACK_BOT_TOKEN found: {slack_token[:10]}...")
    print(f"📢 Target channel: {slack_channel}")

    # Try to import Slack SDK
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
    except ImportError:
        print("\n❌ slack_sdk not installed!")
        print("\n💡 Install it with:")
        print("   pip install slack-sdk")
        return False

    print("✅ slack_sdk imported successfully")

    # Test connection
    print("\n🔌 Testing connection...")

    try:
        client = WebClient(token=slack_token)

        # Test auth
        print("   Testing authentication...")
        response = client.auth_test()
        print(f"   ✅ Authenticated as: {response['user']}")
        print(f"   ✅ Team: {response['team']}")

        # Send test message
        print(f"\n📤 Sending test message to {slack_channel}...")

        test_message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ Slack Connection Test Successful!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Your Airflow Intelligence Agent can now send beautiful reports to Slack! 🎉"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 *Test message from Airflow Intelligence Agent*"
                    }
                ]
            }
        ]

        result = client.chat_postMessage(
            channel=slack_channel,
            blocks=test_message_blocks,
            text="Slack Connection Test"
        )

        print(f"   ✅ Message sent successfully!")
        print(f"   ✅ Message timestamp: {result['ts']}")
        print(f"   ✅ Channel: {result['channel']}")

        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your Slack integration is working!")
        print("\nNext steps:")
        print("   1. Run a health report:")
        print("      python -m agents.airflow_intelligence.cli report")
        print("\n   2. Or test with example:")
        print("      python agents/airflow_intelligence/example_beautiful_slack_report.py")

        return True

    except SlackApiError as e:
        error = e.response['error']
        print(f"\n❌ Slack API Error: {error}")

        if error == 'invalid_auth':
            print("\n💡 Your token is invalid or expired")
            print("   Get a new token from: https://api.slack.com/apps")

        elif error == 'channel_not_found':
            print(f"\n💡 Channel '{slack_channel}' not found")
            print("   Make sure:")
            print("   - Channel exists")
            print("   - Bot is invited to the channel")
            print("   - Channel name starts with #")

        elif error == 'not_in_channel':
            print(f"\n💡 Bot is not in channel '{slack_channel}'")
            print("   Invite the bot:")
            print(f"   1. Go to {slack_channel} in Slack")
            print("   2. Type: /invite @YourBotName")

        else:
            print(f"\n💡 Error details: {e.response}")

        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file\n")
    except ImportError:
        print("ℹ️  python-dotenv not installed (optional)")
        print("   Install with: pip install python-dotenv\n")
    except:
        print("ℹ️  No .env file found (using environment variables)\n")

    success = test_slack_connection()

    sys.exit(0 if success else 1)
