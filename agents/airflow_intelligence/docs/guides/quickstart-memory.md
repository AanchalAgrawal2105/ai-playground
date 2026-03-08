# 🚀 Quick Start: Testing Your Agent's New Memory

## ⚡ 1-Minute Test

### Step 1: Test Memory System
```bash
python agents/airflow_intelligence/test_memory_integration.py
```

**Expected output:**
```
🧠 Testing Agent Memory System (Phase 1)
✅ Memory initialized
✅ Stored incident: etl_daily_20260305_123456
✅ Found 2 past incidents
✅ Memory System Test Complete!
```

---

### Step 2: Test with Real Agent

```bash
python -m agents.airflow_intelligence.cli chat
```

**Try this conversation:**

```
You: Find any failed DAGs in the last 24 hours and store the incidents in memory

Agent: Let me investigate...
[Agent will query DAGs, analyze failures, and STORE them in memory]

You: What incidents do you remember about [dag_id]?

Agent: Let me check my memory...
[Agent will RECALL stored incidents and tell you what it remembers!]
```

---

## 🧪 3 Quick Tests to See Memory in Action

### Test 1: Store and Recall

**Session 1:**
```
You: Investigate performance of etl_daily and store the incident
```

**Session 2 (NEW terminal):**
```
You: What do you remember about etl_daily?

Agent: "I have institutional knowledge about this DAG:
- I've investigated this 1 time before
- Root cause was: [previous finding]
- Last incident: [date]"
```

✅ **Memory working!**

---

### Test 2: Pattern Recognition

Run same investigation 3 times:
```
You: Investigate etl_daily performance and store findings
```

Then ask:
```
You: What patterns do you see in etl_daily?

Agent: "This DAG has recurring issues:
- Same root cause 3 times
- Incidents are becoming more frequent"
```

✅ **Pattern detection working!**

---

### Test 3: Smarter Recommendations

After building memory:
```
You: Investigate etl_daily again

Agent: "Let me check my memory first...
I've seen this 3 times before. Root cause is always Spark memory.
Based on historical patterns, I recommend [data-backed suggestion]"
```

✅ **Learning from history!**

---

## 📁 Check Memory Files

```bash
# View stored incidents
cat .agent_memory/incidents.jsonl | jq .

# Count total incidents
wc -l .agent_memory/incidents.jsonl

# Find specific DAG
grep "etl_daily" .agent_memory/incidents.jsonl | jq .
```

---

## 🎯 What to Look For

### Agent Should Now:

1. **Before Investigation:**
   - ✅ Say "Let me check my memory first..."
   - ✅ Call `recall_historical_context()`
   - ✅ Reference past incidents

2. **During Analysis:**
   - ✅ Compare to historical patterns
   - ✅ Mention "I've seen this X times before"
   - ✅ Reference previous root causes

3. **After Investigation:**
   - ✅ Call `store_incident()`
   - ✅ Say "Storing in memory for future reference"
   - ✅ Actually save to `.agent_memory/`

---

## ⚠️ Troubleshooting

### Memory not recalling?
```bash
# Check if directory exists
ls -la .agent_memory/

# If not, create it
mkdir .agent_memory
```

### Agent not using memory tools?
The system prompt instructs it to, but you can explicitly ask:
```
"Check your memory for past incidents about etl_daily"
```

### Want to reset memory?
```bash
rm -rf .agent_memory/
```

---

## 📊 Success Indicators

✅ **Working Correctly If:**
- Agent mentions checking memory
- Agent references past incidents
- `.agent_memory/` directory contains files
- Agent gets smarter over multiple sessions

❌ **Not Working If:**
- Agent never mentions memory
- No `.agent_memory/` directory created
- Same investigation repeated without context

---

## 💡 Pro Tips

1. **Build up memory:** Run 5-10 investigations to populate memory
2. **Test across sessions:** Close terminal, reopen, agent should still remember
3. **Check files:** Verify `.agent_memory/incidents.jsonl` is growing
4. **Compare responses:** Same question should get smarter answers over time

---

## 🎉 Success!

If the agent:
- ✅ Recalls past incidents
- ✅ References historical patterns
- ✅ Stores new findings
- ✅ Provides context-aware analysis

**Then Phase 1 is working perfectly!** 🚀

---

**Next:** Ready for Phase 2 (Proactive Monitoring)? The agent will run continuously and autonomously decide when to investigate!
