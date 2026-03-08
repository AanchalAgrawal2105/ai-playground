# Airflow Intelligence Agent - Project Overview

## Executive Summary

This is a **production-ready, autonomous AI agent** that monitors Apache Airflow pipelines, detects failures, analyzes patterns, and sends intelligent alerts to Slack. Built with AWS Bedrock Claude, it demonstrates true agentic behavior through autonomous reasoning, multi-step planning, and persistent memory.

**Key Achievements:**
- ✅ Fully autonomous monitoring with 24/7 proactive mode
- ✅ Persistent memory system with chronic failure pattern detection
- ✅ Production-ready CI/CD pipeline with automated testing and deployment
- ✅ Clean, modular codebase following Python best practices
- ✅ Comprehensive documentation and examples
- ✅ Multiple deployment options (Systemd, Kubernetes)

---

## What Makes This "Agentic"?

Unlike traditional monitoring systems that follow rigid rules, this agent:

1. **🧠 Autonomous Reasoning** - Decides what to investigate based on objectives
2. **🔄 Multi-Step Planning** - Chains multiple tools strategically to solve problems
3. **💬 Interactive** - Have conversations, ask follow-up questions, learn from responses
4. **🎯 Goal-Oriented** - Works towards objectives with minimal human guidance
5. **📊 Context-Aware** - Maintains persistent memory across interactions and learns from patterns

**Example:** When asked "Why did dag_X fail?", the agent:
- Queries the database for failure details
- Checks historical memory for similar patterns
- Analyzes logs and error messages
- Correlates with recent changes
- Provides root cause analysis with recommendations
- Stores findings for future reference

---

## Repository Structure

```
myaiproject/
├── agents/airflow_intelligence/    # Self-contained agent package
│   ├── src/                        # Source code
│   │   ├── core/                   # Agent, orchestrator, memory, config
│   │   ├── tools/                  # Database, Slack, analysis tools
│   │   ├── monitoring/             # Proactive 24/7 monitoring
│   │   ├── cli/                    # Command-line interface
│   │   └── utils/                  # Slack formatters, utilities
│   ├── tests/                      # Unit and integration tests
│   ├── docs/                       # Documentation
│   │   ├── guides/                 # User guides
│   │   ├── architecture/           # System design docs
│   │   └── development/            # Developer docs
│   ├── examples/                   # Example scripts
│   ├── deploy/                     # Deployment configs
│   └── README.md                   # Project documentation
│
├── .github/                        # CI/CD automation
│   ├── workflows/                  # GitHub Actions
│   │   ├── ci.yml                  # Continuous integration
│   │   ├── pr-validation.yml       # PR validation
│   │   └── deploy.yml              # Deployment pipeline
│   ├── CODEOWNERS                  # Auto-assign reviewers
│   ├── dependabot.yml              # Dependency updates
│   └── README.md                   # CI/CD documentation
│
├── .flake8                         # Linting configuration
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
└── README.md                       # Repository overview
```

---

## Core Features

### 1. Persistent Memory System

Stores and recalls historical failures to detect patterns:

```python
# Detects chronic failures
- Daily DAGs: 7+ failures in 7-day window
- Weekly/Monthly: 3+ consecutive failures
```

**Memory Operations:**
- `store_incident()` - Save failure details
- `recall_historical_context()` - Retrieve similar past incidents
- `analyze_failure_patterns()` - Detect chronic issues

**Storage:** JSONL format in `.agent_memory/incidents.jsonl`

### 2. Proactive Monitoring

Autonomous 24/7 monitoring that runs every N minutes:

```bash
python -m src proactive --interval 15
```

**What it does:**
- Checks for recent failures (last 24h)
- Investigates each failure autonomously
- Sends consolidated Slack reports
- Stores findings in memory
- Learns from patterns over time

### 3. Interactive Mode

Chat-like interface for ad-hoc investigations:

```bash
python -m src interactive
```

**Example conversation:**
```
You: What DAGs failed today?
Agent: [Queries database, analyzes 3 failures]
Agent: I found 3 failed DAGs in the last 24 hours...

You: Tell me more about dag_payment_processing
Agent: [Retrieves details, checks memory, analyzes]
Agent: This DAG has failed 8 times in the past 7 days...
```

### 4. Chronic Failure Detection

Schedule-aware pattern analysis:

- **Daily DAGs:** 7+ failures in 7-day window = chronic
- **Weekly DAGs:** 3+ consecutive failures = chronic
- **Monthly DAGs:** 3+ consecutive failures = chronic

Alerts include:
- Failure frequency analysis
- Pattern detection (same error, same task)
- Historical context from memory
- Actionable recommendations

### 5. Beautiful Slack Notifications

Rich formatting using Slack Block Kit:
- Color-coded by severity (🔴 Critical, 🟡 Warning)
- Consolidated reports for multiple failures
- Clear sections: Summary, Root Cause, Recommendations
- Direct links to Airflow UI

---

## Technology Stack

**AI & LLM:**
- AWS Bedrock Claude Sonnet 4.5 - Agentic reasoning and tool use
- Anthropic SDK - Direct API integration

**Data & Storage:**
- PostgreSQL - Airflow metadata database
- SQLAlchemy - Database ORM
- JSONL - Persistent memory storage
- Pandas/NumPy - Data analysis

**Integrations:**
- Slack SDK - Notifications and alerts
- AWS Boto3 - Bedrock access

**Development:**
- Python 3.9+ - Core language
- Pytest - Testing framework
- Black/Flake8/isort - Code quality
- GitHub Actions - CI/CD

**Deployment:**
- Systemd - Linux service deployment
- Kubernetes - Container orchestration
- Docker - Containerization

