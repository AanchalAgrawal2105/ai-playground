# AI Agents Playground

> A collection of autonomous AI agents for various enterprise use cases

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

This repository contains multiple AI agents, each designed to solve specific problems with autonomous reasoning, multi-step planning, and intelligent decision-making.

Each agent is self-contained with its own:
- Complete source code and dependencies
- Configuration and deployment scripts
- Documentation and examples
- Test suites

---

## Available Agents

### 🤖 [Airflow Intelligence Agent](agents/airflow_intelligence/)

**Autonomous Apache Airflow monitoring with persistent memory**

An intelligent agent that monitors Airflow pipelines 24/7, detects anomalies, analyzes failure patterns, and sends actionable alerts to Slack.

**Key Features:**
- 🧠 Persistent memory with chronic failure detection
- 🔄 Autonomous investigation and root cause analysis
- 📊 Proactive 24/7 monitoring
- 💬 Interactive chat interface
- 🎨 Beautiful Slack notifications

**Quick Start:**
```bash
cd agents/airflow_intelligence
cp .env.example .env
# Edit .env with your credentials

python -m src interactive
```

**Documentation:** [agents/airflow_intelligence/README.md](agents/airflow_intelligence/README.md)

---

## Repository Structure

```
myaiproject/
├── agents/
│   └── airflow_intelligence/    # Airflow monitoring agent
│       ├── src/                 # Source code
│       ├── tests/               # Test suites
│       ├── docs/                # Documentation
│       ├── examples/            # Example scripts
│       ├── deploy/              # Deployment configs
│       ├── README.md            # Quick start guide
│       └── PROJECT_OVERVIEW.md  # Comprehensive docs
│
├── .github/                     # CI/CD workflows
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## Adding New Agents

Each agent should be self-contained under `agents/<agent-name>/`:

```
agents/<agent-name>/
├── src/                    # Source code
├── tests/                  # Tests
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── README.md              # Quick start
└── PROJECT_OVERVIEW.md    # Detailed docs
```

---

## Technology Stack

**AI & LLM:**
- AWS Bedrock Claude (Anthropic)
- LangChain / Anthropic SDK

**Languages:**
- Python 3.9+

**Infrastructure:**
- Docker, Kubernetes
- GitHub Actions CI/CD

---

## Development

Each agent has its own development setup. See individual agent READMEs for specific instructions.

**General workflow:**
```bash
# Navigate to agent directory
cd agents/<agent-name>

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
pytest tests/ -v
```

---

## CI/CD

Automated workflows for:
- ✅ Code quality (black, flake8, isort, mypy)
- ✅ Security scanning (bandit, safety, gitleaks)
- ✅ Automated testing
- ✅ PR validation
- ✅ Deployment automation

See [.github/README.md](.github/README.md) for details.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Author

**Aanchal Agrawal**

Building autonomous AI agents for enterprise automation.

---

**🚀 Explore, extend, and deploy intelligent agents**
