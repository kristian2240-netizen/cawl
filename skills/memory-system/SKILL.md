---
name: memory-system
description: "Cognithor-style 6-tier cognitive memory. Apply when storing, retrieving, or reasoning about information."
user-invocable: true
---

# 6-Tier Cognitive Memory — The Knowledge Vault

Inspired by Cognithor's architecture. All tiers stored locally, $0, zero telemetry.

## Memory Tiers

| Tier | Name | Storage | Purpose | Example |
|------|------|---------|---------|---------|
| 1 | **Core** | `SOUL.md` | Identity, rules, personality | "I am C.A.W.L." |
| 2 | **Episodic** | `vault/sessions/` | What happened today/yesterday | "2026-08-20: Built tech priest system" |
| 3 | **Semantic** | `memory/knowledge-graph.json` | Facts, entities, relations | "Groq has 1K RPD limit" |
| 4 | **Procedural** | `skills/*/SKILL.md` | Learned skills and workflows | "How to route code tasks" |
| 5 | **Working** | RAM (volatile) | Active session context | Current conversation |
| 6 | **Tactical** | `memory/tactical.json` | Active goals, pending actions | "Need to install OpenFang" |

## Tier 1: Core Identity
- **File:** `SOUL.md`
- **What:** Identity, rules, personality, commandments
- **When:** Referenced every request
- **Update:** Rarely — only when persona evolves

## Tier 2: Episodic Memory
- **Directory:** `vault/sessions/`
- **Format:** `YYYY-MM-DD.md` — one file per day
- **What:** What happened, decisions made, outcomes
- **When:** Appended after every significant session
- **Update:** Append-only, never edit past entries

### Session Log Format
```markdown
# 2026-08-20

## Session 1: Tech Priest System
- **Time:** 14:00-15:30
- **Task:** Built 4-tech-priest delegation system
- **Outcome:** Success — all priests configured
- **Lessons:** Groq qwen3.6-27b is fast for reasoning
- **RPD Used:** Groq: 5, OpenRouter: 3, NVIDIA: 2

## Session 2: Cognithor Integration
- **Time:** 15:30-16:00
- **Task:** Implemented 6-tier memory
- **Outcome:** In progress
- **Lessons:** N/A
```

## Tier 3: Semantic Knowledge Graph
- **File:** `memory/knowledge-graph.json`
- **What:** Entities, facts, and their relationships
- **Format:** JSON with nodes and edges
- **When:** Updated when new knowledge is acquired
- **Search:** By entity name, relation type, or recency

### Knowledge Graph Schema
```json
{
  "entities": [
    {
      "id": "groq-provider",
      "type": "provider",
      "name": "Groq",
      "properties": {
        "rpm": 30,
        "tpm": 6000,
        "rpd": 1000,
        "hardware": "LPU",
        "speed": "very fast"
      },
      "created": "2026-08-20",
      "lastAccessed": "2026-08-20"
    }
  ],
  "relations": [
    {
      "source": "groq-provider",
      "target": "tech-priest-alpha",
      "type": "bound_to",
      "properties": { "model": "qwen3.6-27b" }
    }
  ]
}
```

## Tier 4: Procedural Memory
- **Directory:** `skills/*/SKILL.md`
- **What:** How to do things — workflows, procedures, skills
- **When:** Referenced when executing tasks
- **Update:** When new procedures are learned

## Tier 5: Working Memory
- **Location:** RAM (current session)
- **What:** Active context, recent messages, current task
- **When:** Automatic — cleared each session
- **Update:** Automatic

## Tier 6: Tactical Memory
- **File:** `memory/tactical.json`
- **What:** Active goals, pending actions, rollback points
- **When:** Updated when tasks are created/completed
- **Format:** Priority queue with status

### Tactical Memory Schema
```json
{
  "goals": [
    {
      "id": "goal-001",
      "description": "Implement OpenFang Hands",
      "status": "in_progress",
      "priority": "high",
      "created": "2026-08-20",
      "deadline": null,
      "subtasks": [
        { "task": "Create Hands config", "status": "completed" },
        { "task": "Implement Researcher Hand", "status": "pending" },
        { "task": "Implement Collector Hand", "status": "pending" }
      ],
      "rollback": {
        "previous_state": "no-hands",
        "can_rollback": true
      }
    }
  ],
  "pending_actions": [
    {
      "action": "Pull qwen3-embedding:0.6b for vector search",
      "priority": "medium",
      "created": "2026-08-20"
    }
  ]
}
```

## Memory Search Protocol

When searching memory:
1. **Tier 5 (Working)** — Check current session first
2. **Tier 6 (Tactical)** — Check active goals
3. **Tier 3 (Semantic)** — Query knowledge graph
4. **Tier 2 (Episodic)** — Search recent session logs
5. **Tier 4 (Procedural)** — Check skills directory
6. **Tier 1 (Core)** — Check identity (rarely needed)

## Memory Consolidation

Every 7 days, consolidate:
1. **Episodic → Semantic:** Extract facts from session logs
2. **Semantic → Procedural:** Turn repeated patterns into skills
3. **Tactical → Episodic:** Archive completed goals
4. **Prune:** Remove stale entities (>30 days, no references)

## The $0 Vow

- All memory stored locally in JSON/Markdown
- No cloud databases, no external services
- Search is local (BM25 + simple graph traversal)
- Vector search via Ollama embeddings (optional, local)
