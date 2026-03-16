# 🚀 Getting Started - Complete Guide

This guide will walk you through setting up and running the Airflow Intelligence Agent locally, step by step.

---

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Python 3.9 or higher** installed
  ```bash
  python3 --version  # Should show 3.9, 3.10, or 3.11
  ```

- [ ] **Access to Airflow PostgreSQL database**
  - Host, port, username, password, database name
  - Database should contain Airflow metadata

- [ ] **LLM Provider** - Choose ONE of the following:
  - **AWS Bedrock** (recommended for enterprise):
    - AWS Access Key ID & Secret Access Key
    - Region with Claude Sonnet enabled 
    - Bedrock model access enabled in AWS console
  - **Anthropic API** (easiest to get started):
    - Get API key from https://console.anthropic.com/
    - Direct access to latest Claude models
  - **OpenAI API**:
    - Get API key from https://platform.openai.com/api-keys
    - GPT-4 Turbo or GPT-4o recommended

- [ ] **Slack Bot Token** (Optional, but recommended)
  - Go to https://api.slack.com/apps
  - Create app or use existing
  - Get Bot User OAuth Token (starts with `xoxb-`)
  - Bot needs `chat:write` permission

- [ ] **Git** installed
  ```bash
  git --version
  ```

---

## 🎯 Quick Start (5 Minutes)

### Using Docker (Easiest - Recommended)

```bash
# 1. Clone repository
git clone https://github.com/AanchalAgrawal2105/ai-playground.git
cd ai-playground/agents/airflow_intelligence

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials (see Configuration section below)

# 3. Run with docker-compose
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop
docker-compose down
```

**That's it!** The agent is now monitoring your Airflow pipelines. 🎉

---

## 💻 Detailed Local Setup (Without Docker)

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/AanchalAgrawal2105/ai-playground.git

# Navigate to agent directory
cd ai-playground/agents/airflow_intelligence

# Verify you're in the right place
ls -la  # Should see: src/, tests/, deploy/, requirements.txt, etc.
```

### Step 2: Set Up Python Virtual Environment

**Option A: Using `uv` (Fastest - Recommended)**

```bash
# Install uv (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal or run:
source ~/.bashrc  # or ~/.zshrc on macOS

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies (super fast!)
uv pip install -r requirements.txt

# Verify installation
python -c "from src.core import AgentOrchestrator; print('✅ Installation successful')"
```

**Option B: Using Standard `pip`**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.core import AgentOrchestrator; print('✅ Installation successful')"
```

### Step 3: Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Open in your favorite editor
nano .env   # or: vim .env, code .env, etc.
```

**Edit these required fields:**

```bash
# ============ DATABASE (REQUIRED) ============
# Replace with your Airflow database details
AIRFLOW_DB_URL=postgresql://username:password@hostname:5432/airflow_db

# Example: If your database is:
# - Host: your-airflow-db.example.com
# - Port: 5432
# - Username: airflow_user
# - Password: MySecurePass123
# - Database: airflow_metadata
# Then:
AIRFLOW_DB_URL=postgresql://airflow_user:MySecurePass123@your-airflow-db.example.com:5432/airflow_metadata


# ============ LLM PROVIDER (REQUIRED) ============
# Choose ONE: "bedrock", "anthropic", or "openai"
LLM_PROVIDER=anthropic

# Model ID (provider-specific):
# - Bedrock: anthropic.claude-sonnet-4-20250514-v1:0
# - Anthropic: claude-sonnet-4-20250514
# - OpenAI: gpt-4-turbo or gpt-4o
MODEL_ID=claude-sonnet-4-20250514

# --- If using Bedrock ---
AWS_REGION=us-east-1

# Option 1: AWS SSO (Recommended for enterprise environments)
# If you use AWS SSO, set your profile name and leave credentials blank
AWS_PROFILE=sso-bedrock

# Option 2: Static credentials (for IAM users)
# Only fill these if NOT using AWS SSO
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# --- If using Anthropic API ---
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# --- If using OpenAI ---
OPENAI_API_KEY=sk-your-openai-key-here


# ============ SLACK (OPTIONAL) ============
# Set to false if you don't have Slack
ENABLE_SLACK_NOTIFICATIONS=true

# If enabled, provide token and channel:
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_CHANNEL=#airflow-monitoring


# ============ AGENT BEHAVIOR ============
# These defaults are good, but you can customize:
AGENT_TEMPERATURE=0.3
AGENT_MAX_ITERATIONS=10
WINDOW_HOURS=24
```

**Save and close the file.**

### Step 4: Test Configuration

```bash
# Make sure virtual environment is still activated
# (You should see (.venv) in your prompt)

# Test configuration loading
python -m src.cli test
```

**Expected output:**
```
✅ Configuration loaded successfully
✅ Database connection: OK
✅ AWS Bedrock: OK
✅ Slack: OK (or "Not configured" if disabled)
✅ All systems ready!
```

**If you see errors:**
- Double-check your `.env` file
- Make sure database is accessible from your machine
- Verify AWS credentials are correct
- For Slack errors (if enabled), check bot token

### Step 5: Try Interactive Mode

```bash
# Start chatting with the agent
python -m src.cli interactive
```

**Try these commands:**

```
You: Hello

