# Airflow Intelligence Agent

> **Autonomous AI agent for Apache Airflow monitoring with persistent memory and chronic failure detection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

An intelligent, self-contained AI agent that autonomously monitors Airflow pipelines, detects anomalies, analyzes failure patterns, and sends actionable alerts. Built with AWS Bedrock Claude, it demonstrates true agentic behavior through autonomous reasoning, multi-step planning, and persistent memory.

**🎯 For a comprehensive overview, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**

---

## Key Features

### 🤖 **Autonomous Investigation**
Decides what to investigate and how to solve problems with minimal human guidance

### 🧠 **Persistent Memory**
Stores and recalls historical failures to detect chronic patterns:
- Daily DAGs: 7+ failures in 7 days = chronic
- Weekly/Monthly: 3+ consecutive failures = chronic

### 📊 **Proactive Monitoring**
Runs 24/7, checking for failures every N minutes and sending consolidated Slack reports

### 💬 **Interactive Mode**
Chat-like interface for ad-hoc investigations and follow-up questions

### 📈 **Pattern Detection**
Schedule-aware analysis that learns from historical data

### 🎨 **Beautiful Slack Alerts**
Rich, color-coded notifications with root cause analysis and recommendations

---

## Quick Start

### Installation

```bash
cd agents/airflow_intelligence

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

Create `.env` file with:

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

**Interactive Mode (Chat with Agent):**
```bash
python -m src interactive
```

**Generate Failure Report:**
```bash
python -m src report
```

**Execute a Mission:**
```bash
python -m src mission "Find performance anomalies in last 24 hours"
```

**Proactive Monitoring (24/7):**
```bash
python -m src proactive --interval 15
```

---

## What Makes This "Agentic"?

Unlike traditional monitoring systems, this agent:

| Traditional Monitoring | This AI Agent |
|------------------------|---------------|
| Follows rigid rules | **Autonomous reasoning and decision-making** |
| Single-step queries | **Multi-step strategic planning** |
| Stateless | **Persistent memory and pattern learning** |
| Pre-programmed responses | **Goal-oriented with minimal guidance** |
| Alert on threshold | **Contextual analysis with root cause** |

**Example:** When investigating a failure, the agent:
1. Queries database for failure details
2. Checks memory for similar historical patterns
3. Analyzes error messages and logs
4. Correlates with recent changes
5. Provides root cause analysis
6. Stores findings for future reference

---

## Project Structure

```
agents/airflow_intelligence/     # Self-contained agent package
├── src/                         # Source code
│   ├── core/                    # Agent, orchestrator, memory
│   ├── tools/                   # Database, Slack, analysis
│   ├── monitoring/              # Proactive 24/7 monitoring
│   ├── cli/                     # Command-line interface
│   └── utils/                   # Utilities
├── tests/                       # Unit and integration tests
├── docs/                        # Documentation
│   ├── guides/                  # User guides
│   ├── architecture/            # System design
│   ├── development/             # Developer docs
│   └── deployment/              # Deployment guides
├── examples/                    # Example scripts
├── deploy/                      # Deployment configs
│   ├── Dockerfile               # Container image
│   ├── systemd/                 # Linux service
│   └── kubernetes/              # K8s manifests
└── README.md                    # Project documentation
```

---

## Documentation

### **Start Here**
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Comprehensive project overview
- **[agents/airflow_intelligence/README.md](agents/airflow_intelligence/README.md)** - Detailed project documentation

### **User Guides**
- [Quick Reference](agents/airflow_intelligence/docs/guides/QUICK_REFERENCE.md) - Common commands
- [Usage Guide](agents/airflow_intelligence/docs/guides/usage.md) - Detailed usage
- [Proactive Monitoring](agents/airflow_intelligence/docs/guides/proactive-monitoring.md) - 24/7 setup
- [Memory System](agents/airflow_intelligence/docs/guides/memory-system.md) - How memory works
- [Failure Analysis](agents/airflow_intelligence/docs/guides/failure-pattern-analysis.md) - Pattern detection

### **Technical Documentation**
- [Persistent Memory Explained](agents/airflow_intelligence/docs/development/PERSISTENT_MEMORY_EXPLAINED.md) - Memory architecture
- [Setup Guide](agents/airflow_intelligence/docs/deployment/setup-guide.md) - Deployment instructions
- [Roadmap](agents/airflow_intelligence/docs/architecture/roadmap.md) - Future enhancements

### **CI/CD**
- [CI/CD Documentation](.github/README.md) - Pipeline overview
- [Branch Protection](.github/BRANCH_PROTECTION.md) - Protection rules

---

## Deployment

### Systemd (Recommended for Linux)

```bash
cd agents/airflow_intelligence
sudo ./deploy/deploy.sh systemd
```

- Native Linux service
- Auto-restart on failure
- Integrated logging
- Low overhead

### Kubernetes (Production)

```bash
cd agents/airflow_intelligence
./deploy/deploy.sh k8s
```

- Deployment for 24/7 monitoring
- CronJob for scheduled reports
- ConfigMap and Secret management

---

## CI/CD Pipeline

**Complete production-ready pipeline with:**

- ✅ Automated testing (Python 3.9, 3.10, 3.11)
- ✅ Code quality checks (black, flake8, isort, mypy)
- ✅ Security scanning (safety, bandit, gitleaks)
- ✅ PR validation (title, size, secrets)
- ✅ Automated deployment (staging/production)
- ✅ Dependency updates (Dependabot)

**Workflow:**
```
feature/* → dev (1 approval) → main (1 approval) → production
            ↓                    ↓                      ↓
        Basic CI          Full CI + Deploy       Release & Tag
```

See [.github/README.md](.github/README.md) for details.

---

## Technology Stack

**AI & LLM:**
- AWS Bedrock Claude Sonnet 4.5
- Anthropic SDK

**Data & Storage:**
- PostgreSQL, SQLAlchemy
- JSONL (persistent memory)
- Pandas, NumPy

**Integrations:**
- Slack SDK
- AWS Boto3

**Development:**
- Python 3.9+
- Pytest, Black, Flake8
- GitHub Actions

---

## Testing

```bash
cd agents/airflow_intelligence

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

**Test Coverage:** >80%

**Tests Include:**
- Memory system integration
- Failure pattern analysis
- Slack formatting
- Chronic failure detection

---

## Code Quality

- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Black formatted (88 chars)
- ✅ Flake8 compliant
- ✅ isort sorted imports
- ✅ Mypy type checked

---

## Security

- ✅ Secret scanning (Gitleaks)
- ✅ Dependency scanning (Safety, Dependabot)
- ✅ Security linting (Bandit)
- ✅ Credentials in `.env` (not committed)
- ✅ Non-root Docker user

---

## Performance

**Response Times:**
- Simple queries: 2-5 seconds
- Complex investigations: 10-20 seconds
- Report generation: 30-60 seconds (10+ failures)

**Resource Usage:**
- Memory: ~100-200 MB
- CPU: <5% average
- Storage: ~1-5 MB for memory files

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Author

**Aanchal Agrawal**

---

**🚀 Production-Ready AI Agent for Airflow Monitoring**
