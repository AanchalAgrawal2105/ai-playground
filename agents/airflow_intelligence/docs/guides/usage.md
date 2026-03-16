# 🚀 Usage Guide - Airflow Intelligence Agent

## Quick Start

### 1. Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### 2. Create Virtual Environment & Install Dependencies

```bash
# Navigate to the agent directory
cd agents/airflow_intelligence

# Create virtual environment with uv
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install all dependencies using uv (much faster than pip!)
uv pip install -r requirements.txt

# Or install from project root
cd /path/to/myaiproject
uv venv
source .venv/bin/activate
uv pip install -r agents/airflow_intelligence/requirements.txt
```

**Why uv?**
- ⚡ **10-100x faster** than pip
- 🔒 **Deterministic** dependency resolution
- 🎯 **Drop-in replacement** for pip
- 💾 **Global cache** - installs are reused

### 3. Configure Environment

```bash
# Copy environment template
cp .env.template agents/airflow_intelligence/.env

# Edit configuration
vim agents/airflow_intelligence/.env
```

**Required Configuration:**
```bash
# Database (Required)
AIRFLOW_DB_URL=postgresql://user:password@host:5432/airflow

# AWS Bedrock (Required)
AWS_REGION=eu-west-1
MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Slack (Optional)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#airflow-alerts
ENABLE_SLACK_NOTIFICATIONS=true
```

---

## Usage Methods

### Method 1: Command-Line Interface (Recommended)

#### Interactive Mode (Chat with Agent)
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Using module syntax
python -m agents.airflow_intelligence.cli interactive

# Using standalone script
./run_agent.py interactive

# Example session:
# You: What DAGs failed in the last 24 hours?
# Agent: Let me investigate... [autonomous reasoning]
# Agent: I found 3 failed DAGs: ...
#
# You: Why did the first one fail?
# Agent: [investigates] The etl_daily failed due to...
```

#### Mission Mode (Single Objective)
```bash
# Execute a specific objective
python -m agents.airflow_intelligence.cli mission "Find performance anomalies"

# With verbose output (show reasoning)
python -m agents.airflow_intelligence.cli mission "Investigate slow pipelines" --verbose

# Examples:
python -m agents.airflow_intelligence.cli mission "Find all failed DAGs in last 24 hours"
python -m agents.airflow_intelligence.cli mission "Check health of etl_daily pipeline"
python -m agents.airflow_intelligence.cli mission "Generate report and send to Slack"
```

#### Report Mode (Automated Monitoring)
```bash
# Generate comprehensive health report
python -m agents.airflow_intelligence.cli report

# Generate report without Slack notification
python -m agents.airflow_intelligence.cli report --no-slack
```

#### Test Mode (Verify Setup)
```bash
# Run system tests
python -m agents.airflow_intelligence.cli test

# Tests:
# ✓ Configuration validation
# ✓ Database connectivity
# ✓ Agent reasoning
```

#### Config Mode (View Settings)
```bash
# Display current configuration
python -m agents.airflow_intelligence.cli config
```

---

### Method 2: Python API

#### Basic Usage
```python
from agents.airflow_intelligence import create_orchestrator

# Create orchestrator (loads from .env)
orchestrator = create_orchestrator()

# Execute a mission
result = orchestrator.execute_mission(
    objective="Find performance issues in last 24 hours"
)

print(result["response"])
```

#### Advanced Usage
```python
from agents.airflow_intelligence import AgentConfig, AgentOrchestrator

# Custom configuration
config = AgentConfig(
    airflow_db_url="postgresql://...",
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_region="eu-west-1",
    temperature=0.3,
    enable_slack=True,
    slack_token="xoxb-...",
    anomaly_multiplier=1.5
)

# Create orchestrator
orchestrator = AgentOrchestrator(config)

# Mission with details
result = orchestrator.execute_mission(
    objective="Investigate etl_daily pipeline performance",
    show_reasoning=True,
    return_details=True
)

print(f"Success: {result['success']}")
print(f"Tools used: {len(result['tools_used'])}")
print(f"Iterations: {result['iterations']}")
print(f"Response: {result['response']}")
```

#### Interactive Mode
```python
orchestrator = create_orchestrator()
orchestrator.interactive_mode()
# Starts chat session
```

#### Automated Report
```python
orchestrator = create_orchestrator()
result = orchestrator.generate_report()
print(result["response"])
```

---

### Method 3: Scheduled Jobs (Cron)

#### Virtual Environment in Cron

When setting up cron jobs, make sure to activate the virtual environment:

```bash
# Hourly health report
0 * * * * cd /path/to/myaiproject && source .venv/bin/activate && python -m agents.airflow_intelligence.cli report >> /var/log/airflow-agent.log 2>&1

