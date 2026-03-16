# 🔍 Failure Pattern Analysis Enhancement

**Status:** ✅ Implemented
**Build:** Phase 1.1 - Memory Enhancement
**Impact:** ⭐⭐⭐⭐⭐ Critical for production monitoring

---

## 🎯 What Was Added

### New Capability: Sophisticated Chronic Failure Detection

Your agent can now distinguish between:
- ❌ **One-off failures** (isolated incidents)
- ⚠️ **Chronic failures** (systematic, recurring problems)

This is critical for prioritizing which DAGs need urgent attention!

---

## 📊 How It Works

### For Daily DAGs (runs every day)
**Analysis Window:** Last 7 days

**Chronic Failure Criteria:**
- 3 or more failures in 7 days
- Failure rate > 40%

**Example:**
```
etl_daily:
- Ran 7 times in last 7 days
- Failed 5 times
- Failure rate: 71%
- Status: ⚠️ CHRONIC FAILURE
- Severity: CRITICAL
```

---

### For Weekly/Monthly DAGs (runs less frequently)
**Analysis Window:** Last 3 runs

**Chronic Failure Criteria:**
- All 3 consecutive runs failed

**Example:**
```
weekly_report:
- Last 3 runs analyzed
- Failed 3 times (100%)
- Status: ⚠️ CHRONIC FAILURE
- Severity: CRITICAL
- Message: "DAG is completely broken"
```

---

## 🛠️ New Tool: `analyze_failure_patterns`

### Tool Specification

```python
{
    "name": "analyze_failure_patterns",
    "description": "Analyze failure patterns based on DAG schedule",
    "parameters": {
        "dag_id": "DAG identifier",
        "schedule_type": "daily | weekly | monthly"
    }
}
```

### Usage Examples

#### Example 1: Daily DAG
```python
analyze_failure_patterns(
    dag_id="etl_daily",
    schedule_type="daily"
)
```

**Returns:**
```json
{
    "dag_id": "etl_daily",
    "schedule_type": "daily",
    "analysis_window": "Last 7 days",
    "is_chronic_failure": true,
    "failure_count": 5,
    "failure_rate": 71.4,
    "consecutive_failures": 3,
    "severity": "critical",
    "recommendation": "URGENT: DAG is chronically failing (5 failures in 7 days). Immediate investigation required.",
    "recent_incidents": [...]
}
```

#### Example 2: Weekly DAG
```python
analyze_failure_patterns(
    dag_id="weekly_report",
    schedule_type="weekly"
)
```

**Returns:**
```json
{
    "dag_id": "weekly_report",
    "schedule_type": "weekly",
    "analysis_window": "Last 3 runs",
    "is_chronic_failure": true,
    "failure_count": 3,
    "failure_rate": 100.0,
    "consecutive_failures": 3,
    "severity": "critical",
    "recommendation": "CRITICAL: All 3 consecutive runs failed. DAG is completely broken. Immediate action required.",
    "recent_incidents": [...]
}
```

---

## 🤖 How Agent Uses It

### Before (No Pattern Analysis)
```
Agent: "Found 10 failed DAGs. All need investigation."
[No prioritization - wastes time on one-off failures]
```

### After (With Pattern Analysis)
```
Agent: "Found 10 failed DAGs. Let me analyze which are chronically failing...
*calls analyze_failure_patterns for each*

Priority breakdown:
1. CRITICAL (2 DAGs): Chronically failing - URGENT
2. HIGH (3 DAGs): Multiple failures - investigate soon
3. MEDIUM (5 DAGs): One-off failures - monitor

Focusing on critical DAGs first..."
```

---

## 📈 Severity Levels

| Severity | Daily DAGs | Weekly/Monthly DAGs | Action |
|----------|------------|---------------------|---------|
| **CRITICAL** | 5+ failures in 7 days | 3/3 consecutive failures | URGENT - Immediate action |
| **HIGH** | 3-4 failures in 7 days | 2/3 consecutive failures | High priority - Investigate soon |
| **MEDIUM** | 2 failures in 7 days | 1/3 consecutive failures | Monitor - Track pattern |
| **LOW** | 0-1 failures in 7 days | 0/3 consecutive failures | No action needed |

---

## 🔄 Integration Points

### 1. Memory System (`memory.py`)
✅ Added `analyze_failure_patterns()` method
✅ Added `_analyze_daily_failures()` for daily DAGs
✅ Added `_analyze_consecutive_failures()` for weekly/monthly DAGs
✅ Added `_count_consecutive_failures()` helper

### 2. Agent Tools (`agent.py`)
✅ Added `analyze_failure_patterns` tool
✅ Updated system prompt with chronic failure detection workflow
✅ Added examples of when to use the tool
✅ Updated `send_health_report` description

### 3. Orchestrator (`orchestrator.py`)
✅ Added execution logic for `analyze_failure_patterns`

---

## 🧪 Testing

### Test 1: Manual Test Script

