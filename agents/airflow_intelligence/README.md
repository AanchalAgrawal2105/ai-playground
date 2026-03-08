# 🤖 Airflow Intelligence Agent

An autonomous AI agent for intelligent Airflow pipeline monitoring, anomaly detection, and optimization recommendations.

## 🎯 What Makes This "Agentic"?

Unlike traditional monitoring systems, this agent:

- **🧠 Autonomous Reasoning**: Decides what to investigate based on objectives
- **🔄 Multi-Step Planning**: Chains multiple tools strategically to solve problems
- **💬 Interactive**: Have conversations, ask follow-up questions
- **🎯 Goal-Oriented**: Works towards objectives with minimal human guidance
- **📊 Context-Aware**: Maintains memory across interactions

## 🚀 Quick Start

### Installation

```bash
# Install uv (ultra-fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies (much faster than pip!)
uv pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

### Usage

#### Interactive Mode (Chat with the Agent)
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

python -m agents.airflow_intelligence.cli interactive
```

Example conversation:
```
You: What DAGs failed in the last 24 hours?
Agent: Let me check... [investigates autonomously]
Agent: I found 3 failed DAGs: ...

You: Why did the ETL pipeline fail?
Agent: [drills into details] The transform_data task failed due to...
```

#### Mission Mode (Single Objective)
```bash
python -m agents.airflow_intelligence.cli mission \
  --objective "Find performance anomalies and send report to Slack"
```

#### Report Mode (Scheduled Monitoring)
```bash
# For cron jobs
python -m agents.airflow_intelligence.cli report
```

## 🛠️ Architecture

```
User Input
    ↓
Agent Brain (Claude)
    ↓
Tool Selection & Execution
    ↓
├─ Database Tools (query DAGs, get baselines)
├─ Slack Tools (send alerts)
└─ Analysis Tools (detect anomalies, find patterns)
    ↓
Intelligent Analysis
    ↓
Recommendations & Actions
```

## 📚 Available Commands

The agent has access to these tools and decides when to use them:

- `query_dag_runs` - Get recent DAG execution history
- `analyze_performance_baseline` - Calculate historical baselines
- `detect_anomalies` - Run ML-based anomaly detection
- `get_task_breakdown` - Investigate specific DAG run bottlenecks
- `send_slack_alert` - Send formatted alerts to Slack
- `get_dag_health_summary` - Overall system health metrics

## 🧪 Testing

```bash
# Install test dependencies
uv pip install pytest pytest-cov

# Run tests
pytest tests/agents/airflow_intelligence/

# With coverage
pytest tests/agents/airflow_intelligence/ --cov=agents.airflow_intelligence
```

## 📖 Examples

### Example 1: Autonomous Investigation
```python
from agents.airflow_intelligence import AgentOrchestrator, AgentConfig

config = AgentConfig.from_env()
agent = AgentOrchestrator(config)

result = agent.execute_mission(
    "Investigate why my daily ETL pipeline is running slower than usual"
)

# Agent will:
# 1. Query DAG runs for ETL patterns
# 2. Compare to baseline performance
# 3. Identify bottleneck tasks
# 4. Analyze resource patterns
# 5. Provide recommendations
```

### Example 2: Scheduled Health Check
```python
result = agent.execute_mission(
    "Analyze last 24 hours, identify issues, send report to Slack"
)

# Agent autonomously:
# - Gathers relevant data
# - Detects anomalies
# - Formats findings
# - Sends Slack notification
```

## 🔧 Configuration

All configuration is loaded from `.env` file. Copy `.env.example` and fill in your values:

```bash
# Database (Required)
AIRFLOW_DB_URL=postgresql://user:pass@host:5432/airflow

# AWS Bedrock (Required)
AWS_REGION=eu-west-1
MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
AWS_ACCESS_KEY_ID=your_key          # Optional if using IAM role
AWS_SECRET_ACCESS_KEY=your_secret   # Optional if using IAM role
AWS_SESSION_TOKEN=your_token        # Optional

# Slack (Required config, optional token)
SLACK_BOT_TOKEN=xoxb-your-token     # Leave blank if not using Slack
SLACK_CHANNEL=#airflow-alerts
SLACK_USERNAME=Airflow Intelligence Agent
ENABLE_SLACK_NOTIFICATIONS=false

# Agent Behavior (Required)
AGENT_TEMPERATURE=0.3               # 0.0-1.0, higher = more creative
AGENT_MAX_TOKENS=4096              # Max tokens per response
AGENT_MAX_ITERATIONS=10            # Max reasoning loops

# Monitoring Configuration (Required)
WINDOW_HOURS=24                    # Hours to look back for failures
BASELINE_DAYS=14                   # Days for baseline calculation
MIN_HISTORY=10                     # Min runs required for baseline
ANOMALY_MULTIPLIER=1.5             # Duration > baseline * multiplier = anomaly
STALE_DAG_THRESHOLD_DAYS=10        # Days before DAG considered stale

# Performance (Required)
QUERY_TIMEOUT=30                   # Database query timeout (seconds)
MAX_RESULTS=1000                   # Maximum results per query
```

See `.env.example` for detailed descriptions of each variable.

## 🆚 vs MCP Approach

| Feature | MCP Approach | Agent Approach |
|---------|--------------|----------------|
| Workflow | Fixed sequence | Autonomous |
| Tool Selection | Pre-determined | Dynamic |
| Interaction | Batch | Interactive |
| Memory | None | Conversation + Context |
| Problem Solving | Single-step | Multi-step |

## 📈 Roadmap

- [x] Core agent with tool use
- [x] Database tools
- [x] Slack integration
- [x] Anomaly detection
- [ ] Predictive analytics
- [ ] Auto-remediation
- [ ] Web UI
- [ ] Multi-agent collaboration

## 🤝 Contributing

This is a self-contained module. To add features:

1. Add new tools in `tools.py`
2. Register tools in agent's `get_tools()` method
3. Test with interactive mode
4. Write unit tests

## 📄 License

Same as parent project.

---

**Built with ❤️ using Claude AI and AWS Bedrock**
