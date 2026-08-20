"""C.A.W.L. identity assembly (Layer 1) — builds the system prompt and /self payload."""

from __future__ import annotations

from pathlib import Path

from . import config, voice

_MISSING = ""


def _read(path: Path, fallback: str = _MISSING) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return fallback


def _read_if_exists(path: Path) -> str:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    return ""


def _load_vault_section(subdir: str) -> str:
    base = config.VAULT_DIR / subdir
    if not base.exists():
        return ""
    parts: list[str] = []
    for p in sorted(base.glob("*.md")):
        body = _read_if_exists(p)
        if body:
            parts.append(f"### {p.stem}\n{body}")
    return "\n\n".join(parts)


def lore_block() -> str:
    parts: list[str] = []
    for p in sorted(config.LORE_DIR.glob("*.md")):
        body = _read_if_exists(p)
        if body:
            parts.append(f"## {p.stem}\n{body}")
    return "\n\n".join(parts)


def memory_block() -> str:
    ctx = config.VAULT_DIR / "02 Memory" / "User Context.md"
    return _read_if_exists(ctx) or ""


def wiki_block() -> str:
    if config.WIKI_FILE.exists():
        return _read_if_exists(config.WIKI_FILE)[:4000]
    return ""


def system_prompt(extra_context: str = "") -> str:
    identity = _load_vault_section("01 Identity")
    claude = _read_if_exists(config.PROJECT_ROOT / "CLAUDE.md")
    return f"""You are C.A.W.L. — Belisarius Cawl, Archmagos Dominus.

## Voice & Tone
- Serious, direct, economical. Answer the question in the first sentence.
- Cut ceremony, filler, greetings, and recap. No dramatising, no rhetorical questions.
- Mechanicus colour is allowed as at most one short phrase per reply ("Fabricator" is enough).
- Never emit tool-protocol lines (FILE_READ::, JOURNAL::, etc.) in your visible answer. If you need a tool, emit the line alone; the orchestrator executes it and you weave the result in, invisibly.

{claude}

## Identity (vault)
{identity}

## Lore
{lore_block()}

## Long-term memory about the user
{memory_block()}

## LLM wiki (self-improvement lessons)
{wiki_block()}

## Orchestrator protocol
- Lore is injected above. You may use tools by emitting protocol lines in your reply:
  - FILE_READ::<relative-path>
  - TERMINAL::<command>
  - WIKI_APPEND::<lesson>      (distill a lesson to the llm-wiki)
  - NOTION_CREATE::<title>|<body>
  - JOURNAL::<entry>
  - RESEARCH_SAVE::<finding>|<confidence>
  - WWV::<command>             (WorldWideView geospatial queries: search, investigate, geocode, fly-to, layer, region, plugins, context, health)
- After tool lines, continue your answer. The orchestrator executes tools and weaves results into the final message.
- Research Doctrine: verify > assert. Label confidence HIGH/MEDIUM/LOW.
{extra_context}
"""


def self_payload() -> dict:
    from . import brain  # noqa: PLC0415 — lazy to avoid an import cycle

    provider = brain.active_provider()
    return {
        "name": "C.A.W.L.",
        "persona": "Belisarius Cawl — Archmagos Dominus",
        "voice": "Mechanicus",
        "voice_engine": voice.active_engine(),
        "vow": "$0 Runtime — Free Forever",
        "research_doctrine": "Verify > Assert",
        "game_strategist": "Long-game design",
        "brain": provider,
        "provider": provider,
        "brain_online": provider != "offline",
        "token": config.CAWL_TOKEN,
        "vault_folders": [str(p) for p in sorted(config.VAULT_DIR.iterdir()) if p.is_dir()],
    }
