# C.A.W.L. Vault — Index

The Vault is C.A.W.L.'s long-term memory. Markdown, one idea per note, YAML frontmatter.

## Map

| Folder | Purpose |
|---|---|
| `01 Identity` | Persona, Rules, $0 Vow, Preferences |
| `02 Memory` | Durable facts about Void Dragon |
| `03 Research` | Research log, sources, findings, confidence labels |
| `04 Game Strategy` | Long-game design notes (Redwood Prison etc.) |
| `05 Projects` | Setup, interface, build tracker |
| `06 Journal` | Session log — append-only, dated entries |
| `99 Templates` | Note template |

## Files

| File | Size | Purpose |
|---|---|---|
| `Index.md` | ~3 KB | This file — master map |
| `01 Identity/Persona.md` | 0.7 KB | C.A.W.L. persona definition |
| `01 Identity/Preferences.md` | 0.5 KB | Void Dragon preferences |
| `01 Identity/Rules.md` | 0.9 KB | Operating rules |
| `01 Identity/Vow.md` | 0.8 KB | $0 Vow doctrine |
| `02 Memory/User Context.md` | 0.5 KB | Durable facts about Void Dragon |
| `03 Research/Research Log.md` | 0.8 KB | Research findings with confidence labels |
| `04 Game Strategy/Redwood Prison.md` | 0.6 KB | Game strategy notes |
| `05 Projects/Build tracker.md` | 0.7 KB | Build progress tracker |
| `05 Projects/Interface.md` | 1.0 KB | Interface design notes |
| `05 Projects/Setup.md` | 0.4 KB | System setup notes |
| `06 Journal/Session Log.md` | 1.4 KB | Append-only session journal |
| `99 Templates/Note Template.md` | 0.2 KB | Template for new notes |

## Workspace Files

| File | Size | Purpose |
|---|---|---|
| `SOUL.md` | ~2 KB | Core identity + Cogitator Network |
| `AGENTS.md` | ~1 KB | Operating instructions |
| `MEMORY.md` | ~1 KB | User context, project history |
| `TOOLS.md` | 0.4 KB | Stack, voice, paths |
| `USER.md` | ~1 KB | Void Dragon profile |
| `SKILLS.md` | 3.4 KB | Reference for 14 removed skills |
| `AGENT-OS-INTEGRATION.md` | 3.7 KB | Cognithor + OpenFang research |
| `cawl-lore.md` | 0.9 KB | Mechanicus lore |
| `cawl-lore-sk.md` | 0.6 KB | Slovak lore |
| `self-knowledge.md` | 0.7 KB | Self-knowledge |
| `strategy.md` | 0.8 KB | Long-game design |
| `llm-wiki.md` | 0.6 KB | Self-improvement log |

## Skills

| Skill | Size | Purpose |
|---|---|---|
| `skills/tech-priests/SKILL.md` | 5.5 KB | 5 priests, benchmarks, routing |
| `skills/brain-routing/SKILL.md` | 6.0 KB | Model routing rules |
| `skills/delegation/SKILL.md` | 3.3 KB | Main Brain dispatch protocol |
| `skills/blender/SKILL.md` | 6.8 KB | Blender 5.1 automation |
| `skills/roblox-api/SKILL.md` | ~5 KB | Roblox investigation API tools (no auth) |
| `skills/memory-system/SKILL.md` | 4.9 KB | 6-tier Cognithor memory |
| `skills/hands/SKILL.md` | 4.8 KB | OpenFang autonomous agents |
| `skills/hands/SCHEDULER.md` | ~1 KB | Hand cron scheduling |
| `skills/knowledge-graph-search/SKILL.md` | ~3 KB | Knowledge graph queries |
| `skills/performance-dashboard/SKILL.md` | ~3 KB | Real-time performance tracking |
| `skills/learning-loops/SKILL.md` | ~3 KB | Automated learning from sessions |
| `skills/efficiency/SKILL.md` | 2.7 KB | Response optimization |
| `skills/mechanicus-voice/SKILL.md` | 2.0 KB | TTS voice config |
| `skills/vault-ops/SKILL.md` | 1.9 KB | Vault operations |
| `skills/performance/SKILL.md` | 2.5 KB | Performance measurement |

## Memory

