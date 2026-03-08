# 🧠 Persistent Memory Implementation - Complete Explanation

## 📍 Where Memory is Stored

### File System Location
```
.agent_memory/
├── incidents.jsonl      # All stored incidents (one per line)
├── patterns.jsonl       # Discovered patterns
└── context.json         # Additional context data
```

**Location:** Root directory of your project (`.agent_memory/`)

**Persistence:** Files remain on disk across:
- ✅ Sessions
- ✅ Restarts
- ✅ Days/weeks/months
- ✅ Agent conversations

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   AGENT                              │
│  (Decides when to use memory tools)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                ORCHESTRATOR                          │
│  (Executes memory tool calls)                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              MEMORY MODULE                           │
│  (AgentMemory class)                                 │
│  • store_incident()                                  │
│  • recall_similar_incidents()                        │
│  • analyze_failure_patterns()                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              FILE SYSTEM                             │
│  .agent_memory/incidents.jsonl                       │
│  .agent_memory/patterns.jsonl                        │
│  .agent_memory/context.json                          │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Implementation Details

### 1. Memory Module Location
**File:** `agents/airflow_intelligence/memory.py`

### 2. Key Components

#### A. Initialization (Lines 47-62)
\`\`\`python
class AgentMemory:
    def __init__(self, memory_dir: str = ".agent_memory"):
        """Initialize memory system."""
        # Create directory on disk
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)  # ← Creates .agent_memory/ folder
        
        # Define file paths
        self.incidents_file = self.memory_dir / "incidents.jsonl"
        self.patterns_file = self.memory_dir / "patterns.jsonl"
        self.context_file = self.memory_dir / "context.json"
\`\`\`

**What happens:**
1. Creates `.agent_memory/` directory if it doesn't exist
2. Defines paths to three files (created on first write)

---

#### B. Storage Mechanism - JSONL Format

**Format Used:** JSONL (JSON Lines)
- One JSON object per line
- Append-only (never overwrites)
- Easy to parse line-by-line

**Example: incidents.jsonl**
\`\`\`json
{"id": "etl_daily_20260305_162145", "timestamp": "2026-03-05T16:21:45Z", "dag_id": "etl_daily", "issue_type": "failure", "root_cause": "Database timeout", "severity": "high"}
{"id": "etl_daily_20260305_163021", "timestamp": "2026-03-05T16:30:21Z", "dag_id": "etl_daily", "issue_type": "performance_degradation", "root_cause": "Slow query", "severity": "medium"}
{"id": "api_sync_20260305_164512", "timestamp": "2026-03-05T16:45:12Z", "dag_id": "api_sync", "issue_type": "failure", "root_cause": "API rate limit", "severity": "low"}
\`\`\`

Each line = one incident (never deleted, only appended)

---

#### C. Write Operation (store_incident)

**Code (Lines 64-104):**
\`\`\`python
def store_incident(
    self,
    dag_id: str,
    issue_type: str,
    root_cause: str,
    resolution: Optional[str] = None,
    severity: str = "medium",
    metadata: Optional[Dict] = None
) -> str:
    """Store an incident for future reference."""
    
    # Create unique ID
    incident_id = f"{dag_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Create incident object
    incident = {
        "id": incident_id,
        "timestamp": datetime.utcnow().isoformat(),
        "dag_id": dag_id,
        "issue_type": issue_type,
        "root_cause": root_cause,
        "resolution": resolution,
        "severity": severity,
        "metadata": metadata or {}
    }
    
    # PERSIST TO DISK - This is the key part!
    with open(self.incidents_file, "a") as f:  # ← "a" = append mode
        f.write(json.dumps(incident) + "\n")    # ← Writes JSON + newline
    
    logger.info(f"Stored incident: {incident_id}")
    return incident_id
\`\`\`

**Key Points:**
- Opens file in **append mode** (`"a"`)
- Writes JSON object + newline
- File persists on disk immediately
- No in-memory database needed

---

#### D. Read Operation (recall_similar_incidents)

**Code (Lines 106-140):**
\`\`\`python
def recall_similar_incidents(
    self,
    dag_id: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Recall similar past incidents for a DAG."""
    
    # Check if file exists
    if not self.incidents_file.exists():
        return []
    
    incidents = []
    
    # Read from disk
    with open(self.incidents_file, "r") as f:  # ← Read mode
        for line in f:                          # ← Read line by line
            if line.strip():
                incident = json.loads(line)     # ← Parse JSON
                if incident["dag_id"] == dag_id:
                    incidents.append(incident)
    
    # Sort by timestamp, most recent first
    incidents.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return incidents[:limit]
\`\`\`

**Key Points:**
- Reads file from disk line-by-line
- Filters by dag_id
- Sorts by timestamp
- Returns most recent

---

## 🔄 How It's Used in the Agent

### 1. Orchestrator Initialization (orchestrator.py)

**Lines 64-67:**
\`\`\`python
# Initialize long-term memory system
logger.info("Initializing agent memory...")
self.memory = AgentMemory()  # ← Creates .agent_memory/ directory
\`\`\`

**When:** Agent starts up
**What:** Creates memory instance, ensures directory exists

---

### 2. Agent Tool Execution (orchestrator.py)

**When agent calls recall_historical_context:**
\`\`\`python
elif tool_name == "recall_historical_context":
    dag_id = tool_input.get("dag_id")
    
    # Read from disk
    context = self.memory.get_dag_context(dag_id)  # ← Reads incidents.jsonl
    
    result = {
        "success": True,
        "result": context,
        "message": f"Retrieved historical context for {dag_id}"
    }
\`\`\`

**When agent calls store_incident:**
\`\`\`python
elif tool_name == "store_incident":
    # Write to disk
    incident_id = self.memory.store_incident(  # ← Appends to incidents.jsonl
        dag_id=tool_input.get("dag_id"),
        issue_type=tool_input.get("issue_type"),
        root_cause=tool_input.get("root_cause"),
        resolution=tool_input.get("resolution"),
        severity=tool_input.get("severity", "medium")
    )
    
    result = {
        "success": True,
        "result": {"incident_id": incident_id, ...}
    }
\`\`\`

---

## 💾 Data Persistence Guarantees

### What Persists
✅ **Incidents** - All stored incidents remain forever
✅ **Patterns** - Discovered patterns
✅ **Context** - Additional metadata

### Across What
✅ **Agent restarts** - Files remain on disk
✅ **Conversations** - New sessions see old data
✅ **Days/weeks** - No expiration
✅ **System reboots** - Standard file system persistence

### How Long
- **Forever** (until manually deleted)
- No automatic cleanup
- No expiration
- Append-only growth

---

## 📊 Storage Format Details

### incidents.jsonl Structure
\`\`\`json
{
  "id": "etl_daily_20260305_162145",
  "timestamp": "2026-03-05T16:21:45.123456",
  "dag_id": "etl_daily",
  "issue_type": "failure",
  "root_cause": "Database connection timeout",
  "resolution": "Increased connection pool size",
  "severity": "high",
  "metadata": {}
}
\`\`\`

### patterns.jsonl Structure
\`\`\`json
{
  "id": "pattern_20260305_162145",
  "timestamp": "2026-03-05T16:21:45.123456",
  "pattern_type": "memory_overflow",
  "description": "ETL pipelines experiencing memory issues during peak hours",
  "affected_dags": ["etl_daily", "etl_hourly"],
  "confidence": 0.92
}
\`\`\`

### context.json Structure
\`\`\`json
{
  "last_health_check": {
    "value": "2026-03-05T16:21:45",
    "timestamp": "2026-03-05T16:21:45"
  },
  "system_stats": {
    "value": {"total_dags": 47},
    "timestamp": "2026-03-05T16:21:45"
  }
}
\`\`\`

---

## 🔍 Inspect Memory Files

### View all incidents
\`\`\`bash
cat .agent_memory/incidents.jsonl | jq .
\`\`\`

### Count total incidents
\`\`\`bash
wc -l .agent_memory/incidents.jsonl
\`\`\`

### Find incidents for specific DAG
\`\`\`bash
grep "etl_daily" .agent_memory/incidents.jsonl | jq .
\`\`\`

### View patterns
\`\`\`bash
cat .agent_memory/patterns.jsonl | jq .
\`\`\`

### Check memory directory size
\`\`\`bash
du -sh .agent_memory/
\`\`\`

---

## 🛠️ Implementation Files

### Core Memory Module
**File:** `agents/airflow_intelligence/memory.py`
**Lines:** 384 total
**Key Methods:**
- `__init__()` - Create directory and file paths
- `store_incident()` - Write to incidents.jsonl
- `recall_similar_incidents()` - Read from incidents.jsonl
- `get_dag_context()` - Comprehensive context retrieval
- `analyze_failure_patterns()` - Pattern analysis
- `store_pattern()` - Write to patterns.jsonl
- `get_known_patterns()` - Read patterns

### Integration Points
**File:** `agents/airflow_intelligence/orchestrator.py`
**Lines:** 67 (init), 337-367 (execution)
**Purpose:** 
- Initialize memory on startup
- Execute memory tool calls
- Bridge agent ↔ memory

### Agent Tools
**File:** `agents/airflow_intelligence/agent.py`
**Lines:** 796-900 (tool definitions)
**Tools:**
- `recall_historical_context` - Read memory
- `store_incident` - Write memory
- `analyze_failure_patterns` - Analyze memory

---

## 🔐 Data Durability

### Write Durability
- **Immediate:** Data written immediately to disk
- **Buffered:** Uses OS file buffering (typically <30s flush)
- **Crash-safe:** Completed writes survive crashes
- **Atomic:** Each line write is atomic

### Read Consistency
- **Consistent:** Reads always see all completed writes
- **No cache:** Reads directly from disk files
- **Sequential:** Reads in insertion order

### Backup Strategy
\`\`\`bash
# Manual backup
cp -r .agent_memory/ .agent_memory_backup_$(date +%Y%m%d)/

# Automated backup (add to cron)
0 0 * * * tar -czf ~/backups/agent_memory_$(date +\%Y\%m\%d).tar.gz .agent_memory/
\`\`\`

---

## 📈 Growth & Scalability

### File Growth
- **1 incident** ≈ 300 bytes
- **1000 incidents** ≈ 300 KB
- **10,000 incidents** ≈ 3 MB
- **100,000 incidents** ≈ 30 MB

### Performance
- **Write:** O(1) - append-only
- **Read (filtered):** O(n) - linear scan
- **Memory usage:** Minimal (streaming reads)

### When to Optimize
- If `incidents.jsonl` > 100 MB
- If queries become slow (>1 second)
- Consider SQLite or proper database

---

## 🎯 Key Takeaways

### Where
✅ `.agent_memory/` directory in project root

### How
✅ JSONL files (JSON Lines format)
✅ Append-only writes
✅ Line-by-line reads

### When
✅ Written when agent calls `store_incident()`
✅ Read when agent calls `recall_historical_context()`

### Why This Works
✅ Simple - just files on disk
✅ Reliable - standard file system guarantees
✅ Portable - works anywhere Python runs
✅ Inspectable - human-readable JSON
✅ Persistent - survives restarts
✅ No external dependencies - no database needed

---

## 🧪 Test Persistence

\`\`\`bash
# Session 1: Store incident
python -m agents.airflow_intelligence.cli chat
> "Store an incident for etl_daily with failure type"
> exit

# Check file exists
ls -la .agent_memory/
cat .agent_memory/incidents.jsonl

# Session 2: Recall (NEW process)
python -m agents.airflow_intelligence.cli chat
> "What do you remember about etl_daily?"
# Should recall the incident from session 1!
\`\`\`

---

**Summary:** Memory is implemented as simple append-only JSONL files in `.agent_memory/` directory, providing true persistence across sessions with zero external dependencies! 🎉