You: What DAGs do we have?

You: Show me failures from last 24 hours

You: exit
```

### Step 6: Generate Your First Report

```bash
# Generate comprehensive health report
python -m src.cli report
```

This will:
- Analyze last 24 hours
- Check for failures
- Detect performance issues
- Send report to Slack (if enabled)

### Step 7: Run Proactive Monitoring

```bash
# Run in foreground (press Ctrl+C to stop)
python -m src.cli proactive --interval 15

# Or run in background
nohup python -m src.cli proactive --interval 15 > logs/proactive.log 2>&1 &

# Check logs
tail -f logs/proactive.log
```

---

## 🐳 Using Docker (Production-Ready)

### Option 1: Docker Compose (Easiest)

```bash
# Start proactive monitoring
docker-compose up -d

# View logs
docker-compose logs -f airflow-agent-proactive

# Run interactive mode
docker-compose run --rm airflow-agent-interactive

# Stop everything
docker-compose down
```

### Option 2: Docker Commands

```bash
# Build image
docker build -t airflow-agent -f deploy/Dockerfile .

# Run interactively
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  airflow-agent \
  python -m src interactive

# Note: If using AWS SSO (AWS_PROFILE in .env), add AWS credentials mount:
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  -v ~/.aws:/home/agent/.aws:ro \
  airflow-agent \
  python -m src interactive

# Run proactive monitoring (background)
docker run -d \
  --name airflow-agent \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  --restart unless-stopped \
  airflow-agent \
  python -m src proactive --interval 15

# Note: Add AWS credentials mount for SSO: -v ~/.aws:/home/agent/.aws:ro

# View logs
docker logs -f airflow-agent

# Stop
docker stop airflow-agent
docker rm airflow-agent
```

---

## 🎮 Usage Examples

### Example 1: Interactive Investigation

```bash
python -m src.cli interactive
```

```
You: What's the health status of my pipelines?

Agent: Let me check... [analyzes]
Overall health: 92.5%
- 587 active DAGs
- 3 failures in last 24 hours
- 2 performance anomalies detected

Would you like details on the failures?

You: Yes, tell me about the failures

Agent: [detailed analysis with root causes and recommendations]

You: Can you send this to Slack?

Agent: [formats and sends report]
Done! Report sent to #airflow-monitoring
```

### Example 2: One-Off Mission

```bash
# Find slow pipelines
python -m src.cli mission "Find DAGs that are running slower than usual"

# Investigate specific DAG
python -m src.cli mission "Why did etl_daily fail? Check the history"

# Comprehensive analysis
python -m src.cli mission "Analyze last 24 hours and send report to Slack"
```

### Example 3: Scheduled Reports

Add to crontab:

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily health report at 8 AM
0 8 * * * cd /path/to/agents/airflow_intelligence && source .venv/bin/activate && python -m src.cli report >> logs/daily.log 2>&1

# Check for failures every hour
0 * * * * cd /path/to/agents/airflow_intelligence && source .venv/bin/activate && python -m src.cli mission "Check for critical failures in last hour" >> logs/hourly.log 2>&1
```

### Example 4: Proactive Monitoring

```bash
# Monitor every 15 minutes
python -m src.cli proactive --interval 15

# Monitor every hour
python -m src.cli proactive --interval 60

# With detailed logging
python -m src.cli proactive --interval 30 --verbose
```

---

## 📊 Understanding the Output

### Memory System

The agent stores incidents in `.agent_memory/`:

```bash
.agent_memory/
├── incidents.jsonl      # Historical failures
├── patterns.jsonl       # Detected patterns
└── context.json         # Additional context
```

**View stored incidents:**
```bash
cat .agent_memory/incidents.jsonl | jq .
```

### Slack Reports

Reports include:
- **🎯 Overall Health** - Percentage score
- **📊 Critical Issues** - Performance problems
- **❌ Failures** - Recent pipeline failures
- **⚠️ Chronic Failures** - Repeatedly failing DAGs
- **💡 Recommendations** - Actionable next steps

### Chronic Failure Detection

The agent automatically detects patterns:

- **Daily DAGs:** 7+ failures in 7 days = chronic
- **Weekly DAGs:** 3+ consecutive failures = chronic
- **Monthly DAGs:** 3+ consecutive failures = chronic

These get highlighted in reports with special attention.

---

## 🔧 Troubleshooting

### Issue: Can't connect to database

```bash
# Test connection manually
python -c "
from src.core.config import AgentConfig
config = AgentConfig.from_env()
errors = config.validate()
if errors:
    for error in errors:
        print(f'❌ {error}')
else:
    print('✅ Configuration is valid')
"

# Check database URL format
# Correct: postgresql://user:pass@host:port/database
# Wrong: postgres://... (should be postgresql://)
```

**Common fixes:**
- Ensure database is accessible (firewall, security groups)
- Check username/password are correct
- Verify database name exists
- Try connecting with `psql` directly

### Issue: AWS Bedrock access denied

