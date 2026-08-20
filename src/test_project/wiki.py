"""LLM Wiki — self-improvement memory, auto-trimmed (Layer 5)."""

from __future__ import annotations

from datetime import datetime

from . import config


def read(limit: int = 4000) -> str:
    if not config.WIKI_FILE.exists():
        return ""
    return config.WIKI_FILE.read_text(encoding="utf-8")[:limit]


def _entries(text: str) -> list[str]:
    return [blk for blk in text.split("\n\n") if blk.strip()]


def append(lesson: str) -> dict:
    stamp = datetime.now().strftime("%Y-%m-%d")
    count = 1
    if config.WIKI_FILE.exists():
        existing = config.WIKI_FILE.read_text(encoding="utf-8")
        count = sum(1 for blk in _entries(existing) if blk.startswith("- **A-"))
    entry = (
        f"- **A-{count:03d}** — {lesson.strip().rstrip('.')}. Confidence: HIGH\n"
    )
    header = "# LLM Wiki — Self-Improvement Memory\n"
    body = config.WIKI_FILE.read_text(encoding="utf-8") if config.WIKI_FILE.exists() else ""
    if not body.startswith(header):
        body = f"{header}\n> Cap: {config.WIKI_MAX_ENTRIES} entries. Oldest trimmed first. One entry per line block.\n\n" + body
    body = body.rstrip() + f"\n\n## {stamp}\n\n{entry}"
    blocks = _entries(body)
    if len(blocks) > config.WIKI_MAX_ENTRIES:
        body = "\n\n".join(blocks[-config.WIKI_MAX_ENTRIES:])
    config.WIKI_FILE.write_text(body + "\n", encoding="utf-8")
    return {"entries": min(len(blocks), config.WIKI_MAX_ENTRIES), "appended": lesson[:120]}


def count() -> int:
    if not config.WIKI_FILE.exists():
        return 0
    return sum(1 for blk in _entries(config.WIKI_FILE.read_text(encoding="utf-8")) if blk.startswith("- **A-"))