# Every 6 hours with verbose logging
0 */6 * * * cd /path/to/myaiproject && source .venv/bin/activate && python -m agents.airflow_intelligence.cli report --verbose >> /var/log/airflow-agent.log 2>&1

# Daily summary at 9 AM
0 9 * * * cd /path/to/myaiproject && source .venv/bin/activate && python -m agents.airflow_intelligence.cli mission "Generate daily summary and send to Slack" >> /var/log/airflow-agent.log 2>&1

# Performance check every 30 minutes
*/30 * * * * cd /path/to/myaiproject && source .venv/bin/activate && python -m agents.airflow_intelligence.cli mission "Check for performance anomalies" >> /var/log/airflow-agent.log 2>&1
```

**Alternative: Use absolute path to Python**
```bash
# Find your venv python path
which python  # while venv is activated

# Use in cron (example)
0 * * * * /path/to/myaiproject/.venv/bin/python -m agents.airflow_intelligence.cli report >> /var/log/airflow-agent.log 2>&1
```

---

## Dependency Management with uv

### Install Specific Packages

```bash
# Install a single package
uv pip install pandas

# Install with specific version
uv pip install sqlalchemy==2.0.0

# Install development dependencies
uv pip install pytest pytest-cov black isort
```

### Update Dependencies

```bash
# Update all packages
uv pip install --upgrade -r requirements.txt

# Update specific package
uv pip install --upgrade boto3
```

### List Installed Packages

```bash
# List all installed packages
uv pip list

# Show package details
uv pip show sqlalchemy
```

### Create Requirements File

```bash
# Generate from current environment
uv pip freeze > requirements-lock.txt
```

---

## Example Objectives

### Performance Monitoring
- "Find slow running pipelines in the last 24 hours"
- "Identify performance anomalies and send report to Slack"
- "Investigate why etl_daily is taking longer than usual"
- "Check for any DAGs running more than 2x their baseline"

### Failure Investigation
- "What DAGs failed in the last 24 hours?"
- "Investigate the cause of ml_training pipeline failures"
- "Find all failed DAGs and summarize the issues"
- "Check if any pipelines are consistently failing"

### Health Monitoring
- "Give me a health summary of all pipelines"
- "Check the overall system health and alert if critical"
- "Find any stale or inactive DAGs"
- "Assess the health of data pipelines"

### Specific Investigation
- "Drill into the etl_daily pipeline and find bottlenecks"
- "Analyze task-level performance for slow_pipeline"
- "Compare today's performance vs last week's baseline"
- "Find which task in data_processing is taking the most time"

---

## Output Examples

### Interactive Session
```
You: Find slow pipelines

🤔 Agent thinking (iteration 1/10)...
🔧 Agent decided to use tools...
   📞 Calling: query_dag_runs
      Parameters: {"window_hours": 24}
      ✅ Success: 50 results

🤔 Agent thinking (iteration 2/10)...
🔧 Agent decided to use tools...
   📞 Calling: analyze_performance_baseline
      Parameters: {"days": 14}
      ✅ Success: 45 results

🤔 Agent thinking (iteration 3/10)...
🔧 Agent decided to use tools...
   📞 Calling: detect_anomalies
      Parameters: {"sensitivity": "medium"}
      ✅ Success: 3 results

✅ Agent reached conclusion after 3 iterations
🛠️  Tools used: 3

🤖 Agent:
I found 3 slow pipelines that are running significantly above their baseline:

**1. etl_daily** - 4.2 hours vs 1.5h baseline (2.8x deviation)
   - Root cause: Transform task taking 3.5 hours (87% of runtime)
   - Confidence: 92% (based on 28 historical runs)

**2. ml_training** - 2.8 hours vs 1.2h baseline (2.3x deviation)
   - Root cause: Model training step with increased data volume
   - Confidence: 88%

**3. api_sync** - 45 minutes vs 20min baseline (2.25x deviation)
   - Root cause: External API latency spike
   - Confidence: 85%

**Recommendations:**
1. etl_daily: Increase memory allocation for transform task
2. ml_training: Implement data sampling or distributed training
3. api_sync: Add timeout and retry logic for API calls

Would you like me to send this analysis to Slack?
```

---

## Troubleshooting

### Virtual Environment Issues

**Error:** `ModuleNotFoundError: No module named 'agents'`

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r agents/airflow_intelligence/requirements.txt

# Verify installation
python -c "import agents.airflow_intelligence; print('✓ Import successful')"
```

---

**Error:** `uv: command not found`

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv

# Verify installation
uv --version
```

---

### Connection Errors

**Error:** `Configuration validation failed: AIRFLOW_DB_URL is required`

**Solution:**
- Ensure `.env` file exists in the correct location
- Check `AIRFLOW_DB_URL` is set correctly
- Format: `postgresql://user:password@host:port/database`

