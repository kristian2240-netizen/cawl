# Hands Cron Scheduler

## How It Works

Hands run on schedules defined in their `HAND.toml`. The scheduler checks every 15 minutes and triggers hands when their cron matches.

## Cron Expressions

| Expression | Meaning |
|---|---|
| `on-demand` | Manual only, never auto-runs |
| `*/15 * * * *` | Every 15 minutes |
| `0 */6 * * *` | Every 6 hours (00:00, 06:00, 12:00, 18:00) |
| `0 9 * * 1` | Every Monday at 09:00 |
| `0 9 * * 1-5` | Weekdays at 09:00 |
| `30 8 * * *` | Daily at 08:30 |

## Hand Schedules

| Hand | Schedule | Last Run | Next Run |
|---|---|---|---|
| Researcher | `on-demand` | Never | Manual only |
| Collector | `0 */6 * * *` | Never | Next 6-hour mark |
| Forecaster | `0 9 * * 1` | Never | Next Monday 09:00 |
| Code Reviewer | `on-demand` | Never | Manual only |

## How to Run a Hand Manually

```bash
# From OpenClaw, tell C.A.W.L.:
"Run the Researcher hand on topic X"
"Trigger the Collector hand now"
"Run code review on file.py"
```

## How to Change Schedules

Edit the `HAND.toml` file for the hand you want to change:
```toml
schedule = "0 */4 * * *"  # Every 4 hours
```

## Status Tracking

Hand status is tracked in `memory/tactical.json` under `hands_status`.

## Cron Implementation

Since OpenClaw doesn't have built-in cron, the scheduler works through:
1. **Session startup check:** C.A.W.L. checks `memory/tactical.json` for due hands
2. **Manual triggers:** User can trigger any hand at any time
3. **Collector auto-run:** Collector runs every 6 hours via session check
4. **Forecaster auto-run:** Forecaster runs every Monday via session check

## Running a Hand

When a hand is triggered:
1. Read `hands/{name}/HAND.toml` for config
2. Read `hands/{name}/system-prompt.md` for instructions
3. Execute the pipeline (websearch, analysis, etc.)
4. Write output to `hands/{name}/output/`
5. Update `memory/tactical.json` with run stats
6. Update `memory/knowledge-graph.json` if new entities found
