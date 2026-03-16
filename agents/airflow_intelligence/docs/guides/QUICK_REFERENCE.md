# 📋 Quick Reference - Failure Pattern Analysis

## ⚡ Quick Test (30 seconds)

```bash
python agents/airflow_intelligence/test_failure_pattern_analysis.py
```

---

## 🎯 What It Does

### Daily DAGs
- Analyzes **last 7 days**
- Chronic if **3+ failures**
- Critical if **5+ failures**

### Weekly/Monthly DAGs
- Analyzes **last 3 runs**
- Chronic if **all 3 failed**
- Critical if **100% failure**

---

## 🛠️ New Tool

```python
analyze_failure_patterns(
    dag_id="etl_daily",
    schedule_type="daily"  # or "weekly" or "monthly"
)
```

**Returns:**
- `is_chronic_failure`: Boolean
- `failure_count`: Number of failures
- `failure_rate`: Percentage
- `severity`: low/medium/high/critical
- `recommendation`: Action to take

---

## 💬 Use with Agent

```bash
python -m agents.airflow_intelligence.cli chat
```

**Ask:**
- "Find chronically failing DAGs"
- "Analyze failure patterns for etl_daily"
- "Generate health report with chronic failure analysis"

---

## 📊 Severity Levels

| Level | Daily | Weekly/Monthly | Action |
|-------|-------|---------------|--------|
| CRITICAL | 5+ in 7d | 3/3 consecutive | URGENT |
| HIGH | 3-4 in 7d | 2/3 consecutive | Soon |
| MEDIUM | 2 in 7d | 1/3 consecutive | Monitor |
| LOW | 0-1 in 7d | 0/3 consecutive | None |

---

## 📁 Files Modified

1. `agents/airflow_intelligence/memory.py` (+180 lines)
2. `agents/airflow_intelligence/agent.py` (+40 lines)
3. `agents/airflow_intelligence/orchestrator.py` (+8 lines)

---

## ✅ Verification

```bash
# Check implementation
grep -n "analyze_failure_patterns" agents/airflow_intelligence/memory.py
grep -n "analyze_failure_patterns" agents/airflow_intelligence/agent.py
grep -n "analyze_failure_patterns" agents/airflow_intelligence/orchestrator.py

# Run tests
python agents/airflow_intelligence/test_failure_pattern_analysis.py
```

---

## 📚 Documentation

- `FAILURE_PATTERN_ANALYSIS.md` - Full details
- `QUICKSTART_FAILURE_ANALYSIS.md` - Quick start
- `IMPLEMENTATION_SUMMARY.md` - Complete summary
- `test_failure_pattern_analysis.py` - Test suite

---

## 🎉 What You Got

✅ 7-day analysis for daily DAGs
✅ 3-run analysis for weekly/monthly DAGs
✅ Chronic failure detection
✅ Severity prioritization
✅ Smart recommendations
✅ Full test coverage
✅ Complete documentation

**Status:** Production Ready 🚀