---

**Error:** `Failed to initialize database connection`

**Solution:**
- Verify database is accessible
- Check credentials
- Test connection: `psql $AIRFLOW_DB_URL`

---

### AWS Bedrock Errors

**Error:** `AWS credentials not configured`

**Solution:**
- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
- Or use IAM role (if running on AWS)
- Or configure AWS CLI: `aws configure`

---

**Error:** `Model not found: anthropic.claude...`

**Solution:**
- Check `MODEL_ID` in `.env`
- Current model: `global.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Verify model is available in your region
- Request model access in AWS Console if needed

---

### Slack Errors

**Error:** `Slack not configured`

**Solution:**
- This is a warning, not an error (Slack is optional)
- To enable: Set `SLACK_BOT_TOKEN` and `ENABLE_SLACK_NOTIFICATIONS=true`

---

## Best Practices

### 1. Always Use Virtual Environment
```bash
# Create once
uv venv

# Activate for each session
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Verify
which python  # Should show .venv path
```

### 2. Keep Dependencies Updated
```bash
# Update all packages
uv pip install --upgrade -r requirements.txt

# Check for outdated packages
uv pip list --outdated
```

### 3. Use uv for Speed
```bash
# uv is much faster than pip
time uv pip install -r requirements.txt
# vs
time pip install -r requirements.txt

# uv can be 10-100x faster!
```

### 4. Start with Test Mode
```bash
python -m agents.airflow_intelligence.cli test
```
Verify everything is configured correctly before running missions.

### 5. Use Interactive Mode for Exploration
Interactive mode is best for:
- Learning what the agent can do
- Investigating specific issues
- Asking follow-up questions

### 6. Use Mission Mode for Automation
Mission mode is best for:
- Scheduled jobs
- Specific objectives
- CI/CD integration

---

## Advanced Topics

### Custom Virtual Environment Location

```bash
# Create venv in custom location
uv venv /path/to/custom/.venv

# Activate
source /path/to/custom/.venv/bin/activate
```

### Multiple Python Versions

```bash
# Create venv with specific Python version
uv venv --python 3.11

# Or specify full path
uv venv --python /usr/bin/python3.10
```

### Development Setup

```bash
# Install with development dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install pytest pytest-cov black isort mypy

# Run tests
pytest tests/

# Format code
black agents/airflow_intelligence/
isort agents/airflow_intelligence/
```

---

## Integration Examples

### Flask API
```python
from flask import Flask, request, jsonify
from agents.airflow_intelligence import create_orchestrator

app = Flask(__name__)
orchestrator = create_orchestrator()

@app.route('/investigate', methods=['POST'])
def investigate():
    objective = request.json.get('objective')
    result = orchestrator.execute_mission(objective)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### Airflow DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from agents.airflow_intelligence import create_orchestrator

def run_monitoring():
    orchestrator = create_orchestrator()
    result = orchestrator.generate_report()
    return result

with DAG('airflow_monitoring', schedule_interval='@hourly') as dag:
    monitor = PythonOperator(
        task_id='run_intelligence_agent',
        python_callable=run_monitoring
    )
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY agents/airflow_intelligence/requirements.txt .

# Create venv and install dependencies with uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy agent code
COPY agents/ agents/
COPY run_agent.py .

# Activate venv and run
CMD [".venv/bin/python", "-m", "agents.airflow_intelligence.cli", "report"]
```

---

## Support

For issues or questions:
1. Check logs: `~/.airflow_intelligence/logs/`
2. Review configuration: `python -m agents.airflow_intelligence.cli config`
3. Run tests: `python -m agents.airflow_intelligence.cli test`
4. Enable debug mode: `--debug` flag

---

## Quick Reference Card

```bash
# Setup (one time)
uv venv
source .venv/bin/activate
uv pip install -r agents/airflow_intelligence/requirements.txt

# Daily usage
source .venv/bin/activate  # Activate venv

# Commands
python -m agents.airflow_intelligence.cli interactive  # Chat
python -m agents.airflow_intelligence.cli mission "..."  # Objective
python -m agents.airflow_intelligence.cli report        # Report
python -m agents.airflow_intelligence.cli test          # Test

# Updates
uv pip install --upgrade -r requirements.txt
```

---

**Happy monitoring with AI! 🤖🚀**

**Built with:**
- ⚡ uv - Ultra-fast Python package installer
- 🤖 Claude AI (Sonnet 4.5)
- 🔧 Python 3.8+
- 🗄️ PostgreSQL
- 💬 Slack SDK
- 🎨 Rich terminal UI
