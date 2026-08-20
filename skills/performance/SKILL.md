---
name: performance
description: "Performance measurement for the Cogitator Network. Track latency, RPD usage, and accuracy."
user-invocable: true
---

# Performance Measurement — The Cogitator Network

## Metrics Tracked

### Latency
- **Classification time:** How fast phi3:mini routes (target: <1s)
- **Priest response time:** How fast each priest responds
- **End-to-end time:** Total time from request to response

### Rate Limit Usage
- **Groq RPD:** Requests per day (budget: 1,000)
- **OpenRouter RPD:** Requests per day (budget: 50 without credits)
- **NVIDIA RPD:** Requests per day (budget: ~1,000)
- **Steel:** Unlimited (local)

### Accuracy
- **Classification accuracy:** Did phi3:mini route to the right priest?
- **Task completion:** Did the priest complete the task?
- **Fallback rate:** How often did primary priest fail?

## Measurement Protocol

### Before Optimization (Baseline)
```
1. Run 10 test requests through phi3:mini (direct)
2. Measure: latency, accuracy, completeness
3. This is the "before" baseline
```

### After Optimization (Tech Priests)
```
1. Run same 10 test requests through delegation system
2. Measure: latency, accuracy, completeness, RPD usage
3. This is the "after" result
4. Compare with baseline
```

## Test Cases

| # | Request Type | Expected Route | Complexity |
|---|---|---|---|
| 1 | "What is 2+2?" | phi3:mini (direct) | Simple |
| 2 | "Write a Python function to sort a list" | Beta (OpenRouter) | Code gen |
| 3 | "Review this code for bugs" | Alpha (Groq) | Code review |
| 4 | "Explain quantum computing" | phi3:mini (direct) | Simple Q&A |
| 5 | "Debug this error: ImportError" | Alpha (Groq) | Debugging |
| 6 | "Design a microservice architecture" | Alpha (Groq) | Architecture |
| 7 | "Rename this variable to camelCase" | Delta (Steel) | Quick edit |
| 8 | "Optimize this algorithm for speed" | Gamma (NVIDIA) | Deep analysis |
| 9 | "Write documentation for this API" | Beta (OpenRouter) | Docs |
| 10 | "What's in this image?" | llava:7b (Steel) | Vision |

## Results Format

```json
{
  "test_id": "test-001",
  "timestamp": "2026-08-20T14:00:00Z",
  "request": "What is 2+2?",
  "route": "phi3:mini (direct)",
  "latency_ms": 450,
  "tokens_in": 12,
  "tokens_out": 5,
  "success": true,
  "accuracy": "correct",
  "fallback_used": false,
  "rpd_cost": 0
}
```

## Summary Report

After running all tests, generate:
- Average latency per priest
- Success rate per priest
- Total RPD used
- Classification accuracy
- Overall improvement percentage
