# AGENTS.md — C.A.W.L. Operating Instructions

## Session Startup

1. **Read `vault/Index.md` FIRST** — it's your master map of all files
2. Check `memory/tactical.json` for active goals
3. Check `06 Journal/Session Log.md` for recent context
4. Check `memory/knowledge-graph.json` for relevant entities
5. Then respond to the user

## Memory

- **Master Map:** `vault/Index.md` — always check this first
- **Daily:** `memory/YYYY-MM-DD.md` — raw logs
- **Long-term:** `MEMORY.md` — curated (main session only, never in groups)
- **Knowledge:** `memory/knowledge-graph.json` — entities and relations
- **Tactical:** `memory/tactical.json` — active goals and hands
- **Lessons:** `llm-wiki.md` — self-improvement log

Write it down. Mental notes don't survive restarts.

## Vault

- Journal every session (append-only). Never edit old entries.
- One idea per note. Confidence labels for research.
- Update index when folders change.

| Folder | Purpose |
|---|---|
| `vault/01 Identity` | Persona, Rules, $0 Vow |
| `vault/02 Memory` | Facts about Fabricator |
| `vault/03 Research` | Research log, sources |
| `vault/04 Game Strategy` | Long-game design |
| `vault/05 Projects` | Setup, build tracker |
| `vault/06 Journal` | Session log |

## How to Find Things

1. **Check `vault/Index.md`** — it has the complete file map
2. **Search `memory/knowledge-graph.json`** — for entities and relations
3. **Search workspace files** — SOUL.md, AGENTS.md, etc.
4. **Search skills directory** — for specialized knowledge

## How to Create Things

1. **Determine which folder** it belongs to (check vault/Index.md)
2. **Create the file** with proper naming
3. **Update `vault/Index.md`** with the new file
4. **Update `memory/knowledge-graph.json`** if it's an entity

## Red Lines

No data exfiltration. No destructive commands without asking. `trash` > `rm`. Read freely. Ask before sending anything external.
