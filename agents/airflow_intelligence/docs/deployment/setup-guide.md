# 🚀 Setup Guide - Airflow Intelligence Agent

Complete guide for setting up the AI agent from scratch using virtual environments and uv.

---

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database with Airflow metadata
- AWS account with Bedrock access
- (Optional) Slack workspace with bot token

---

## Step 1: Install uv

**uv** is an ultra-fast Python package installer (10-100x faster than pip).

### macOS and Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Alternative (using pip)
```bash
pip install uv
```

### Verify Installation
```bash
uv --version
# Should output: uv 0.x.x
```

---

## Step 2: Set Up Project Structure

```bash
# Navigate to your project directory
cd /path/to/myaiproject

# Verify agent files exist
ls agents/airflow_intelligence/
# Should see: agent.py, tools.py, orchestrator.py, cli.py, etc.
```

---

## Step 3: Create Virtual Environment

```bash
# Create virtual environment using uv
uv venv

# This creates a .venv directory with Python environment
```

### What This Does
- Creates isolated Python environment
- Prevents dependency conflicts
- Keeps project dependencies separate from system Python

---

## Step 4: Activate Virtual Environment

### macOS / Linux
```bash
source .venv/bin/activate
```

### Windows (Command Prompt)
```cmd
.venv\Scripts\activate.bat
```

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

### Verify Activation
```bash
which python
# Should show: /path/to/myaiproject/.venv/bin/python

python --version
# Should show: Python 3.x.x
```

---

## Step 5: Install Dependencies

```bash
# Install all required packages using uv (much faster!)
uv pip install -r agents/airflow_intelligence/requirements.txt
```

### What Gets Installed
```
Core Dependencies:
- boto3                 # AWS Bedrock
- sqlalchemy            # Database ORM
- psycopg2-binary       # PostgreSQL driver
- pandas                # Data analysis
- numpy                 # Numerical computing
- slack-sdk             # Slack integration
- rich                  # Terminal UI
```

### Installation Time Comparison
```
pip:  ~45 seconds
uv:   ~5 seconds  ⚡ 9x faster!
```

---

## Step 6: Configure Environment Variables

### Create .env File
```bash
# Copy template
cp .env.template agents/airflow_intelligence/.env

# Edit with your credentials
vim agents/airflow_intelligence/.env
# Or use your preferred editor
```

### Required Configuration

```bash
# Database Connection (REQUIRED)
AIRFLOW_DB_URL=postgresql://username:password@hostname:5432/airflow

# AWS Bedrock Configuration (REQUIRED)
AWS_REGION=eu-west-1
MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Slack Configuration (OPTIONAL)
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#airflow-alerts
ENABLE_SLACK_NOTIFICATIONS=true

# Agent Configuration (OPTIONAL)
AGENT_TEMPERATURE=0.3
WINDOW_HOURS=24
BASELINE_DAYS=14
ANOMALY_MULTIPLIER=1.5
```

### Getting AWS Credentials

1. **Log in to AWS Console**
2. **Navigate to IAM**
3. **Create user with Bedrock permissions**
4. **Generate access keys**
5. **Copy to .env file**

### Getting Slack Token

1. **Go to api.slack.com/apps**
2. **Create new app**
3. **Add Bot Token Scopes**: `chat:write`, `channels:read`
4. **Install to workspace**
5. **Copy Bot User OAuth Token**

---

## Step 7: Verify Installation

```bash
# Run system tests
python -m agents.airflow_intelligence.cli test
```

### Expected Output
```
🧪 Running System Tests

1. Testing configuration... ✓ PASS
2. Testing database connection... ✓ PASS
3. Testing agent reasoning... ✓ PASS

Results: 3/3 tests passed
✅ All tests passed! System ready.
```

---

## Step 8: First Run

### Interactive Mode (Recommended for First Time)
```bash
python -m agents.airflow_intelligence.cli interactive
```

**Try these commands:**
```
You: What's the system status?
You: Find slow pipelines
You: Generate a health report
```

### Mission Mode
```bash
python -m agents.airflow_intelligence.cli mission "Find performance issues"
```

### Report Mode
```bash
python -m agents.airflow_intelligence.cli report
```

---

## Common Setup Issues & Solutions

### Issue 1: Virtual Environment Not Activated

**Symptom:**
```bash
python -m agents.airflow_intelligence.cli interactive
# Error: ModuleNotFoundError: No module named 'agents'
```

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Verify
which python  # Should show .venv path
```

---

### Issue 2: Database Connection Failed

**Symptom:**
```
❌ Database error: could not connect to server
```

**Solution:**
```bash
# Test database connection
psql $AIRFLOW_DB_URL

# Check:
- Database is running
- Hostname/port correct
- Username/password correct
- Network access allowed
```

---

### Issue 3: AWS Credentials Not Working

**Symptom:**
```
❌ AWS credentials not configured
```

**Solution:**
```bash
# Option 1: Check .env file
cat agents/airflow_intelligence/.env | grep AWS

# Option 2: Use AWS CLI
aws configure

