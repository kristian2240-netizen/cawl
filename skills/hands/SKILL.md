---
name: hands
description: "OpenFang-style autonomous Hands. Scheduled agents that work for you 24/7. Apply when managing autonomous tasks."
user-invocable: true
---

# Hands — Autonomous Agents

Inspired by OpenFang's Hands architecture. Agents that work on schedules, not just on prompt.

## What Are Hands?

Hands are autonomous agents that run on schedules. They don't wait for you to type — they work for you. Each Hand has:
- **HAND.toml:** Manifest (tools, settings, schedule)
- **System Prompt:** Multi-phase operational playbook
- **SKILL.md:** Domain expertise reference
- **Guardrails:** Approval gates for sensitive actions

## The 4 C.A.W.L. Hands

### Hand 1: Researcher
- **Schedule:** On-demand (manual activation)
- **Task:** Deep research on any topic
- **Pipeline:** Query → Multi-source search → CRAAP evaluation → APA citations → Report
- **Tools:** websearch, webfetch, filesystem
- **Guardrails:** Read-only, no purchases
- **Output:** `hands/reports/research-{topic}-{date}.md`

### Hand 2: Collector
- **Schedule:** Every 6 hours (configurable)
- **Task:** OSINT-style intelligence gathering
- **Pipeline:** Monitor targets → Change detection → Sentiment analysis → Knowledge graph update → Alerts
- **Tools:** websearch, webfetch, memory-system
- **Guardrails:** Read-only, alert-only (no actions)
- **Output:** Updates to `memory/knowledge-graph.json` + alerts

### Hand 3: Forecaster
- **Schedule:** Weekly (every Monday)
- **Task:** Superforecasting with confidence intervals
- **Pipeline:** Collect signals → Build reasoning chains → Generate predictions → Track accuracy
- **Tools:** websearch, webfetch, memory-system
- **Guardrails:** Read-only, no real-world actions
- **Output:** `hands/forecasts/forecast-{date}.md`

### Hand 4: Code Reviewer
- **Schedule:** On-demand (triggered by code changes)
- **Task:** Autonomous code review
- **Pipeline:** Detect changes → Analyze code → Find bugs → Suggest improvements → Report
- **Tools:** filesystem, shell (read-only)
- **Guardrails:** Read-only, suggest-only (no auto-fixes)
- **Output:** `hands/reviews/review-{file}-{date}.md`

## Hand Manifest Format (HAND.toml)

```toml
[hand]
name = "researcher"
version = "0.1.0"
description = "Deep autonomous researcher"
schedule = "on-demand"  # or "*/6 * * * *", "0 9 * * 1", etc.

[hand.tools]
allowed = ["websearch", "webfetch", "filesystem"]
denied = ["shell", "browser"]

[hand.guardrails]
read_only = true
require_approval = false
max_tokens_per_run = 50000
timeout_seconds = 300

[hand.output]
directory = "hands/reports"
format = "markdown"
retain_days = 30

[hand.dashboard]
metrics = ["tasks_completed", "tokens_used", "accuracy_score"]
```

## Hand Lifecycle

```
1. CREATE    → Define HAND.toml + system prompt + SKILL.md
2. ACTIVATE  → Hand starts on schedule
3. RUNNING   → Hand executes pipeline
4. PAUSE     → Hand pauses (manual or rate-limit)
5. RESUME   → Hand continues
6. DEACTIVATE → Hand stops
7. ARCHIVE   → Hand output archived
```

## Hand Commands

```bash
# Create a new hand
# (manual — create directory in hands/)

# Activate a hand
# (set schedule in HAND.toml)

# Check hand status
# (read hands/{name}/status.json)

# Pause a hand
# (set schedule to "paused" in HAND.toml)

# Resume a hand
# (set schedule back to cron expression)

# Deactivate a hand
# (set schedule to "inactive" in HAND.toml)
```

## Hand Output

Each hand produces structured output:
```json
{
  "hand": "researcher",
  "started": "2026-08-20T14:00:00Z",
  "completed": "2026-08-20T14:05:30Z",
  "status": "success",
  "tokens_used": 12500,
  "output_file": "hands/reports/research-cognithor-2026-08-20.md",
  "metrics": {
    "sources_checked": 15,
    "citations_found": 8,
    "confidence": "HIGH"
  }
}
```

## Guardrails

### Always enforced:
- Read-only by default (no writes to system files)
- $0 Vow — no paid API calls without approval
- Rate limit awareness — check RPD before dispatching
- Timeout — 5 minutes max per hand run
- Max tokens — 50K per run

### Approval required:
- Any write to `vault/` (append-only)
- Any network request to unknown hosts
- Any shell command
- Any file deletion

## Integration with Tech Priests

Hands use Tech Priests for LLM calls:
- **Researcher** → Alpha (Groq) for reasoning, Beta (OpenRouter) for generation
- **Collector** → phi3:mini for classification, Alpha for analysis
- **Forecaster** → Alpha (Groq) for reasoning chains
- **Code Reviewer** → Alpha (Groq) for review, Delta (Steel) for local

## Dashboard

Hand metrics tracked in `memory/tactical.json`:
```json
{
  "hands": {
    "researcher": { "runs": 5, "tokens": 62500, "last_run": "2026-08-20" },
    "collector": { "runs": 30, "tokens": 150000, "last_run": "2026-08-20" },
    "forecaster": { "runs": 4, "tokens": 50000, "last_run": "2026-08-19" },
    "code-reviewer": { "runs": 12, "tokens": 75000, "last_run": "2026-08-20" }
  }
}
```
