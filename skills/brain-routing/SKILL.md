---
name: brain-routing
description: "C.A.W.L. brain routing — phi3:mini is the Main Brain, routes to Tech Priests. Apply when processing any request."
user-invocable: true
---

# Brain Routing — The Cogitator Network v2

**Main Brain: Steel/phi3:mini** — Fast local router, ~53 tok/s, 2.3GB VRAM
**Tech Priests:** 4 specialists, each bound to one provider

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         USER REQUEST                     │
                    └──────────────┬──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │    MAIN BRAIN: Steel/phi3:mini           │
                    │    (Classify + Route + Synthesize)       │
                    │    Speed: ~53 tok/s | VRAM: 2.3GB       │
                    └──────────────┬──────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │ Tech-Priest-Alpha │ │ Tech-Priest-  │ │ Tech-Priest-      │
    │ Groq (LPU)        │ │ Beta          │ │ Gamma             │
    │ qwen3.6-27b       │ │ OpenRouter    │ │ NVIDIA NIM        │
    │ 30RPM/6KTPM/1KRPD │ │ gemma-4-26b   │ │ deepseek-coder    │
    │ Reasoning+Review  │ │ 50-1K RPD     │ │ ~40RPM/~1KRPD     │
    │                   │ │ Code Gen      │ │ Deep Analysis     │
    └───────────────────┘ └───────────────┘ └───────────────────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │    Tech-Priest-Delta (Local Fallback)    │
                    │    Steel/qwen2.5-coder:7b               │
                    │    Unlimited | ~4.5GB VRAM               │
                    └─────────────────────────────────────────┘
```

## Routing Rules

### Default Path (70% of requests)
```
Request → phi3:mini (classify) → Route to priest → phi3:mini (synthesize) → User
```

### Code Generation
```
"Write code" / "Create function" / "Implement" → Tech-Priest-Beta (OpenRouter, free)
If Beta fails → Tech-Priest-Alpha (Groq)
If Alpha fails → Tech-Priest-Delta (Steel, local)
```

### Code Review
```
"Review this" / "Check my code" / "Find bugs" → Tech-Priest-Alpha (Groq, fast)
If Alpha fails → Tech-Priest-Gamma (NVIDIA)
If Gamma fails → Tech-Priest-Delta (Steel, local)
```

### Complex Debugging
```
"Debug this" / "Fix error" / "Why isn't this working" → Tech-Priest-Alpha (Groq)
If Alpha fails → Tech-Priest-Gamma (NVIDIA)
If Gamma fails → Tech-Priest-Delta (Steel, local)
```

### Architecture Design
```
"Design system" / "Architecture" / "How should I structure" → Tech-Priest-Alpha (Groq)
If Alpha fails → Tech-Priest-Beta (OpenRouter)
If Beta fails → Steel/qwen3:8b (local)
```

### Quick Code Edit
```
"Change this line" / "Rename variable" / "Small fix" → Tech-Priest-Delta (Steel, local)
No fallback needed — local is always available
```

### Deep Analysis
```
"Optimize performance" / "Algorithm analysis" / "Complexity" → Tech-Priest-Gamma (NVIDIA)
If Gamma fails → Tech-Priest-Alpha (Groq)
If Alpha fails → Steel/qwen3:8b (local)
```

### Vision/Image
```
"Describe image" / "What's in screenshot" → Steel/llava:7b (local only)
No cloud fallback — privacy
```

### Privacy-Sensitive
```
"Personal data" / "Credentials" / "Private" → Steel/qwen3:8b (local only)
NEVER send to cloud priests
```

### Simple Q&A
```
Quick facts, yes/no, simple lookups → phi3:mini (direct answer)
No priest needed — save RPD
```

## Rate Limit Budget

| Provider | Daily Budget | Used For | Alert At |
|---|---|---|---|
| Groq | 1,000 RPD | Reasoning, review | 800 RPD |
| OpenRouter | 50 RPD (no credits) | Code generation | 40 RPD |
| NVIDIA | ~1,000 RPD | Deep analysis | 800 RPD |
| Steel | Unlimited | Local tasks | Never |

## Fallback Chain

```
1. Primary priest (per routing rules)
2. Different cloud priest (if primary is rate-limited)
3. Steel/qwen3:8b (if all cloud fails)
4. Steel/phi3:mini (emergency — slow but works)
5. Text-only response with apology
```

## VRAM Management (RTX 4070 Laptop — 8GB)

- phi3:mini (2.3GB) is ALWAYS loaded — it's the main brain
- Only ONE 7-8B model can run alongside phi3:mini
- qwen2.5-coder:7b (~4.5GB) loads on-demand for Delta
- llava:7b (4.7GB) loads for vision, evicts code model
- Model switching causes ~2-3s eviction delay

## Anti-Patterns

- Using Alpha (Groq) for simple questions (waste of 1K RPD)
- Using Beta (OpenRouter) for complex reasoning (50 RPD limit)
- Sending private data to cloud priests
- Running two local models simultaneously (VRAM conflict)
- Not tracking RPD usage — you WILL hit limits
- Using phi3:mini for complex code (too small — delegate to priests)
