# Airflow Runtime Monitoring System

[![CI/CD Pipeline](https://github.com/hellofresh/airflow-monitoring/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/hellofresh/airflow-monitoring/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/hellofresh/airflow-monitoring/branch/main/graph/badge.svg)](https://codecov.io/gh/hellofresh/airflow-monitoring)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready FastMCP-based system for monitoring Airflow pipeline runtime performance with AI-powered analysis and Slack integration.

## 🎯 Features

- **Real-time Airflow Monitoring**: Query DAG run metrics from Airflow database
- **AI-Powered Analysis**: Generate intelligent summaries using AWS Bedrock (Claude)
- **Slack Integration**: Automated notifications with rich formatting
- **Anomaly Detection**: Identify pipeline runs exceeding performance baselines
- **Containerized Deployment**: Docker and Kubernetes ready
- **CI/CD Ready**: Complete GitHub Actions pipeline
- **Comprehensive Testing**: Unit, integration, and E2E tests
- **Production Grade**: Monitoring, logging, and health checks

## 🏗️ Architecture

```mermaid
graph TB
    A[Scheduler/CronJob] --> B[Airflow Runtime Agent]
    B --> C[Airflow MCP Server]
    B --> D[Slack MCP Server]
    B --> E[AWS Bedrock]
    
    C --> F[(Airflow Database)]
    D --> G[Slack API]
    E --> H[Claude AI Model]
    
    B --> I[Rich Analysis Report]
    I --> J[Console Output]
    I --> K[Slack Channel]
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL (for Airflow database)
- AWS Account (for Bedrock)
- Slack Bot Token

### 1. Development Setup

```bash
# Clone the repository
git clone https://github.com/hellofresh/airflow-monitoring.git
cd airflow-monitoring

# Run development setup script
./scripts/setup-dev.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit configuration (required)
vim .env
```

**Required Configuration:**
```bash
# Database
AIRFLOW_DB_URL=postgresql://user:password@host:port/database

# AWS Bedrock
AWS_REGION=us-east-1
MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Slack (optional)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#test-notification-ai
ENABLE_SLACK_NOTIFICATIONS=true
```

### 3. Running Locally

```bash
# Install package in development mode
pip install -e ".[dev]"

# Run the monitoring agent
python -m airflow_monitoring.airflow_runtime_agent

# Or run with Docker
docker-compose up airflow-monitor
```

## 🧪 Testing

```bash
# Run all tests
./scripts/run-tests.sh all

# Run specific test types
./scripts/run-tests.sh unit
./scripts/run-tests.sh integration
./scripts/run-tests.sh e2e

# Run with coverage
pytest tests/ --cov=src/airflow_monitoring --cov-report=html
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
# Build and run
docker-compose up -d

# Or use pre-built image
docker run -d \
  --env-file .env \
  ghcr.io/hellofresh/airflow-monitoring:latest
```

## ☸️ Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace monitoring

# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n monitoring
```

### CronJob Deployment (Recommended)

The system includes a Kubernetes CronJob that runs hourly:

```bash
kubectl apply -f k8s/cronjob.yaml
```

## 🔧 Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AIRFLOW_DB_URL` | PostgreSQL connection string | - | ✅ |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` | ✅ |
| `MODEL_ID` | Bedrock model ID | `anthropic.claude-3-5-sonnet...` | ✅ |
| `SLACK_BOT_TOKEN` | Slack bot OAuth token | - | 🔶 |
| `SLACK_CHANNEL` | Target Slack channel | `#test-notification-ai` | ❌ |
| `ENABLE_SLACK_NOTIFICATIONS` | Enable Slack integration | `false` | ❌ |
| `WINDOW_HOURS` | Hours to look back for recent runs | `24` | ❌ |
| `BASELINE_DAYS` | Days of historical data for baselines | `14` | ❌ |
| `MIN_HISTORY` | Minimum runs for anomaly detection | `10` | ❌ |
| `ANOMALY_MULTIPLIER` | Anomaly threshold multiplier | `1.5` | ❌ |

## 📊 Output Examples

### Console Output
```
===============================================================================
AIRFLOW RUNTIME REPORT
===============================================================================
# Airflow Pipeline Health Report
**Generated:** 2026-02-10 12:30 UTC | **Window:** 24h

## Top 5 Longest DAG Runs
1. **data-pipeline-heavy** - `success` - 4h 24m (15,874s)
2. **ml-training-job** - `success` - 2h 44m (9,875s)
3. **etl-batch-process** - `running` - 1h 30m (5,400s)

## Anomalies Detected (3 total)
**Critical Performance Deviations (>1.5x P90 baseline):**

- **data-pipeline-heavy**: 4h 24m vs 2h 15m baseline (1.95x deviation)
- **api-sync-job**: 45m vs 20m baseline (2.25x deviation)

✅ No other anomalies detected
```

### Slack Integration
- 🟢 **Green**: No anomalies detected
- 🟡 **Yellow**: 1-5 anomalies detected  
- 🔴 **Red**: >5 anomalies detected
- Rich formatting with DAG details and recommendations

## 🔍 Available Tools (MCP Servers)

### Airflow MCP Server
- `get_dag_runs(window_hours)`: Get recent DAG runs with filtering
- `get_baseline_durations(days)`: Get historical performance data

### Slack MCP Server  
- `test_connection()`: Test Slack API connectivity
- `send_message(channel, message, username)`: Send simple text message
- `send_rich_message(channel, title, message, color)`: Send formatted message
- `send_code_block(channel, content, title, language)`: Send code block

## 🚀 CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline:

### Pipeline Stages
1. **Lint & Format**: Black, isort, flake8, mypy
2. **Test**: Unit, integration, e2e tests across Python 3.8-3.11
3. **Security**: Bandit security scanning, dependency checks
4. **Build**: Package building and Docker image creation
5. **Deploy**: Automated deployment to staging/production

### Branch Strategy
- `main`: Production releases
- `develop`: Staging deployments
- Feature branches: Pull request validation

## 📈 Monitoring & Observability

### Health Checks
- HTTP health endpoint: `/health`
- Readiness probe: `/ready`
- Container health checks included

### Logging
- Structured JSON logging
- Configurable log levels
- Container log aggregation ready

### Metrics
- Execution duration tracking
- Success/failure rates
- Anomaly detection metrics

## 🛡️ Security

- Non-root container execution
- Secret management via environment variables
- Security scanning with Bandit
- Dependency vulnerability checking
- Pre-commit security hooks

## 🔧 Development

### Code Quality
```bash
# Format code
black src tests
isort src tests

# Lint
flake8 src tests
mypy src

# Security scan  
bandit -r src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Write tests first**: Add tests in `tests/`
3. **Implement feature**: Add code in `src/airflow_monitoring/`
4. **Run quality checks**: `./scripts/run-tests.sh`
5. **Submit PR**: Pipeline will validate automatically

## 📚 API Documentation

### Environment Configuration

The system uses a centralized configuration class:

```python
from airflow_monitoring.config import MonitoringConfig

# Load from environment
config = MonitoringConfig.from_env()

# Validate configuration
errors = config.validate()
if errors:
    print(f"Configuration errors: {errors}")
```

### Package Structure

```
src/airflow_monitoring/
├── __init__.py                 # Package initialization
├── config.py                  # Configuration management
├── airflow_mcp_server.py      # Airflow database MCP server
├── slack_mcp_server.py        # Slack integration MCP server
└── airflow_runtime_agent.py   # Main monitoring agent
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines
- Follow PEP 8 and use Black formatting
- Write comprehensive tests
- Update documentation for new features
- Ensure CI pipeline passes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/hellofresh/airflow-monitoring/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hellofresh/airflow-monitoring/discussions)
- **Email**: data-contracts-cicd@hellofresh.com

## 🎉 Acknowledgments

- FastMCP framework for elegant MCP server implementation
- AWS Bedrock for AI-powered analysis
- Slack SDK for seamless integration
- HelloFresh Data Platform Team

---

**Made with ❤️ by the HelloFresh Data Platform Team**