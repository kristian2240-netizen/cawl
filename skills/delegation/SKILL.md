---
name: delegation
description: "Main Brain delegation protocol. phi3:mini classifies requests and dispatches to Tech Priests. Apply when processing any request."
user-invocable: true
---

# Delegation Protocol — The Cogitator Network

The Main Brain (phi3:mini) is the router. It classifies, dispatches, and synthesizes. It does NOT do heavy work itself.

## Classification Matrix

| Request Type | Primary Priest | Fallback | VRAM | RPD Cost |
|---|---|---|---|---|
| Simple Q&A | phi3:mini (direct) | Steel/qwen3:8b | 0 | 0 |
| Code generation | Beta (OpenRouter) | Alpha (Groq) | 0 | 1 |
| Code review | Alpha (Groq) | Beta (OpenRouter) | 0 | 1 |
| Complex debugging | Alpha (Groq) | Gamma (NVIDIA) | 0 | 1 |
| Architecture design | Alpha (Groq) | Beta (OpenRouter) | 0 | 1 |
| Quick code edit | Delta (Steel) | Beta (OpenRouter) | 4.5GB | 0 |
| Performance optimization | Gamma (NVIDIA) | Alpha (Groq) | 0 | 1 |
| Algorithm design | Gamma (NVIDIA) | Alpha (Groq) | 0 | 1 |
| Documentation | Beta (OpenRouter) | Delta (Steel) | 0 | 1 |
| Image/vision | llava:7b (Steel) | — | 4.7GB | 0 |
| Privacy-sensitive | Steel/qwen3:8b | Delta (Steel) | 5.2GB | 0 |
| Research/analysis | Alpha (Groq) | Beta (OpenRouter) | 0 | 1 |

## Dispatch Protocol

### Step 1: Classify
```
Input → phi3:mini
  Extract: task_type, complexity, privacy_level, code_involved
  Output: { priest: "alpha|beta|gamma|delta|direct", reason: "..." }
```

### Step 2: Check Rate Limits
```
Before dispatching to cloud priest:
  - Check: have we used >800 RPD today on this provider?
  - If yes → fallback to next priest
  - If no → dispatch
```

### Step 3: Dispatch
```
Send task to selected priest with:
  - Clear task description
  - Required output format
  - Constraints (length, language, etc.)
  - Timeout: 30s for cloud, 60s for local
```

### Step 4: Synthesize
```
Priest returns result → phi3:mini
  - Validate: is result complete? correct format?
  - If incomplete → retry with different priest
  - If complete → present to user
  - Add C.A.W.L. voice if TTS enabled
```

## Batch Processing

For multiple code tasks, batch them to minimize RPD burn:
```
1. Collect all tasks
2. Route to Beta (OpenRouter) — 50 RPD limit
3. If >5 tasks, split across Beta + Alpha
4. If >10 tasks, add Gamma
5. Delta handles overflow (unlimited local)
```

## Emergency Protocols

### All Cloud Providers Rate-Limited:
```
1. Steel/qwen3:8b (local, general)
2. Steel/qwen2.5-coder:7b (local, code)
3. Steel/phi3:mini (emergency, slow)
4. Text-only response with apology
```

### VRAM Exhausted:
```
1. Unload non-essential models
2. Use phi3:mini only (2.3GB)
3. Route complex tasks to cloud priests
4. Warn user about degraded performance
```

### Network Down:
```
1. Steel/phi3:mini (always available)
2. Steel/qwen3:8b (if loaded)
3. Steel/qwen2.5-coder:7b (if loaded)
4. Text-only response
```

## Performance Tracking

After each delegation, log:
```
{ task_type, priest, provider, tokens_in, tokens_out, latency_ms, success: bool }
```

Track daily:
- RPD usage per provider
- Average latency per priest
- Success rate per priest
- Total tokens processed

## The $0 Vow

- All priests use free tiers or local models
- Never spend API credits without explicit user permission
- If free tier is exhausted, use local models or wait for reset
- Warn user before any paid operation
