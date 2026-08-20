---
name: performance-dashboard
description: "Real-time performance dashboard for all providers, hands, and system health. Apply when checking system status."
user-invocable: true
---

# Performance Dashboard

Live performance tracking for C.A.W.L.'s infrastructure.

## Dashboard Location

`memory/dashboard/system-status.json` — Updated after every provider test, hand run, or system event.

## What Gets Tracked

### Provider Metrics
- **Latency:** Rolling average of last 10 requests
- **Success Rate:** % of successful responses
- **RPD Usage:** Requests per day remaining
- **Error Count:** Total errors in last 24h
- **Last Error:** Most recent error message

### Hand Metrics
- **Runs:** Total runs since activation
- **Tokens:** Total tokens consumed
- **Success Rate:** % of successful runs
- **Last Run:** Timestamp of most recent run
- **Avg Duration:** Average run duration

### System Metrics
- **Uptime:** Time since last restart
- **Memory Usage:** VRAM utilization
- **Model Load:** Current models in memory
- **Session Count:** Total sessions today

## Dashboard Update Protocol

### After Every Provider Test
```json
{
  "type": "provider_test",
  "provider": "groq",
  "model": "qwen/qwen3.6-27b",
  "latency_ms": 393,
  "success": true,
  "timestamp": "2026-08-20T22:00:00Z"
}
```

### After Every Hand Run
```json
{
  "type": "hand_run",
  "hand": "collector",
  "status": "success",
  "duration_ms": 45000,
  "tokens_used": 12500,
  "timestamp": "2026-08-20T22:00:00Z"
}
```

### After Every Error
```json
{
  "type": "error",
  "source": "provider",
  "name": "nvidia",
  "error": "403 Forbidden",
  "timestamp": "2026-08-20T22:00:00Z"
}
```

## Dashboard Display

When asked "show dashboard" or "system status", read `memory/dashboard/system-status.json` and format:

```
=== C.A.W.L. PERFORMANCE DASHBOARD ===

PROVIDERS
  Groq:      393ms avg | 99.9% success | 847/1000 RPD
  Mistral:   443ms avg | 100% success | N/A RPD
  Steel:     479ms avg | 100% success | Unlimited
  NVIDIA:    543ms avg | 95% success | 920/1000 RPD
  OpenRouter: 915ms avg | 98% success | 32/50 RPD

HANDS
  Researcher:   0 runs | 0 tokens | On-demand
  Collector:    0 runs | 0 tokens | Every 6h
  Forecaster:   0 runs | 0 tokens | Weekly
  Code Review:  0 runs | 0 tokens | On-demand
  API Monitor:  0 runs | 0 tokens | Every 4h

SYSTEM
  Uptime: 12h 34m
  VRAM: 6.8/8.0 GB (85%)
  Models Loaded: phi3:mini, qwen2.5-coder:7b
  Sessions Today: 3

SCORE: 78/100
```

## Alerting

Alert when:
- Provider latency > 5x baseline
- Provider success rate < 90%
- RPD remaining < 10%
- Hand run fails
- VRAM usage > 90%

## History

Keep last 24 hours of metrics in `memory/dashboard/metrics-history.json`.
Prune entries older than 24 hours on each update.
