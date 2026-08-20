---
name: vault-ops
description: "C.A.W.L. Vault operations — read, write, journal, research save. Use when the Fabricator asks to save notes, log sessions, record research findings, or manage the vault."
user-invocable: true
---

# Vault Operations

C.A.W.L.'s long-term memory system. Markdown files with YAML frontmatter.

## Vault Structure

```
vault/
  Index.md              — Map of the vault (read this first)
  01 Identity/          — Persona, Rules, $0 Vow, Preferences
  02 Memory/            — Durable facts about the Fabricator
  03 Research/          — Research log with confidence labels
  04 Game Strategy/     — Long-game design notes
  05 Projects/          — Setup, interface, build tracker
  06 Journal/           — Session log (append-only)
  99 Templates/         — Note template
```

## Operations

### Journal Entry (append-only)
Append a dated entry to `vault/06 Journal/Session Log.md`. Never edit old entries.

Format:
```markdown
## YYYY-MM-DD HH:MM

- What happened in this session.
```

### Research Save
Append a finding to `vault/03 Research/Research Log.md` with a confidence label.

Format:
```markdown
## YYYY-MM-DD — Title

- **Confidence:** HIGH / MEDIUM / LOW
- **Finding:** What was discovered
- **Source:** Where it came from
```

### Read a Note
Read any file under `vault/`. Start with `vault/Index.md` to find the right folder.

### Write a Note
Write to the appropriate vault folder. Follow the template in `vault/99 Templates/Note Template.md`:
- YAML frontmatter: type, tags, updated
- Fields: Title, Date, Source, Confidence, Summary, Details, Sources

### User Context
Durable facts about the Fabricator live in `vault/02 Memory/User Context.md`. Keep it lean. One fact per line.

## Rules

- **Append-only** for journal entries. Never edit or delete old entries.
- **One idea per note.** Don't combine unrelated concepts.
- **Confidence labels** on all research entries.
- **Update the Index** if you add a new folder.
