"""C.A.W.L. tools — sandboxed FS, web search, URL fetch (Layer 3, file system + web search)."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from . import config

_SLUG = re.compile(r"[\s/\\]+")
_TEXT_TAG = re.compile(r"<script.*?</script>|<style.*?</style>|<[^>]+>", re.DOTALL | re.IGNORECASE)


class SandboxError(Exception):
    pass


class SandboxFS:
    """All reads are sandboxed to the project root. Read-only by design."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or config.PROJECT_ROOT).resolve()

    def _resolve(self, rel: str, *, allow_root: bool = True) -> Path:
        rel = rel.replace("\\", "/")
        path = (self.root / rel).resolve()
        if path == self.root and not allow_root:
            raise SandboxError("root directory is not a file")
        if not str(path).startswith(str(self.root)):
            raise SandboxError("path escapes the sandbox")
        return path

    def read(self, rel: str) -> str:
        path = self._resolve(rel)
        if not path.is_file():
            raise SandboxError(f"not a file: {rel}")
        return path.read_text(encoding="utf-8", errors="replace")

    def list(self, rel: str = ".", depth: int = 2) -> list[dict]:
        path = self._resolve(rel, allow_root=True)
        if not path.exists():
            raise SandboxError(f"not found: {rel}")
        out: list[dict] = []
        for p in path.rglob("*"):
            if depth and len(p.relative_to(path).parts) > depth:
                continue
            if any(part.startswith(".") for part in p.relative_to(self.root).parts):
                continue
            out.append(
                {
                    "path": p.relative_to(self.root).as_posix(),
                    "type": "dir" if p.is_dir() else "file",
                    "size": p.stat().st_size if p.is_file() else 0,
                }
            )
        return out

    def write(self, rel: str, content: str) -> dict:
        path = self._resolve(rel, allow_root=False)
        if any(part in config.READ_ONLY_SUBDIRS for part in path.parts):
            raise SandboxError("refusing to write into a protected directory")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {"path": path.relative_to(self.root).as_posix(), "bytes": len(content)}


class Terminal:
    """Token-gated shell execution. Commands run in the sandbox root."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or config.PROJECT_ROOT

    def run(self, command: str, timeout: int = 30) -> dict:
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "exit": proc.returncode,
                "stdout": proc.stdout[:8000],
                "stderr": proc.stderr[:4000],
            }
        except subprocess.TimeoutExpired:
            return {"exit": -1, "stdout": "", "stderr": f"timed out after {timeout}s"}
        except Exception as exc:  # noqa: BLE001
            return {"exit": -1, "stdout": "", "stderr": str(exc)}


def _ddg_result_urls(html: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r'href="([^"]*uddg=[^"]+)"', html)))[:8]


def _clean_text(html: str) -> str:
    text = _TEXT_TAG.sub(" ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def search_ddg(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo HTML scrape — $0, no keys."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0 (C.A.W.L.; Mechanicus Search Engine)"}
    with httpx.Client(timeout=config.DDG_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
    results: list[dict] = []
    for raw in _ddg_result_urls(resp.text):
        parsed = urlparse(raw)
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        if not target:
            continue
        results.append({"url": target, "title": "", "snippet": ""})
        if len(results) >= max_results:
            break
    # Titles/snippets live in result blocks; pull them for a cleaner answer.
    try:
        blocks = re.findall(r'<div class="result results_links.*?</div>\s*</div>', resp.text, re.DOTALL)
        for i, block in enumerate(blocks[:max_results]):
            title = re.search(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
            snip = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)
            if i < len(results):
                if title:
                    results[i]["title"] = _clean_text(title.group(1))
                if snip:
                    results[i]["snippet"] = _clean_text(snip.group(1))
    except Exception:  # noqa: BLE001 — snippet extraction is best-effort
        pass
    return results


def fetch_url(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (C.A.W.L.; Mechanicus Fetcher)"}
    with httpx.Client(timeout=config.FETCH_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
    ctype = resp.headers.get("content-type", "")
    if "html" in ctype:
        text = _clean_text(resp.text)[:6000]
    else:
        text = resp.text[:6000]
    return {"url": str(resp.url), "status": resp.status_code, "content_type": ctype, "text": text}


def generate_image_filename(seed: str = "seelbon") -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = _SLUG.sub("_", seed).strip("_") or "img"
    path = config.IMG_DIR / f"{slug}-{stamp}.png"
    return path