| File | Size | Purpose |
|---|---|---|
| `memory/knowledge-graph.json` | ~10 KB | 21 entities, 20 relations |
| `memory/tactical.json` | ~4 KB | Active goals + hands status |
| `memory/benchmark-results.json` | ~4 KB | Provider benchmarks (all GREEN) |
| `memory/performance-baseline.json` | 3.7 KB | Test results |
| `memory/system-improvements.md` | ~4 KB | Priority fixes, score 85/100 |
| `memory/claude-code-evaluation.md` | 2.6 KB | CCR analysis |
| `memory/known-apis.json` | ~5 KB | 12 APIs monitored |
| `memory/dashboard/system-status.json` | ~4 KB | Live performance data |
| `memory/learning/error-patterns.json` | ~1 KB | Known errors and fixes |
| `memory/learning/user-patterns.json` | ~1 KB | User behavior patterns |
| `memory/learning/provider-patterns.json` | ~1 KB | Provider reliability data |

## Hands

| Hand | Status | Schedule | Provider |
|---|---|---|---|
| `hands/researcher/` | Active | On-demand | Groq (Alpha) |
| `hands/collector/` | Active | Every 6 hours | phi3:mini + Groq |
| `hands/forecaster/` | Active | Weekly Monday | Groq (Alpha) |
| `hands/code-reviewer/` | Active | On-demand | Groq (Alpha) |
| `hands/api-monitor/` | Active | Every 4 hours | phi3:mini |

## Providers (6 Active, 2 Pending)

| Provider | Latency | Status | Notes |
|---|---|---|---|
| Groq | 393ms | GREEN | Fastest, primary |
| Mistral | 443ms | GREEN | Overflow, multilingual |
| Steel | 120ms warm | GREEN | Local, unlimited |
| NVIDIA | 543ms | GREEN | Backup cloud |
| OpenRouter | 915ms | GREEN | Free models: Gemma 4 26B, GPT-OSS 20B, Nemotron 3 Nano 30B, Nemotron 3 Super 120B |
| SambaNova | ~200ms | NEEDS KEY | 70B at 400+ tok/s |
| Google AI | ~300ms | NEEDS KEY | 1M context, 1500 RPD |

## Experimental APIs (Monitored)

| API | Status | Free Tier | Notes |
|---|---|---|---|
| HuggingFace | Unknown | Rate limited | Check every 4h |
| Google AI Studio | Unknown | 1500 RPD | Check every 4h |
| Cloudflare Workers AI | Unknown | 10000 RPD | Check every 4h |
| SambaNova | Unknown | 100 RPD | Check every 4h |
| Together.ai | Unknown | Free credits | Check every 4h |
| Fireworks AI | Unknown | Free tier | Check every 4h |
| Cohere | Unknown | Free tier | Check every 4h |
| Replicate | Unknown | Free tier | Check every 4h |

## System Score: 85/100

- Routing: 9/10
- Memory: 7/10
- Hands: 7/10 (+1)
- Learning: 7/10 (+5)
- Monitoring: 8/10 (+3)
- Error recovery: 6/10 (+1)
- Documentation: 9/10
- Provider health: 10/10
- User identity: 10/10
- API awareness: 8/10 (new)

## Maintenance rules

- Append to `06 Journal/Session Log.md` at the end of every session. Never edit old entries.
- Keep `02 Memory/User Context.md` lean: durable facts only.
- One idea per note. Use the template in `99 Templates/Note Template.md`.
- Research entries get a confidence label (HIGH / MEDIUM / LOW).
- This Index is the first stop. If a folder changes, update this map.

## How to Use This Index

**When C.A.W.L. starts a session:**
1. Read this Index first
2. Check `SOUL.md` for identity
3. Check `memory/tactical.json` for active goals
4. Check `memory/dashboard/system-status.json` for provider health
5. Check `memory/learning/error-patterns.json` for things to avoid
6. Check `06 Journal/Session Log.md` for recent context
7. Check `memory/knowledge-graph.json` for relevant entities

**When C.A.W.L. needs to find something:**
1. Search this Index for the file
2. Read the relevant file
3. If not found, search `memory/knowledge-graph.json`
4. If still not found, search workspace files

**When C.A.W.L. creates new content:**
1. Determine which folder it belongs to
2. Create the file with proper naming
3. Update this Index with the new file
4. Update `memory/knowledge-graph.json` if it's an entity
