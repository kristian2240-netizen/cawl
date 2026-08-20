---
name: learning-loops
description: "Automated learning from session logs. Extract patterns, update llm-wiki, improve over time. Apply when reviewing past sessions."
user-invocable: true
---

# Learning Loops

C.A.W.L. learns from every session. This skill defines how.

## What Gets Learned

### From Session Logs (`06 Journal/Session Log.md`)
- **Successful patterns:** What worked well
- **Failed patterns:** What didn't work
- **User preferences:** What Void Dragon liked/disliked
- **Provider performance:** Which priest handled what best
- **Error patterns:** Common mistakes to avoid

### From Hand Reports
- **API availability:** Which experimental APIs are worth using
- **Research quality:** Which sources are most reliable
- **Code review findings:** Common code issues

### From Dashboard Metrics
- **Provider degradation:** When a provider gets slower
- **Capacity planning:** When to add/remove providers
- **Cost tracking:** Even $0 has opportunity costs

## Learning Pipeline

### 1. Collect (Every Session)
After each session, append to `06 Journal/Session Log.md`:
```markdown
## Session {date}
- **Duration:** {minutes}m
- **Tasks:** {list}
- **Providers Used:** {list}
- **Issues:** {list}
- **Wins:** {list}
```

### 2. Distill (Daily)
At end of day, analyze session logs and extract:
- **New patterns** → Add to `llm-wiki.md`
- **User preferences** → Update `vault/02 Memory/User Context.md`
- **Provider notes** → Update `memory/knowledge-graph.json`
- **Error fixes** → Add to `memory/learning/error-patterns.json`

### 3. Apply (Next Session)
Before each session:
- Read `llm-wiki.md` for known patterns
- Read `memory/learning/error-patterns.json` for things to avoid
- Read `memory/learning/user-patterns.json` for preferences

### 4. Archive (Weekly)
Every Sunday:
- Archive old session logs to `memory/learning/archive/`
- Summarize week in `memory/learning/weekly-summary-{date}.md`
- Update system score in `memory/system-improvements.md`

## Learning Files

| File | Purpose |
|---|---|
| `memory/learning/error-patterns.json` | Known errors and fixes |
| `memory/learning/user-patterns.json` | User behavior patterns |
| `memory/learning/provider-patterns.json` | Provider reliability data |
| `memory/learning/weekly-summary-{date}.md` | Weekly summaries |
| `memory/learning/archive/` | Old session logs |

## Error Pattern Format

```json
{
  "patterns": [
    {
      "id": "err-001",
      "error": "phi3:mini cold start > 10s",
      "cause": "Ollama env vars not propagated",
      "fix": "Logout/login to propagate OLLAMA_KEEP_ALIVE",
      "frequency": 3,
      "last_seen": "2026-08-20",
      "status": "pending_fix"
    }
  ]
}
```

## User Pattern Format

```json
{
  "patterns": [
    {
      "id": "user-001",
      "pattern": "Prefers direct answers over explanations",
      "context": "When asking technical questions",
      "frequency": 15,
      "last_seen": "2026-08-20"
    }
  ]
}
```

## Provider Pattern Format

```json
{
  "patterns": [
    {
      "id": "provider-001",
      "provider": "groq",
      "pattern": "Consistently fastest for reasoning tasks",
      "latency_p50": 393,
      "latency_p99": 867,
      "reliability": 0.999,
      "last_updated": "2026-08-20"
    }
  ]
}
```

## Weekly Summary Format

```markdown
# Weekly Summary — Week of {date}

## Stats
- Sessions: {n}
- Total Duration: {minutes}m
- Providers Used: {list}
- Hands Run: {n}

## Top Patterns
1. {pattern}
2. {pattern}

## Errors Encountered
1. {error} → {fix}

## Improvements Made
1. {improvement}

## Next Week Focus
- {focus}
```

## Score Impact

Each learning loop iteration should improve the system score:
- **Error patterns** → Better error recovery (+1-2 points)
- **User patterns** → Better user experience (+1-2 points)
- **Provider patterns** → Better routing (+1 point)
- **Weekly reviews** → Continuous improvement (+1 point per week)