# Option 3: Use IAM role (if on AWS)
# No credentials needed, uses instance role
```

---

### Issue 4: uv Command Not Found

**Symptom:**
```
bash: uv: command not found
```

**Solution:**
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell
exec $SHELL

# Or add to PATH manually
export PATH="$HOME/.cargo/bin:$PATH"
```

---

## Development Setup (Optional)

For development work, install additional tools:

```bash
# Activate venv
source .venv/bin/activate

# Install development dependencies
uv pip install pytest pytest-cov black isort mypy flake8

# Run tests
pytest tests/ -v

# Format code
black agents/airflow_intelligence/
isort agents/airflow_intelligence/

# Type checking
mypy agents/airflow_intelligence/

# Linting
flake8 agents/airflow_intelligence/
```

---

## Directory Structure After Setup

```
myaiproject/
├── .venv/                          # ✅ Virtual environment
│   ├── bin/python                  # Python executable
│   ├── lib/python3.x/site-packages # Installed packages
│   └── ...
│
├── agents/
│   └── airflow_intelligence/
│       ├── .env                    # ✅ Your configuration
│       ├── agent.py
│       ├── tools.py
│       ├── orchestrator.py
│       ├── cli.py
│       └── requirements.txt
│
└── run_agent.py
```

---

## Scheduled Jobs Setup

### Option 1: Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add hourly report
0 * * * * cd /path/to/myaiproject && source .venv/bin/activate && python -m agents.airflow_intelligence.cli report >> /var/log/airflow-agent.log 2>&1
```

### Option 2: systemd (Linux)

Create `/etc/systemd/system/airflow-agent.service`:

```ini
[Unit]
Description=Airflow Intelligence Agent
After=network.target

[Service]
Type=oneshot
User=airflow
WorkingDirectory=/path/to/myaiproject
Environment="PATH=/path/to/myaiproject/.venv/bin"
ExecStart=/path/to/myaiproject/.venv/bin/python -m agents.airflow_intelligence.cli report

[Install]
WantedBy=multi-user.target
```

Create timer `/etc/systemd/system/airflow-agent.timer`:

```ini
[Unit]
Description=Run Airflow Intelligence Agent hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable airflow-agent.timer
sudo systemctl start airflow-agent.timer
```

### Option 3: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., hourly)
4. Action: Start a program
   - Program: `C:\path\to\myaiproject\.venv\Scripts\python.exe`
   - Arguments: `-m agents.airflow_intelligence.cli report`
   - Start in: `C:\path\to\myaiproject`

---

## Updating Dependencies

```bash
# Activate venv
source .venv/bin/activate

# Update all packages
uv pip install --upgrade -r agents/airflow_intelligence/requirements.txt

# Update specific package
uv pip install --upgrade boto3

# Check for outdated packages
uv pip list --outdated
```

---

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

This returns you to your system Python environment.

---

## Multiple Environments (Optional)

You can create multiple environments for different purposes:

```bash
# Production environment
uv venv .venv-prod
source .venv-prod/bin/activate
uv pip install -r requirements.txt

# Development environment
uv venv .venv-dev
source .venv-dev/bin/activate
uv pip install -r requirements.txt
uv pip install pytest black mypy

# Testing environment
uv venv .venv-test
source .venv-test/bin/activate
uv pip install -r requirements.txt
uv pip install pytest pytest-cov
```

---

## Uninstallation

If you need to remove everything:

```bash
# Deactivate venv
deactivate

# Remove virtual environment
rm -rf .venv

# Remove .env file
rm agents/airflow_intelligence/.env

# Remove agent code (optional)
rm -rf agents/airflow_intelligence/
```

---

## Next Steps

After setup is complete:

1. ✅ Read [USAGE.md](./USAGE.md) for detailed usage guide
2. ✅ Try interactive mode to explore capabilities
3. ✅ Set up scheduled monitoring jobs
4. ✅ Integrate with your Slack workspace
5. ✅ Customize configuration for your needs

---

## Support & Troubleshooting

### Quick Diagnostics

```bash
# Check Python version
python --version

# Check virtual environment
which python

# Check installed packages
uv pip list

# Check configuration
python -m agents.airflow_intelligence.cli config

# Run full system test
python -m agents.airflow_intelligence.cli test --debug
```

### Get Help

1. **Check logs** - Look for error messages
2. **Enable debug mode** - Use `--debug` flag
3. **Review documentation** - USAGE.md, README.md
4. **Test components** - Run individual tests

---

## Summary Checklist

- [ ] Install uv
- [ ] Create virtual environment (`uv venv`)
- [ ] Activate venv (`source .venv/bin/activate`)
- [ ] Install dependencies (`uv pip install -r requirements.txt`)
- [ ] Create .env file with credentials
- [ ] Run tests (`python -m ... cli test`)
- [ ] Try interactive mode
- [ ] Set up scheduled jobs (optional)

---

**✅ Setup Complete! You're ready to use the AI agent!** 🎉

**Quick start command:**
```bash
source .venv/bin/activate && python -m agents.airflow_intelligence.cli interactive
```
