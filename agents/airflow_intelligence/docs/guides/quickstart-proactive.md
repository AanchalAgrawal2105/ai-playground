# 🚀 Phase 2: Proactive Monitoring - Quick Start

## ⚡ 30-Second Start

```bash
# Run proactive monitoring
python -m agents.airflow_intelligence.cli proactive
```

That's it! The agent will now run continuously and autonomously monitor your Airflow instance.

---

## 🎯 What It Does

The agent runs every 15 minutes and:
1. ✅ Checks system health
2. ✅ Investigates if issues found
3. ✅ Uses memory to detect patterns
4. ✅ Analyzes failure patterns (7-day for daily DAGs, 3-run for weekly/monthly)
5. ✅ Decides autonomously if alert needed
6. ✅ Sends structured report to Slack (if critical)
7. ✅ Stores findings in memory
8. ✅ Repeats forever

**No human intervention needed!**

---

## 🔧 Configuration

### Change Check Interval

```bash
# Check every 5 minutes
python -m agents.airflow_intelligence.cli proactive --interval 5

# Check every 30 minutes
python -m agents.airflow_intelligence.cli proactive --interval 30

# Check every hour
python -m agents.airflow_intelligence.cli proactive --interval 60
```

---

## 🛑 Stop the Agent

Press `Ctrl+C` - the agent will shutdown gracefully and show a summary.

---

## 📊 What You'll See

```
================================================================================
🤖 PROACTIVE AGENT MODE - Autonomous Monitoring
================================================================================
✅ Agent will check system every 15 minutes
✅ Agent will decide autonomously when to investigate and alert
✅ Press Ctrl+C to stop gracefully
================================================================================

🔄 Running initial health check...

================================================================================
🔍 Proactive Check #1 @ 2026-03-05 17:30:00 UTC
================================================================================

🤔 Agent thinking...
🔧 Agent using tools...
   📞 Calling: get_dag_health_summary
   📞 Calling: query_dag_runs
   📞 Calling: analyze_failure_patterns

✅ Check complete

⏰ Next check at 17:45:00 UTC
```

---

## 🎯 When Agent Alerts

Agent will send Slack alert if it finds:
- ⚠️ Health dropped >10%
- ⚠️ Chronic failures (3+ in 7 days for daily DAGs)
- ⚠️ Critical pipelines failing (3/3 consecutive for weekly/monthly)
- ⚠️ New failure patterns

Agent WON'T alert for:
- ✅ Minor one-off failures
- ✅ Health >95%
- ✅ Already known issues with no changes

**Smart alerting = No alert fatigue!**

---

## 🐛 Troubleshooting

### Not Starting?
```bash
# Check configuration
python -m agents.airflow_intelligence.cli test

# Check logs
python -m agents.airflow_intelligence.cli proactive --debug
```

### Agent Not Finding Issues?
The system might be healthy! That's good.

Check manually:
```bash
python -m agents.airflow_intelligence.cli mission "Check system health"
```

---

## 🎓 How It's Different

### Before (Phase 1 - Reactive)
```
You: "Check pipelines"
Agent: [investigates]
Agent: "Here's the report"
```

### After (Phase 2 - Proactive)
```
[Agent runs continuously]
Agent: "I found 2 chronic failures - alerting team"
[15 minutes later]
Agent: "Checking again... all good now"
[Continues forever...]
```

---

## 📚 More Info

- **Full Guide:** `PHASE2_COMPLETE.md`
- **Deployment:** `PHASE2_DEPLOYMENT.md`
- **Phase 1:** `PHASE1_COMPLETE.md`

---

## 🎉 You're Done!

Your agent is now running autonomously 24/7, making intelligent decisions about what to investigate and when to alert.

**This is TRUE autonomous AI!** 🚀

---

**Stop it:** Press Ctrl+C
**Change interval:** Use `--interval N`
**Debug:** Add `--debug` flag
