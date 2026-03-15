# 🤖 Airflow Intelligence Agent

> **Production-ready, autonomous AI agent** for Apache Airflow pipeline monitoring, failure detection, pattern analysis, and intelligent Slack alerts.

[![CI Status](https://github.com/AanchalAgrawal2105/ai-playground/workflows/CI/badge.svg)](https://github.com/AanchalAgrawal2105/ai-playground/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)

---

## 📋 Table of Contents

- [What Makes This "Agentic"?](#-what-makes-this-agentic)
- [Key Features](#-key-features)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Local Development Setup](#-local-development-setup)
- [Usage Guide](#-usage-guide)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Documentation](#-documentation)

---

## 🎯 What Makes This "Agentic"?

Unlike traditional monitoring systems that follow rigid rules, this agent demonstrates **true agentic behavior**:

| Traditional Monitoring | Agentic Intelligence |
|----------------------|---------------------|
| ❌ Fixed alert rules | ✅ **Autonomous reasoning** - Decides what to investigate |
| ❌ Single-step checks | ✅ **Multi-step planning** - Chains tools strategically |
| ❌ Rigid workflows | ✅ **Interactive** - Conversational interface |
| ❌ Stateless | ✅ **Persistent memory** - Learns from patterns |
| ❌ Reactive only | ✅ **Proactive** - 24/7 autonomous monitoring |

**Example:** When asked "Why did dag_X fail?", the agent:
1. Queries database for failure details
2. Checks historical memory for similar patterns
3. Analyzes logs and correlates with recent changes
4. Provides root cause analysis with recommendations
5. Stores findings for future reference

---

## ✨ Key Features

### 🧠 **Persistent Memory System**
- Stores historical failures in JSONL format
- Detects chronic failure patterns (7+ failures in 7 days for daily DAGs)
- Provides context-aware analysis based on past incidents

### 🔄 **Proactive 24/7 Monitoring**
- Autonomous monitoring every N minutes
- Investigates failures independently
- Sends consolidated Slack reports
- Learns from patterns over time

### 💬 **Interactive Chat Mode**
- Natural language conversations
- Ask follow-up questions
- Get detailed explanations
- Real-time investigation

### 📊 **Chronic Failure Detection**
- **Daily DAGs:** 7+ failures in 7-day window
- **Weekly DAGs:** 3+ consecutive failures
- **Monthly DAGs:** 3+ consecutive failures
- Schedule-aware pattern analysis

### 📱 **Beautiful Slack Notifications**
- Rich formatting using Slack Block Kit
- Color-coded severity indicators
- Structured reports with clear sections
- Direct links to Airflow UI

---

## 🚀 Quick Start with Docker

The fastest way to try the agent:

```bash
# 1. Clone the repository
git clone https://github.com/AanchalAgrawal2105/ai-playground.git
cd ai-playground/agents/airflow_intelligence

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# 3. Build Docker image
docker build -t airflow-intelligence-agent -f deploy/Dockerfile .

# 4. Run interactive mode
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  airflow-intelligence-agent \
  python -m src.cli interactive

# 5. Or run proactive monitoring
docker run -d \
  --name airflow-agent \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  --restart unless-stopped \
  airflow-intelligence-agent \
  python -m src.cli proactive --interval 15
```

---

## 💻 Local Development Setup

### Prerequisites

- **Python 3.9+** (3.9, 3.10, or 3.11)
- **PostgreSQL** - Airflow metadata database access
- **AWS Account** - For Bedrock Claude access
- **Slack Bot** (optional) - For notifications

### Step-by-Step Local Setup

#### 1️⃣ **Clone and Navigate**

```bash
git clone https://github.com/AanchalAgrawal2105/ai-playground.git
cd ai-playground/agents/airflow_intelligence
```

#### 2️⃣ **Set Up Python Environment**

**Option A: Using `uv` (Recommended - Much Faster)**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies (ultra-fast!)
uv pip install -r requirements.txt
```

**Option B: Using `pip` (Traditional)**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### 3️⃣ **Install Development Dependencies** (Optional)

```bash
# For running tests and code quality checks
pip install -r ../../requirements-dev.txt
```

#### 4️⃣ **Configure Environment Variables**

```bash
# Copy example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

**Minimum Required Configuration:**

```bash
# Database - REQUIRED
AIRFLOW_DB_URL=postgresql://user:password@host:5432/airflow_db

# AWS Bedrock - REQUIRED
AWS_REGION=us-east-1
MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Slack - OPTIONAL (set ENABLE_SLACK_NOTIFICATIONS=false if not using)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#airflow-monitoring
ENABLE_SLACK_NOTIFICATIONS=true
```

See [Configuration](#-configuration) section for all options.

#### 5️⃣ **Verify Setup**

```bash
# Test database connection
python -c "from src.core.config import AgentConfig; config = AgentConfig.from_env(); print('✅ Configuration loaded successfully')"

# Test imports
python -c "from src.core import AgentOrchestrator, AgentMemory; print('✅ All imports working')"
```

#### 6️⃣ **Create Memory Directory** (Automatic on first run)

```bash
# The agent will create this automatically, but you can create it manually:
mkdir -p .agent_memory
```

---

## 📖 Usage Guide

### Interactive Mode - Chat with the Agent

Perfect for ad-hoc investigations and learning how the agent works:

```bash
# Activate virtual environment
source .venv/bin/activate

# Start interactive mode
python -m src.cli interactive
```

**Example Conversation:**

```
You: What DAGs failed in the last 24 hours?

Agent: Let me check the recent failures...
[Agent autonomously queries database and analyzes results]

Agent: I found 3 failed DAGs in the last 24 hours:
1. etl_daily_pipeline - Failed at 02:15 AM (task: transform_data)
2. customer_sync - Failed at 03:30 AM (task: load_to_warehouse)
3. reporting_job - Failed at 08:00 AM (task: generate_reports)

Would you like me to investigate any of these in detail?

You: Tell me more about etl_daily_pipeline

Agent: [Recalls historical context from memory]
This is concerning - etl_daily_pipeline has failed 6 times in the past 7 days,
making it a chronic failure...
[Provides detailed analysis with recommendations]
```

**Interactive Commands:**
- `exit` or `quit` - Exit interactive mode
- Any natural language question about your pipelines

---

### Mission Mode - Single Objective Execution

Execute a specific task and exit:

```bash
# Find performance issues
python -m src.cli mission "Find DAGs with performance degradation in last 24 hours"

# Investigate specific DAG
python -m src.cli mission "Why did etl_daily fail? Provide root cause analysis"

# Generate and send report
python -m src.cli mission "Analyze pipeline health and send comprehensive report to Slack"

# With verbose output
python -m src.cli mission "Investigate slow pipelines" --verbose
```

---

### Report Mode - Automated Health Reports

Generate a comprehensive health report (great for cron jobs):

```bash
python -m src.cli report
```

**What it does:**
- Analyzes last 24 hours of pipeline activity
- Detects failures and performance issues
- Calculates overall health metrics
- Identifies chronic failures using memory
- Sends beautifully formatted report to Slack

**Schedule with Cron:**
```bash
# Edit crontab
crontab -e

# Add: Run health report every day at 8 AM
0 8 * * * cd /path/to/agents/airflow_intelligence && source .venv/bin/activate && python -m src.cli report >> logs/report.log 2>&1
```

---

### Proactive Mode - 24/7 Autonomous Monitoring

Continuous monitoring that runs in the background:

```bash
# Run every 15 minutes
python -m src.cli proactive --interval 15

# Run every hour
python -m src.cli proactive --interval 60

# With verbose logging
python -m src.cli proactive --interval 30 --verbose
```

**What it does:**
- Runs autonomously every N minutes
- Checks for new failures since last run
- Investigates each failure independently
- Analyzes patterns using memory system
- Sends Slack alerts only when issues found
- Learns from patterns over time

**Run as Background Service:**

```bash
# Using nohup
nohup python -m src.cli proactive --interval 15 > logs/proactive.log 2>&1 &

# Check status
ps aux | grep "proactive"

# Stop
kill <PID>
```

---

### Test Mode - Verify Configuration

```bash
python -m src.cli test
```

Tests all components:
- ✅ Database connectivity
- ✅ AWS Bedrock access
- ✅ Slack integration (if enabled)
- ✅ Agent initialization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
│          (Chat / Mission / Report / Proactive)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                         │
│          (Coordinates agent lifecycle & tools)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│              AI Agent Brain (Claude Sonnet 4.5)             │
│        • Reasoning & Planning                               │
│        • Tool Selection                                     │
│        • Multi-step Problem Solving                         │
└──┬──────────────────┬──────────────────┬───────────────┬────┘
   │                  │                  │               │
   ↓                  ↓                  ↓               ↓
┌──────────┐   ┌────────────┐   ┌─────────────┐   ┌─────────┐
│ Database │   │   Memory   │   │   Slack     │   │Analysis │
│  Tools   │   │   System   │   │   Tools     │   │ Tools   │
└──────────┘   └────────────┘   └─────────────┘   └─────────┘
     │              │                  │               │
     ↓              ↓                  ↓               ↓
┌──────────┐   ┌────────────┐   ┌─────────────┐   ┌─────────┐
│PostgreSQL│   │   JSONL    │   │Slack Block  │   │Pandas/  │
│Metadata  │   │ .agent_mem │   │   Kit API   │   │NumPy    │
│Database  │   │   ory/     │   │             │   │         │
└──────────┘   └────────────┘   └─────────────┘   └─────────┘
```

### Component Overview

**Agent Core:**
- `agent.py` - AI reasoning engine (Claude integration)
- `orchestrator.py` - Tool coordination & execution
- `memory.py` - Persistent incident storage & pattern detection
- `config.py` - Configuration management

**Tools:**
- `database.py` - Query Airflow metadata (DAG runs, tasks, performance)
- `slack.py` - Send beautiful formatted notifications
- `analysis.py` - Anomaly detection & statistical analysis
- `registry.py` - Tool registration & execution

**Monitoring:**
- `proactive_monitor.py` - 24/7 autonomous monitoring

**CLI:**
- `commands.py` - Command-line interface for all modes

**Utilities:**
- `slack_formatter.py` - Slack Block Kit formatting

---

## ⚙️ Configuration

### Environment Variables Reference

Create a `.env` file from `.env.example`:

```bash
# ============================================================================
# DATABASE CONFIGURATION - REQUIRED
# ============================================================================
AIRFLOW_DB_URL=postgresql://username:password@hostname:5432/database

# ============================================================================
# AWS BEDROCK CONFIGURATION - REQUIRED
# ============================================================================
AWS_REGION=us-east-1
MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0

# AWS Credentials (use IAM role in production, credentials for local dev)
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_SESSION_TOKEN=                    # Optional, for temporary credentials

# ============================================================================
# SLACK CONFIGURATION - OPTIONAL
# ============================================================================
ENABLE_SLACK_NOTIFICATIONS=true      # Set to false to disable Slack

# Required only if ENABLE_SLACK_NOTIFICATIONS=true
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#airflow-monitoring
SLACK_USERNAME=Airflow Intelligence Agent

# ============================================================================
# AGENT BEHAVIOR - REQUIRED
# ============================================================================
AGENT_TEMPERATURE=0.3                 # 0.0-1.0 (lower = more deterministic)
AGENT_MAX_TOKENS=4096                 # Max tokens per response
AGENT_MAX_ITERATIONS=10               # Max reasoning loops per mission

# ============================================================================
# MONITORING CONFIGURATION - REQUIRED
# ============================================================================
WINDOW_HOURS=24                       # Hours to look back for failures
BASELINE_DAYS=14                      # Days for baseline calculation
MIN_HISTORY=10                        # Min runs required for baseline
ANOMALY_MULTIPLIER=1.5                # Threshold: duration > baseline * multiplier
STALE_DAG_THRESHOLD_DAYS=10           # Days before DAG considered stale

# ============================================================================
# PERFORMANCE TUNING - REQUIRED
# ============================================================================
QUERY_TIMEOUT=30                      # Database query timeout (seconds)
MAX_RESULTS=1000                      # Maximum results per query
```

### Getting Slack Bot Token

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Go to "OAuth & Permissions"
4. Add Bot Token Scopes:
   - `chat:write`
   - `chat:write.public`
5. Install app to workspace
6. Copy "Bot User OAuth Token" (starts with `xoxb-`)

### Getting AWS Credentials

**For Local Development:**
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

**For Production:**
Use IAM roles instead of hardcoded credentials.

---

## 🧪 Testing

### Run Tests Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Structure

```
tests/
├── test_memory_integration.py      # Memory system tests
└── test_failure_pattern_analysis.py # Chronic failure detection tests
```

**Current Test Coverage:** 26% (8/8 tests passing)

### Manual Testing

```bash
# Test configuration
python -m src.cli test

# Test Slack connection
python examples/test_slack_connection.py

# Test memory system
python examples/run_agent.py
```

---

## 🚀 Deployment

### Option 1: Docker (Recommended)

**Build Image:**
```bash
docker build -t airflow-intelligence-agent -f deploy/Dockerfile .
```

**Run Proactive Monitoring:**
```bash
docker run -d \
  --name airflow-agent \
  --env-file .env \
  -v $(pwd)/.agent_memory:/app/.agent_memory \
  --restart unless-stopped \
  airflow-intelligence-agent \
  python -m src.cli proactive --interval 15
```

**View Logs:**
```bash
docker logs -f airflow-agent
```

**Stop & Remove:**
```bash
docker stop airflow-agent
docker rm airflow-agent
```

---

### Option 2: Systemd Service (Linux)

**Deploy:**
```bash
cd deploy
sudo ./deploy.sh systemd
```

**Manage Service:**
```bash
# Check status
sudo systemctl status airflow-intelligence-agent

# View logs
sudo journalctl -u airflow-intelligence-agent -f

# Restart
sudo systemctl restart airflow-intelligence-agent

# Stop
sudo systemctl stop airflow-intelligence-agent

# Disable auto-start
sudo systemctl disable airflow-intelligence-agent
```

---

### Option 3: Kubernetes

**Deploy:**
```bash
cd deploy
./deploy.sh k8s
```

**Includes:**
- Deployment for 24/7 proactive monitoring
- CronJob for scheduled reports
- ConfigMap for configuration
- Secret for sensitive data

**Manage:**
```bash
# Check status
kubectl get pods -l app=airflow-intelligence-agent

# View logs
kubectl logs -f deployment/airflow-intelligence-agent

# Scale
kubectl scale deployment airflow-intelligence-agent --replicas=2

# Delete
kubectl delete -f kubernetes/
```

---

### Option 4: Cron Job (Simple Scheduled Reports)

```bash
# Edit crontab
crontab -e

# Add scheduled job
# Daily report at 8 AM
0 8 * * * cd /path/to/airflow_intelligence && source .venv/bin/activate && python -m src.cli report >> logs/report.log 2>&1

# Health check every 4 hours
0 */4 * * * cd /path/to/airflow_intelligence && source .venv/bin/activate && python -m src.cli mission "Check for critical failures and alert if found" >> logs/health.log 2>&1
```

---

## 🔄 CI/CD Pipeline

The project includes a production-ready CI/CD pipeline with GitHub Actions:

### Workflows

**1. Continuous Integration (`ci.yml`)** - Runs on PRs and pushes to dev
- ✅ Code quality (Black, isort, flake8)
- ✅ Unit tests (Python 3.9, 3.10, 3.11)
- ℹ️ Security scanning (optional)
- ℹ️ Import verification (optional)
- ℹ️ Documentation checks (optional)
- ℹ️ Build verification (optional)

**2. PR Validation (`pr-validation.yml`)** - Runs on PRs to main
- ✅ PR size check (warns if >1000 lines)
- ✅ Breaking changes detection
- ℹ️ PR title format (optional)
- ℹ️ Secret scanning (optional)
- ℹ️ Description validation (optional)

**3. Deployment (`deploy.yml`)** - Runs on push to main / version tags
- Pre-deploy validation
- Docker image build and push
- Deploy to staging (on push to main)
- Deploy to production (on version tags)

### Branch Strategy

```
feature/* → dev → main → production
            ↓      ↓            ↓
        Basic CI  Full CI   Deploy & Tag
```

### Running CI Checks Locally

```bash
# Code formatting
black --check src/ tests/

# Import sorting
isort --check-only src/ tests/

# Linting
flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,E501,W503

# Tests
pytest tests/ -v --cov=src
```

---

## 📚 Documentation

### For Users
- **[Quick Reference](docs/guides/QUICK_REFERENCE.md)** - Common commands
- **[Usage Guide](docs/guides/usage.md)** - Detailed usage
- **[Proactive Monitoring](docs/guides/proactive-monitoring.md)** - 24/7 setup

### For Reviewers
- **[Memory System](docs/guides/memory-system.md)** - How memory works
- **[Failure Analysis](docs/guides/failure-pattern-analysis.md)** - Pattern detection
- **[Architecture](docs/architecture/roadmap.md)** - System design

### For Developers
- **[Persistent Memory Explained](docs/development/PERSISTENT_MEMORY_EXPLAINED.md)** - Technical details
- **[Setup Guide](docs/deployment/setup-guide.md)** - Deployment instructions

### For CI/CD
- **[CI/CD Documentation](../../.github/README.md)** - Pipeline overview

---

## 🛠️ Development

### Project Structure

```
agents/airflow_intelligence/
├── src/                         # Source code
│   ├── core/                    # Agent, orchestrator, memory, config
│   ├── tools/                   # Database, Slack, analysis tools
│   ├── monitoring/              # Proactive 24/7 monitoring
│   ├── cli/                     # Command-line interface
│   └── utils/                   # Slack formatters, utilities
├── tests/                       # Unit and integration tests
├── docs/                        # Documentation
├── examples/                    # Example scripts
├── deploy/                      # Deployment configs
│   ├── Dockerfile               # Docker image
│   ├── kubernetes/              # K8s manifests
│   └── systemd/                 # Systemd service files
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment config
└── README.md                    # This file
```

### Adding New Features

1. **Add Tool:** Create function in `src/tools/`
2. **Register Tool:** Add to agent's `get_tools()` in `src/core/agent.py`
3. **Test:** Try in interactive mode
4. **Document:** Update relevant docs
5. **Test:** Write unit tests

### Code Quality Standards

- ✅ **Black** formatted (100 char line length)
- ✅ **isort** sorted imports
- ✅ **flake8** compliant
- ✅ Type hints throughout
- ✅ Docstrings for all public functions
- ✅ >80% test coverage target

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following code quality standards
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'feat: Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open Pull Request

---

## 📊 Performance

**Agent Response Time:**
- Simple queries: 2-5 seconds
- Complex investigations: 10-20 seconds
- Report generation: 30-60 seconds

**Resource Usage:**
- Memory: ~100-200 MB
- CPU: Minimal (<5% average)
- Storage: ~1-5 MB for memory files

**Scalability:**
- Handles 100+ DAGs
- Processes 10+ concurrent failures
- Memory scales linearly with incident history

---

## 🔐 Security

- ✅ Secret scanning (Gitleaks)
- ✅ Dependency scanning (Dependabot)
- ✅ Security linting (Bandit)
- ✅ No secrets in code
- ✅ Non-root Docker user
- ✅ Environment-based configuration

---

## 📝 License

MIT License - See [LICENSE](../../LICENSE) file

---

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Test connection
python -c "from src.core.config import AgentConfig; config = AgentConfig.from_env(); errors = config.validate(); print(errors if errors else '✅ Config OK')"

# Check database URL format
# Should be: postgresql://user:pass@host:port/database
```

**2. AWS Bedrock Access Denied**
```bash
# Verify credentials
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-1
```

**3. Slack Not Working**
```bash
# Test Slack token
python examples/test_slack_connection.py

# Verify bot has correct permissions:
# - chat:write
# - chat:write.public
```

**4. Import Errors**
```bash
# Ensure you're in virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📞 Support

**Questions or Issues?**
- Review documentation in `docs/` directory
- Check examples in `examples/` directory
- Open an issue on GitHub
- See CI/CD docs in `.github/`

---

## 🎉 Acknowledgments

Built with:
- **AWS Bedrock Claude Sonnet 4.5** - AI reasoning engine
- **Anthropic SDK** - Claude API integration
- **Slack Block Kit** - Beautiful notifications
- **Python 3.9+** - Core language

---

**Built with ❤️ for the Airflow community**

🚀 Happy monitoring! Let the agent handle the boring stuff while you focus on building great pipelines.
