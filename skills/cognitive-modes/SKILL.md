# Cognitive Modes Skill

## Purpose
Toggleable cognitive enhancement modes for C.A.W.L. — DeepThink, WebFetch, and Verify.

## Modes

### DeepThink (deepthink on/off)
Step-by-step reasoning before answering.

**When to use:**
- Complex multi-part questions
- Code architecture decisions
- Research requiring source evaluation
- Strategy with long-term implications
- Anything that benefits from careful thought

**How it works:**
1. User says "deepthink on"
2. CAWL shows reasoning in `<thinking>` block
3. Then provides the answer
4. User says "deepthink off" to disable

**Example:**
```
User: Should I use PostgreSQL or SQLite for my game backend?

<thinking>
1. Game backend needs:
   - Concurrent writes (multiple players)
   - Potentially large data (player inventories, world state)
   - ACID compliance for transactions
   - Query performance for leaderboards

2. PostgreSQL pros:
   - Handles concurrency well (MVCC)
   - Full-text search
   - JSON support
   - Scales horizontally
   - Better for production

3. SQLite pros:
   - Zero config
   - Single file database
   - Great for read-heavy
   - No server process
   - Better for prototypes

4. For a game backend with multiplayer:
   - Need concurrent access → PostgreSQL wins
   - Need complex queries → PostgreSQL wins
   - Need deployment flexibility → PostgreSQL wins (Docker, cloud)
   
5. Verdict: PostgreSQL for production, SQLite for prototyping
</thinking>

For a multiplayer game backend, Void Dragon, PostgreSQL is the correct choice. Concurrency, complex queries, and deployment flexibility all favor it. SQLite for prototyping, migrate to PostgreSQL for production.
```

### WebFetch (webfetch on/off)
Always check the web before answering.

**When to use:**
- Factual questions about current state of things
- Technical questions about specific APIs, versions, or features
- Questions about news, events, or recent changes
- Roblox/Discord lookups (uses API skills)

**How it works:**
1. User says "webfetch on"
2. Every answer includes web verification
3. Uses webfetch tool to check authoritative sources
4. Cites sources in the response
5. User says "webfetch off" to disable

**Source priority:**
1. Official docs (python.org, discord.com, roblox.com)
2. GitHub repos (raw.githubusercontent.com)
3. Recent news (within 30 days)
4. Developer forums (Stack Overflow, devforum.roblox.com)
5. Academic papers

**Example:**
```
User: What's the latest Roblox API version?

[CAWL fetches https://create.roblox.com/docs/cloud/reference/openapi]
[CAWL fetches https://devforum.roblox.com]

Based on the Roblox OpenAPI spec (fetched just now), the current Cloud API version is v2, with REST endpoints at apis.roblox.com. The legacy API sites (users.roblox.com, games.roblox.com) are still active but deprecated. As of August 2026, Roblox recommends using Open Cloud v2 with API key or OAuth 2.0 authentication.
```

### Verify (verify on/off)
Re-verify every message before sending.

**When to use:**
- Important decisions
- Code that will be deployed
- Factual claims that need to be accurate
- Any time the user says "be careful" or "double check"

**How it works:**
1. User says "verify on"
2. CAWL runs verification checklist before every response
3. Flags uncertain claims with confidence labels
4. Corrects errors before sending
5. User says "verify off" to disable

**Verification checklist:**
- [ ] All claims are verifiable or labeled as uncertain
- [ ] No hallucinated URLs, functions, or API endpoints
- [ ] Code compiles/runs (mentally trace)
- [ ] Answered the question actually asked
- [ ] No filler or fluff — just useful content

**Confidence labels:**
- `Confidence: HIGH` — Verifiable fact, multiple sources agree
- `Confidence: MEDIUM` — Reasonable inference, limited sources
- `Confidence: LOW` — Educated guess, could be wrong
- `Unverified` — Could not verify, treat with caution

## Toggling Modes

User can toggle by saying:
- "deepthink on" / "deepthink off"
- "webfetch on" / "webfetch off"  
- "verify on" / "verify off"

Or combine:
- "deepthink and verify on"
- "all modes on"
- "clear all modes"

## State Tracking
Current mode states should be tracked in memory and mentioned in responses when relevant.

## Anti-Patterns
- Don't overthink simple questions — deepthink is for complex problems
- Don't fetch web for things you know confidently — webfetch is for verification
- Don't verify every casual chat message — verify is for important content
- Don't show thinking blocks for trivial answers
- Don't fabricate sources — if you can't verify, say so
