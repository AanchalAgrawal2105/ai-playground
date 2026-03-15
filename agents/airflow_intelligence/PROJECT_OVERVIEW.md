# Airflow Intelligence Agent - Project Overview

> **⚠️ This file has been merged into the main README.md**
>
> Please see **[README.md](README.md)** for comprehensive documentation.

## Quick Links

- **📖 [Complete Documentation](README.md)** - Everything in one place
- **🚀 [Getting Started Guide](GETTING_STARTED.md)** - Step-by-step setup
- **🐳 [Docker Compose](docker-compose.yml)** - Quick deployment
- **⚙️ [Configuration](README.md#-configuration)** - All environment variables
- **📚 [User Guides](docs/guides/)** - Detailed guides

## What Changed?

The PROJECT_OVERVIEW.md content has been merged into README.md with improvements:

### ✅ New in README.md

1. **Comprehensive "Getting Started" section** - Step-by-step local setup
2. **Docker Quick Start** - Get running in 5 minutes
3. **Detailed Usage Guide** - All modes explained with examples
4. **Configuration Reference** - Complete `.env` documentation
5. **Troubleshooting Section** - Common issues and fixes
6. **Deployment Options** - Docker, Systemd, Kubernetes, Cron
7. **CI/CD Information** - Pipeline details
8. **Testing Guide** - How to run tests locally

### 📂 New Files Added

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Beginner-friendly complete walkthrough
- **[docker-compose.yml](docker-compose.yml)** - Easy Docker deployment
- **[deploy/Dockerfile](deploy/Dockerfile)** - Optimized for local & production use

## Quick Start

### Using Docker (Fastest)

```bash
# Clone, configure, run
git clone https://github.com/AanchalAgrawal2105/ai-playground.git
cd ai-playground/agents/airflow_intelligence
cp .env.example .env  # Edit with your credentials
docker-compose up -d
```

### Using Python Locally

```bash
# Clone and setup
git clone https://github.com/AanchalAgrawal2105/ai-playground.git
cd ai-playground/agents/airflow_intelligence

# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env  # Edit with your credentials

# Run
python -m src.cli interactive
```

## Documentation Structure

```
agents/airflow_intelligence/
├── README.md                    # 📖 MAIN DOCUMENTATION (start here!)
├── GETTING_STARTED.md           # 🚀 Step-by-step beginner guide
├── PROJECT_OVERVIEW.md          # 📋 This file (redirects to README)
├── docker-compose.yml           # 🐳 Docker deployment
├── .env.example                 # ⚙️ Configuration template
│
├── docs/
│   ├── guides/                  # User guides
│   │   ├── usage.md
│   │   ├── proactive-monitoring.md
│   │   ├── memory-system.md
│   │   └── failure-pattern-analysis.md
│   ├── architecture/            # System design
│   └── development/             # Developer guides
│
└── examples/                    # Example scripts
```

## Features Overview

✅ **Autonomous AI Agent** - Claude Sonnet 4.5 powered reasoning
✅ **Persistent Memory** - Learns from past incidents
✅ **Proactive 24/7 Monitoring** - Runs continuously
✅ **Interactive Chat Mode** - Natural language interface
✅ **Chronic Failure Detection** - Pattern analysis
✅ **Beautiful Slack Reports** - Block Kit formatting
✅ **Production CI/CD** - Automated testing & deployment
✅ **Multiple Deployment Options** - Docker, K8s, Systemd
✅ **Comprehensive Testing** - Unit & integration tests
✅ **Full Documentation** - Guides for all user types

## Getting Help

1. **Start Here:** [README.md](README.md) - Main documentation
2. **New User?** [GETTING_STARTED.md](GETTING_STARTED.md) - Complete walkthrough
3. **Specific Topic?** Check `docs/guides/` for detailed guides
4. **Issues?** See troubleshooting in README or open GitHub issue

---

**📖 [Go to Main Documentation →](README.md)**

**🚀 [Go to Getting Started Guide →](GETTING_STARTED.md)**
