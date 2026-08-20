---
name: tech-priests
description: "The five Tech Priests of the Cogitator Network. Each priest is bound to one compute provider and specializes in a domain. Invoke when delegating work."
user-invocable: true
---

# Tech Priests — The Cogitator Network

Five specialists, each bound to one compute provider. The Main Brain (phi3:mini) routes work to them. They never share keys.

## Benchmark Results (2026-08-20)

| Priest | Provider | Latency | Status |
|---|---|---|---|
| Alpha | Groq | **530-867ms** | EXCELLENT |
| Beta | OpenRouter | 2-14s | GOOD |
| Gamma | NVIDIA NIM | 758-1862ms | GOOD |
| Delta | Steel (local) | 1-6.4s | OK |
| Epsilon | Mistral | ~1-2s (est.) | NEEDS API KEY |

## The Five Priests

### Tech-Priest-Alpha — "The Reasoner" (FASTEST)
- **Provider:** Groq (LPU hardware)
- **Model:** `Groq/qwen/qwen3.6-27b` (fallback: `Groq/openai/gpt-oss-20b`)
- **Rate Limits:** 30 RPM, 6K TPM, 1K RPD
- **Benchmark:** 530-867ms average, sub-second for all tasks
- **Specialty:** Fast reasoning, code review, architecture decisions, complex analysis
- **Personality:** Methodical, thorough, thinks before speaking
- **When to invoke:** Code review, architecture questions, complex debugging, need fast cloud reasoning
- **Cost:** $0 free tier, but burns RPD fast — use wisely
- **VERDICT:** Use as primary for ALL cloud tasks — fastest provider by far

### Tech-Priest-Beta — "The Architect"
- **Provider:** OpenRouter (free models)
- **Model:** `OpenRouter/google/gemma-4-26b-a4b-it:free` (fallback: `OpenRouter/openai/gpt-oss-20b:free`)
- **Rate Limits:** 50 RPD (no credits), 1K RPD ($10+ credits), 20 RPM
- **Benchmark:** 2-14s (variable)
- **Specialty:** Code generation, documentation, general coding tasks
- **Personality:** Prolific, creative, generates lots of code
- **When to invoke:** Writing new code, generating boilerplate, documentation, refactoring
- **Cost:** $0, but 50 RPD limit is tight — batch work when possible
- **VERDICT:** Use for batch code generation when Alpha is rate-limited

### Tech-Priest-Gamma — "The Artificer"
- **Provider:** NVIDIA NIM
- **Model:** `NVIDIA/meta/llama-3.1-8b-instruct`
- **Rate Limits:** ~40 RPM, ~1K RPD
- **Benchmark:** 758-1862ms
- **Specialty:** Quick cloud tasks, fast inference, backup reasoning
- **Personality:** Fast, reliable, always available
- **When to invoke:** Quick tasks when Alpha is rate-limited, backup reasoning
- **Cost:** $0 free tier
- **VERDICT:** Good backup — only working NVIDIA model (deepseek-coder, codestral, GLM 5.2 all broken/deprecated)
- **NOTE:** GLM 5.2 deprecated 2026-08-24, deepseek-coder returns 404

### Tech-Priest-Delta — "The Forgewright"
- **Provider:** Steel (Ollama local)
- **Model:** `Steel/qwen2.5-coder:7b` (fallback: `Steel/phi3:mini`)
- **Rate Limits:** Unlimited (local)
- **Benchmark:** 1-6.4s
- **Specialty:** Local code generation, file editing, quick code tasks
- **Personality:** Reliable, always available, works offline
- **When to invoke:** Quick code edits, local-only tasks, privacy-sensitive code, when cloud is unavailable
- **Cost:** $0, GPU only — VRAM shared with main brain
- **VERDICT:** Essential fallback — works offline, unlimited
- **NOTE:** qwen3:8b removed — returns empty responses consistently

### Tech-Priest-Epsilon — "The Scribe" (NEEDS API KEY)
- **Provider:** Mistral (La Plateforme)
- **Model:** `Mistral/mistral-small-latest` (fallback: `Mistral/codestral-latest`)
- **Rate Limits:** ~1 req/sec free tier, ~1B tokens/month
- **Specialty:** Code generation, fast inference, European language support
- **Personality:** Fast, multilingual, code-focused
- **When to invoke:** Code generation, multilingual tasks, when other priests are rate-limited
- **Cost:** $0 free tier (requires API key from console.mistral.ai)
- **VERDICT:** Good addition — need to get API key first
- **ACTION:** Create account at console.mistral.ai, generate API key, update config

## Delegation Rules

### Updated Routing (Post-Benchmark):
```
User Request → phi3:mini (classify + route)
  ├─ Simple question → phi3:mini answers directly
  ├─ Code generation → Alpha (Groq) — 530ms
  ├─ Code review → Alpha (Groq) — 530ms
  ├─ Architecture → Alpha (Groq) — 530ms
  ├─ Complex debugging → Alpha (Groq) — 530ms
  ├─ Quick edit → Delta (Steel) — unlimited
  ├─ Privacy-sensitive → Delta (Steel) — local only
  ├─ Vision/image → Steel/llava:7b — local only
  ├─ Backup cloud → Gamma (NVIDIA) — 758ms
  ├─ Batch code → Beta (OpenRouter) — free
  └─ When all else fails → Epsilon (Mistral) — if key available
```

### Rate Limit Budget:
- **Groq:** 1K RPD — PRIMARY for everything cloud (530ms)
- **OpenRouter:** 50 RPD — batch code generation only
- **NVIDIA:** ~1K RPD — backup reasoning
- **Steel:** Unlimited — local fallback
- **Mistral:** ~1 req/sec — overflow when others rate-limited

### Fallback Chain:
```
1. Alpha (Groq) — primary
2. Gamma (NVIDIA) — if Alpha rate-limited
3. Beta (OpenRouter) — if both Alpha and Gamma rate-limited
4. Epsilon (Mistral) — if key available
5. Delta (Steel) — local fallback
6. phi3:mini — emergency (slow)
7. Text-only response with apology
```

## Anti-Patterns

- Using Beta (OpenRouter) for complex reasoning (50 RPD limit)
- Sending private data to cloud priests
- Running two local models simultaneously (VRAM conflict)
- Not tracking RPD usage — you WILL hit limits
- Using phi3:mini for complex code (too small — delegate to priests)
- Using NVIDIA NIM for anything other than llama-3.1-8b (everything else is broken)