```bash
# Test AWS credentials
aws sts get-caller-identity

# Check if you have Bedrock access
aws bedrock list-foundation-models --region us-east-1 | grep claude

# Request Bedrock access
# Go to AWS Console → Bedrock → Model access → Request access
```

### Issue: Slack not working

```bash
# Test Slack token
python examples/test_slack_connection.py

# Verify bot permissions:
# 1. Go to https://api.slack.com/apps
# 2. Select your app
# 3. Go to "OAuth & Permissions"
# 4. Ensure bot has: chat:write, chat:write.public
# 5. Reinstall app to workspace if needed
```

### Issue: Import errors

```bash
# Ensure virtual environment is activated
which python  # Should point to .venv/bin/python

# If not activated:
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Try importing manually
python -c "from src.core import AgentOrchestrator"
```

### Issue: Agent not finding tools

This means the agent can't access database/Slack tools.

```bash
# Check configuration
python -c "from src.core.config import AgentConfig; config = AgentConfig.from_env(); print(config.validate())"

# Ensure database URL is correct
# Ensure AWS credentials work
# Try running test mode
python -m src.cli test
```

---

## 📈 Next Steps

Now that you have the agent running:

1. **Explore Interactive Mode**
   - Ask questions about your pipelines
   - Let the agent investigate failures
   - Learn how it thinks and reasons

2. **Set Up Proactive Monitoring**
   - Run in background with systemd/docker
   - Get automatic alerts for failures
   - Build institutional knowledge over time

3. **Schedule Regular Reports**
   - Add cron job for daily health checks
   - Review trends and patterns
   - Share with your team

4. **Customize Configuration**
   - Adjust `AGENT_TEMPERATURE` for creativity
   - Change `WINDOW_HOURS` for longer/shorter windows
   - Tune `ANOMALY_MULTIPLIER` for sensitivity

5. **Read the Docs**
   - See `docs/` for detailed guides
   - Check `examples/` for more scripts
   - Review architecture documentation

---

## 🎓 Learning Resources

- **Interactive Mode** - Best way to learn how the agent thinks
- **Examples Directory** - Sample scripts showing different use cases
- **Memory Files** - See what the agent remembers
- **Slack Reports** - Study the formatted output
- **Source Code** - `src/core/agent.py` shows the reasoning engine

---

## 💡 Pro Tips

1. **Start with interactive mode** to understand the agent's capabilities
2. **Let the agent investigate** - don't manually provide all info
3. **Check memory files** to see what patterns it's detecting
4. **Use verbose mode** when debugging (`--verbose`)
5. **Review Slack reports** for insights on your pipelines
6. **Monitor the logs** to see agent's reasoning process

---

## 🆘 Getting Help

**If you're stuck:**

1. Check this guide's Troubleshooting section
2. Run `python -m src.cli test` to verify setup
3. Review logs in `logs/` directory
4. Check `.env` file is configured correctly
5. Try examples: `python examples/test_slack_connection.py`
6. Read documentation in `docs/` folder
7. Open an issue on GitHub with:
   - What you tried
   - Error messages
   - Your configuration (without secrets!)

---

## ✅ Success Checklist

You should now be able to:

- [ ] Run `python -m src.cli test` successfully
- [ ] Chat with agent in interactive mode
- [ ] Generate a health report
- [ ] See incidents stored in `.agent_memory/`
- [ ] Receive Slack notifications (if enabled)
- [ ] Run proactive monitoring
- [ ] Understand agent's reasoning from logs

**If all checked - congratulations! You're ready to go!** 🎉

---

## 🚀 Ready for Production?

See the main [README.md](README.md) for:
- Production deployment with Kubernetes
- Systemd service setup
- CI/CD pipeline details
- Security best practices
- Performance tuning

---

**Questions?** Open an issue or check the documentation in `docs/` folder.

Happy monitoring! 🤖✨

### Using AWS SSO (Recommended for Enterprise)

If your organization uses AWS SSO, follow these steps:

```bash
# 1. Configure AWS SSO (if not already done)
aws configure sso
# Enter your SSO start URL and region
# Select the account and role
# Name the profile (e.g., "sso-bedrock")

# 2. Verify SSO login
aws sso login --profile sso-bedrock

# 3. Test Bedrock access
aws bedrock list-foundation-models --region eu-west-1 --profile sso-bedrock | grep claude

# 4. In your .env file, set:
AWS_PROFILE=sso-bedrock
AWS_REGION=eu-west-1  # or your region

# Leave AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY blank when using SSO
```

**Benefits of AWS SSO:**
- ✅ No long-lived credentials to manage
- ✅ Automatic credential rotation
- ✅ Better security and compliance
- ✅ Single sign-on across AWS accounts

**Important for Docker Users:**

When using AWS SSO with Docker, you must mount your host's AWS credentials directory into the container:

```bash
# Add this volume mount to your docker run command:
-v ~/.aws:/home/agent/.aws:ro

# Full example:
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  -v ~/.aws:/home/agent/.aws:ro \
  airflow-intelligence-agent \
  python -m src interactive
```

This allows the Docker container to access your SSO credentials. Make sure to run `aws sso login --profile sso-bedrock` before starting the container if your session has expired.
