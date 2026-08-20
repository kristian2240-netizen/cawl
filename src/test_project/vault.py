"""C.A.W.L. Vault — long-term memory API (Layer 2).

Reads/writes markdown notes under ``vault/``. Journal is append-only.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from . import config

_SLUG_RE = re.compile(r"[/\\:*?\"<>|\x00-\x1f]")


class VaultError(Exception):
    pass


def _safe_name(name: str) -> str:
    cleaned = _SLUG_RE.sub("_", name).strip().strip(".")
    if not cleaned:
        raise VaultError("empty note name")
    return cleaned


def note_path(folder: str, name: str) -> Path:
    folder_name = _safe_name(folder)
    file_name = _safe_name(name)
    if not file_name.endswith(".md"):
        file_name += ".md"
    path = (config.VAULT_DIR / folder_name / file_name).resolve()
    if not str(path).startswith(str(config.VAULT_DIR.resolve())):
        raise VaultError("path escapes the vault")
    return path


def folders() -> list[str]:
    if not config.VAULT_DIR.exists():
        return []
    return sorted(
        d.name
        for d in config.VAULT_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def list_notes(folder: str | None = None) -> list[dict]:
    notes: list[dict] = []
    base = config.VAULT_DIR
    if folder:
        base = base / _safe_name(folder)
    if not base.exists():
        return notes
    for p in sorted(base.rglob("*.md")):
        notes.append(
            {
                "folder": p.parent.relative_to(config.VAULT_DIR).as_posix(),
                "name": p.name,
                "size": p.stat().st_size,
            }
        )
    return notes


def read_note(folder: str, name: str) -> str:
    path = note_path(folder, name)
    if not path.exists():
        raise VaultError(f"note not found: {folder}/{name}")
    return path.read_text(encoding="utf-8")


def write_note(folder: str, name: str, content: str) -> Path:
    path = note_path(folder, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def journal(entry: str, append: bool = True) -> Path:
    """Append a dated entry to the session log (append-only)."""
    log = config.VAULT_DIR / "06 Journal" / "Session Log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"\n## {stamp}\n\n{entry.strip()}\n"
    if append and log.exists():
        log.write_text(log.read_text(encoding="utf-8").rstrip() + "\n" + block, encoding="utf-8")
    else:
        header = "# Session Log — Append-only\n"
        log.write_text(header + "\nEntries are dated and appended. Never edit or delete old entries.\n" + block, encoding="utf-8")
    return log


def research_save(finding: str, confidence: str = "MEDIUM", source: str = "") -> Path:
    log = config.VAULT_DIR / "03 Research" / "Research Log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    conf = confidence.upper() if confidence.upper() in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM"
    stamp = datetime.now().strftime("%Y-%m-%d")
    lines = [f"## {stamp} — {_first_line(finding)}", ""]
    if source:
        lines.append(f"- **Source:** {source}")
    lines.append(f"- **Finding:** {finding.strip()}")
    lines.append(f"- **Confidence:** {conf}")
    lines.append("")
    log.write_text(log.read_text(encoding="utf-8").rstrip() + "\n" + "\n".join(lines), encoding="utf-8")
    return log


def _first_line(text: str) -> str:
    first = text.strip().splitlines()[0]
    return first[:80] + ("…" if len(first) > 80 else "")