```python
from agents.airflow_intelligence.memory import AgentMemory
from datetime import datetime, timedelta

memory = AgentMemory()

# Simulate daily DAG with chronic failures
for i in range(5):
    memory.store_incident(
        dag_id="etl_daily",
        issue_type="failure",
        root_cause="Database connection timeout",
        severity="high"
    )

# Analyze
result = memory.analyze_failure_patterns("etl_daily", "daily")
print(f"Is chronic? {result['is_chronic_failure']}")
print(f"Failures: {result['failure_count']}")
print(f"Severity: {result['severity']}")
```

### Test 2: Agent Conversation

```bash
python -m agents.airflow_intelligence.cli chat
```

**Ask:**
```
"Find all failed DAGs and identify which ones are chronically failing"
```

**Expected Agent Behavior:**
1. Queries for failed DAGs
2. For each failed DAG, calls `analyze_failure_patterns()`
3. Identifies which are chronic vs. one-off failures
4. Prioritizes chronic failures
5. Provides severity-based recommendations

---

## 📊 Example Agent Output

```
User: "Find chronically failing DAGs"

Agent: Let me investigate failed DAGs and analyze their patterns...

*calls query_dag_runs(state='failed')*
Found 8 DAGs with failures in the last 24 hours.

*calls analyze_failure_patterns() for each*

CHRONIC FAILURE ANALYSIS:

🔴 CRITICAL (2 DAGs - URGENT):
1. etl_daily
   - Type: Daily DAG
   - Failures: 5 of 7 runs (71%)
   - Pattern: Recurring database timeout
   - Action: IMMEDIATE investigation required

2. weekly_aggregation
   - Type: Weekly DAG
   - Failures: 3 of 3 consecutive runs (100%)
   - Pattern: DAG completely broken
   - Action: Fix before next run

⚠️ HIGH PRIORITY (2 DAGs):
3. data_validation
   - Failures: 3 of 7 runs (43%)
   - Action: Investigate soon

4. customer_export
   - Failures: 2 of 3 runs (67%)
   - Action: High priority

ℹ️ MEDIUM (4 DAGs - Monitor):
[One-off failures, monitor for patterns]

RECOMMENDATION:
Focus on etl_daily and weekly_aggregation IMMEDIATELY.
These are systematically failing and blocking production.
```

---

## 💡 Key Benefits

### 1. Smart Prioritization
✅ Focus on DAGs that are truly broken
❌ Don't waste time on one-off failures

### 2. Context-Aware Alerting
✅ Alert only on chronic failures
❌ Reduce alert fatigue

### 3. Better Recommendations
✅ "This DAG has failed 5 times in 7 days - urgent"
❌ "This DAG failed once - maybe check it"

### 4. Data-Driven Decisions
✅ 71% failure rate = CRITICAL
❌ "Seems to be failing a lot"

---

## 🎯 Use Cases

### Use Case 1: Daily Health Report
```
Agent generates daily report:
- Uses analyze_failure_patterns() for all failed DAGs
- Separates chronic failures from one-offs
- Prioritizes recommendations
- Sends structured report to Slack
```

### Use Case 2: Incident Investigation
```
User: "Why is production slow?"
Agent:
- Checks recent failures
- Analyzes patterns
- Identifies 2 chronically failing DAGs
- "Root cause: etl_daily failing 5/7 days, blocking downstream"
```

### Use Case 3: Proactive Monitoring
```
Agent runs every 15 minutes:
- Checks for new failures
- Analyzes patterns
- Detects chronic failure emerging
- Alerts before it becomes critical
```

---

## 📝 Files Modified

1. **`agents/airflow_intelligence/memory.py`** (+180 lines)
   - `analyze_failure_patterns()` - Main method
   - `_analyze_daily_failures()` - Daily DAG logic
   - `_analyze_consecutive_failures()` - Weekly/monthly logic
   - `_count_consecutive_failures()` - Helper

2. **`agents/airflow_intelligence/agent.py`** (+25 lines)
   - New tool: `analyze_failure_patterns`
   - System prompt: Added chronic failure detection workflow
   - Updated: `send_health_report` description

3. **`agents/airflow_intelligence/orchestrator.py`** (+8 lines)
   - Added execution logic for new tool

---

## 🚀 What's Next

### Current State ✅
- ✅ Phase 1: Memory Integration
- ✅ Phase 1.1: Failure Pattern Analysis

### Next ⏭️
- 🎯 Phase 2: Proactive Monitoring
- 🎯 Phase 3: Enhanced Planning

---

## 🎊 Success Metrics

Your agent can now:
✅ Detect chronic failures automatically
✅ Distinguish one-off from recurring issues
✅ Prioritize investigations by severity
✅ Provide data-driven recommendations
✅ Reduce alert fatigue
✅ Focus on DAGs that truly need attention

**This is production-ready failure detection!** 🚀

---

## 📚 Additional Documentation

- `PHASE1_COMPLETE.md` - Memory integration details
- `QUICKSTART_MEMORY.md` - Quick testing guide
- `AGENTIC_ENHANCEMENTS.md` - Full enhancement roadmap

---

**Questions?** Test it out and see the agent automatically detect chronic failures!
