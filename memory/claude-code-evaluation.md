# Claude Code as Harness — Evaluation

## What is Claude Code Router (CCR)?

Open-source local proxy (36K+ GitHub stars, MIT license) that sits between Claude Code and LLM providers. Routes requests by task type to different models/providers.

## How It Works

```
Claude Code → CCR (localhost:3456) → Provider (Groq/OpenRouter/Ollama/etc.)
```

CCR intercepts requests and rewrites them for different providers based on task type:
- **background:** File scanning, context compaction → cheap model
- **think:** Plan Mode, complex reasoning → strong model
- **longContext:** >60K tokens → high-context model
- **default:** Everything else → capable mid-tier

## Would It Be Worth It for C.A.W.L.?

### YES, if:
1. You use Claude Code as your primary coding agent
2. You want to route Claude Code requests through your free providers
3. You want task-based routing (background → cheap, reasoning → expensive)
4. You want automatic failover between providers

### NO, if:
1. You don't use Claude Code (you use OpenClaw)
2. You're already routing through OpenClaw's tech priests
3. You want a simpler setup

### My Recommendation: **NOT WORTH IT for C.A.W.L.**

Here's why:

1. **OpenClaw already does what CCR does** — tech priests route to different providers
2. **CCR is designed for Claude Code specifically** — it translates Anthropic API format to other providers
3. **We already have the routing logic** — phi3:mini classifies, priests execute
4. **Adding CCR would be redundant** — another layer of indirection for no benefit
5. **CCR requires Node.js 22+** — adds dependency

### When CCR WOULD Be Worth It:

If you start using Claude Code as a **separate coding agent** alongside OpenClaw, then CCR would let you:
- Route Claude Code's background tasks to free models (save money)
- Route complex reasoning to Groq (fast)
- Keep local code tasks on Ollama (private)

But that's a different architecture than what we have.

## Alternative: Use CCR's Concept, Not CCR Itself

We can borrow CCR's routing concept (task-based routing) without installing CCR:

1. **background tasks** → phi3:mini (local, free)
2. **think tasks** → Groq qwen3.6-27b (fast, free)
3. **longContext tasks** → OpenRouter gemma-4-26b (free, large context)
4. **default tasks** → Groq qwen3.6-27b (fast, free)

This is exactly what our tech priest system already does!

## Bottom Line

CCR is excellent software, but it's designed for a different use case (Claude Code users who want to route to non-Anthropic providers). Our tech priest system already implements the same concept for OpenClaw.

**If you ever adopt Claude Code as a coding agent, install CCR then. For now, skip it.**
