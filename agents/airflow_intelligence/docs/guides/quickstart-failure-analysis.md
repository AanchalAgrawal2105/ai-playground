# 🚀 Quick Start: Failure Pattern Analysis

## ⚡ 30-Second Test

```bash
# Test the failure pattern analysis
python agents/airflow_intelligence/test_failure_pattern_analysis.py
```

**Expected output:**
```
✅ Test 1: Chronic failure detected (5 failures in 7 days)
✅ Test 2: Not chronic (2 failures in 7 days)
✅ Test 3: Weekly chronic failure (3/3 consecutive)
✅ Test 4: Not chronic (2/3 failures)
✅ Test 5: No false positives with empty history
✅ Test 6: Complex multi-DAG scenario
✅ ALL TESTS PASSED!
```

---

## 🤖 Test with Agent

```bash
python -m agents.airflow_intelligence.cli chat
```

**Try these commands:**

### Command 1: Find Chronic Failures
```
"Find all chronically failing DAGs and prioritize them by severity"
```

**Agent will:**
1. Query failed DAGs
2. Call `analyze_failure_patterns()` for each
3. Identify chronic vs. one-off failures
4. Prioritize by severity
5. Provide actionable recommendations

### Command 2: Analyze Specific DAG
```
"Analyze failure patterns for etl_daily"
```

**Agent will:**
1. Call `analyze_failure_patterns(dag_id="etl_daily", schedule_type="daily")`
2. Tell you if it's chronically failing
3. Provide historical context
4. Suggest actions

### Command 3: Health Report with Failure Analysis
```
"Generate a comprehensive health report including chronic failure analysis"
```

**Agent will:**
1. Get system health overview
2. Analyze each failing DAG for patterns
3. Identify chronic failures
4. Send beautifully formatted report to Slack

---

## 📊 What Agent Now Detects

### Daily DAGs (runs every day)
- ✅ **Chronic if:** 3+ failures in 7 days
- ⚠️ **Critical if:** 5+ failures in 7 days

**Example:**
```
etl_daily:
  Failures: 5 of 7 runs (71% failure rate)
  Status: ⚠️ CHRONIC FAILURE
  Severity: CRITICAL
  Action: URGENT - Immediate investigation required
```

### Weekly/Monthly DAGs (runs less frequently)
- ✅ **Chronic if:** All 3 consecutive runs failed
- ⚠️ **Critical if:** 3/3 failures (100%)

**Example:**
```
weekly_report:
  Failures: 3 of 3 runs (100% failure rate)
  Status: ⚠️ CHRONIC FAILURE
  Severity: CRITICAL
  Action: DAG is completely broken - Fix immediately
```

---

## 🔍 How to Use Each Schedule Type

### Daily DAG
```
analyze_failure_patterns(dag_id="etl_daily", schedule_type="daily")
```
**Analyzes:** Last 7 days
**Use for:** DAGs that run daily or multiple times per day

### Weekly DAG
```
analyze_failure_patterns(dag_id="weekly_summary", schedule_type="weekly")
```
**Analyzes:** Last 3 runs
**Use for:** DAGs that run weekly

### Monthly DAG
```
analyze_failure_patterns(dag_id="monthly_report", schedule_type="monthly")
```
**Analyzes:** Last 3 runs
**Use for:** DAGs that run monthly

---

## 💡 Real-World Examples

### Example 1: Production Incident
```
You: "We have production issues. Find what's breaking."

Agent: Analyzing all failures...
*calls analyze_failure_patterns() for each failed DAG*

🔴 CRITICAL - Immediate Action Required:
1. etl_production: 6 failures in 7 days (86% failure rate)
   Root cause pattern: Network timeout (recurring)
   Action: URGENT investigation needed

2. weekly_summary: 3/3 consecutive runs failed (100%)
   Root cause pattern: Report template broken
   Action: Fix before next scheduled run

⚠️ High Priority:
3. data_sync: 3 failures in 7 days (43%)
   Action: Investigate this week

Recommendation: Focus on etl_production first - it's blocking production daily.
```

### Example 2: Daily Health Report
```
Agent (running proactively at 9am):

Daily Health Report - March 5, 2026

Overall Health: 85%
Active DAGs: 47

🔴 CHRONIC FAILURES (2 DAGs):
- etl_daily: 5/7 failures - URGENT
- api_sync: 4/7 failures - HIGH PRIORITY

✅ HEALTHY DAGS: 43
⚠️ MINOR ISSUES: 2 (one-off failures)

Action Required: Investigate chronic failures today.
```

---

## 📈 Severity Guide

| Failures | Daily DAG | Weekly/Monthly | Severity | Action |
|----------|-----------|----------------|----------|--------|
| 5+ in 7 days | 71%+ fail rate | - | CRITICAL | URGENT |
| 3-4 in 7 days | 43-57% fail rate | - | HIGH | Soon |
| - | - | 3/3 consecutive | CRITICAL | URGENT |
| - | - | 2/3 consecutive | HIGH | Soon |
| 2 in 7 days | 29% fail rate | 1/3 consecutive | MEDIUM | Monitor |
| 0-1 in 7 days | <14% fail rate | 0/3 consecutive | LOW | No action |

---

## 🎯 Key Benefits

### Before
```
❌ "10 DAGs failed. All need investigation."
❌ No prioritization
❌ Wasted time on one-off failures
❌ Missed systematic issues
```

### After
```
✅ "2 DAGs are chronically failing (URGENT)"
✅ "3 DAGs have high priority issues (investigate soon)"
✅ "5 DAGs had one-off failures (monitor)"
✅ Smart prioritization based on data
```

---

## 🧪 Quick Verification

### 1. Check memory has the method
```bash
grep -n "analyze_failure_patterns" agents/airflow_intelligence/memory.py
```
Expected: Should show method definition

### 2. Check agent has the tool
```bash
grep -n "analyze_failure_patterns" agents/airflow_intelligence/agent.py
```
Expected: Should show tool definition

### 3. Check orchestrator has execution logic
```bash
grep -n "analyze_failure_patterns" agents/airflow_intelligence/orchestrator.py
```
Expected: Should show execution logic

---

## 🐛 Troubleshooting

### Agent not using the tool?
Explicitly ask:
```
"Use analyze_failure_patterns to check if etl_daily is chronically failing"
```

### No incidents in memory?
First store some:
```
"Find failed DAGs and store the incidents in memory"
```

### Want to test with fake data?
Run the test script:
```bash
python agents/airflow_intelligence/test_failure_pattern_analysis.py
```

---

## 📚 Related Documentation

- **FAILURE_PATTERN_ANALYSIS.md** - Full technical documentation
- **PHASE1_COMPLETE.md** - Memory system details
- **AGENTIC_ENHANCEMENTS.md** - Full enhancement roadmap

---

## 🎊 Success Indicators

✅ **Working correctly if:**
- Agent mentions "chronic failure" in analysis
- Agent calls `analyze_failure_patterns()` automatically
- Agent prioritizes DAGs by severity
- Agent distinguishes one-off from recurring failures

---

## 🚀 Next Steps

1. ✅ Test the analysis: `python test_failure_pattern_analysis.py`
2. ✅ Try with agent: Ask about chronic failures
3. ✅ Build up memory: Store real incidents
4. ✅ Watch agent get smarter!

**Ready for Phase 2 (Proactive Monitoring)?** The agent will run continuously and use this analysis automatically! 😊