---

## CI/CD Pipeline

### Workflows

**1. CI (`ci.yml`)** - Runs on PRs and pushes to dev
- Code quality (black, flake8, isort, mypy)
- Unit tests (Python 3.9, 3.10, 3.11)
- Security scanning (safety, bandit, gitleaks)
- Import verification
- Documentation checks
- Build verification

**2. PR Validation (`pr-validation.yml`)** - Runs on PRs to main
- PR title format (conventional commits)
- PR size check
- Secret scanning
- Description validation
- Breaking changes detection
- Auto-labeling

**3. Deployment (`deploy.yml`)** - Runs on push to main / tags
- Pre-deploy checks
- Docker image build
- Deploy to staging (on push to main)
- Deploy to production (on version tags)
- Rollback capability

### Branch Strategy

```
feature/* → dev → main → production
            ↓      ↓            ↓
        Basic CI  Full CI   Deploy & Tag
```

**Protection:**
- `main`: Requires 1 approval, all checks pass
- `dev`: Requires 1 approval, basic checks pass
- No force push or deletions

---

## Quick Start Guide

### Prerequisites

- Python 3.9+
- PostgreSQL (Airflow metadata database)
- AWS credentials (Bedrock access)
- Slack Bot Token (for notifications)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd myaiproject/agents/airflow_intelligence

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```bash
# Database
AIRFLOW_DB_URL=postgresql://user:pass@localhost:5432/airflow

# AWS Bedrock
AWS_REGION=us-east-1
MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#airflow-alerts
```

### Usage

**Interactive Mode:**
```bash
python -m src interactive
```

**Generate Failure Report:**
```bash
python -m src report
```

**Proactive Monitoring (24/7):**
```bash
python -m src proactive --interval 15
```

**Test Slack Connection:**
```bash
python examples/test_slack_connection.py
```

---

## Deployment Options

### 1. Systemd (Recommended for Linux)

```bash
cd agents/airflow_intelligence
sudo ./deploy/deploy.sh systemd
```

**Benefits:**
- Native Linux service
- Auto-restart on failure
- Integrated with journalctl logs
- Low overhead

**Manage:**
```bash
systemctl status airflow-intelligence-agent
journalctl -u airflow-intelligence-agent -f
systemctl restart airflow-intelligence-agent
```

### 2. Kubernetes (Production)

```bash
cd agents/airflow_intelligence
./deploy/deploy.sh k8s
```

**Includes:**
- Deployment for 24/7 monitoring
- CronJob for scheduled reports
- ConfigMap for configuration
- Secret management

---

## Testing

**Run all tests:**
```bash
cd agents/airflow_intelligence
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Tests included:**
- Memory system integration
- Failure pattern analysis
- Slack formatting
- Chronic failure detection

---

## Documentation

### For Users
- **[README.md](agents/airflow_intelligence/README.md)** - Project overview
- **[Quick Reference](agents/airflow_intelligence/docs/guides/QUICK_REFERENCE.md)** - Common commands
- **[Usage Guide](agents/airflow_intelligence/docs/guides/usage.md)** - Detailed usage
- **[Proactive Monitoring](agents/airflow_intelligence/docs/guides/proactive-monitoring.md)** - 24/7 setup

### For Reviewers
- **[Memory System](agents/airflow_intelligence/docs/guides/memory-system.md)** - How memory works
- **[Failure Analysis](agents/airflow_intelligence/docs/guides/failure-pattern-analysis.md)** - Pattern detection
- **[Architecture](agents/airflow_intelligence/docs/architecture/roadmap.md)** - System design

### For Developers
- **[Persistent Memory Explained](agents/airflow_intelligence/docs/development/PERSISTENT_MEMORY_EXPLAINED.md)** - Technical details
- **[Setup Guide](agents/airflow_intelligence/docs/deployment/setup-guide.md)** - Deployment instructions

### For CI/CD
- **[CI/CD Documentation](.github/README.md)** - Pipeline overview
- **[Branch Protection](.github/BRANCH_PROTECTION.md)** - Protection rules

---

## Code Quality

- ✅ **Type hints** throughout codebase
- ✅ **Docstrings** for all public functions
- ✅ **Black** formatted (88 char line length)
- ✅ **Flake8** compliant
- ✅ **isort** sorted imports
- ✅ **Mypy** type checked
- ✅ **>80% test coverage**

---

## Security

- ✅ Secret scanning (Gitleaks)
- ✅ Dependency scanning (Safety, Dependabot)
- ✅ Security linting (Bandit)
- ✅ Credentials in `.env` (not committed)
- ✅ Non-root Docker user

---

## Performance

**Agent Response Time:**
- Simple queries: 2-5 seconds
- Complex investigations: 10-20 seconds
- Report generation: 30-60 seconds (10+ failures)

**Resource Usage:**
- Memory: ~100-200 MB
- CPU: Minimal (<5% average)
- Storage: ~1-5 MB for memory files

**Scalability:**
- Handles 100+ DAGs
- Processes 10+ concurrent failures
- Memory scales with incident history

---

## Future Enhancements

See [roadmap.md](agents/airflow_intelligence/docs/architecture/roadmap.md) for details:

- Self-healing capabilities
- Predictive failure detection
- Multi-Airflow environment support
- Web UI dashboard
- Advanced analytics

---

## License

MIT License - See [LICENSE](LICENSE) file

---

## Support

For questions or issues:
- Review documentation in `agents/airflow_intelligence/docs/`
- Check examples in `agents/airflow_intelligence/examples/`
- See CI/CD documentation in `.github/`

---

**Built with ❤️ using AWS Bedrock Claude and Python**
