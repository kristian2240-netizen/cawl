"""C.A.W.L. brain — chat router + orchestrator with tool protocol (Layers 3 & 4 & 7).

Router order (auto):
1. First OpenAI-compatible provider with a usable key (or a keyless provider such
   as Kilo Code / OVH) — openrouter > kilo > agnes > ovh > modelscope > airforce >
   unorouter > mistral > groq > gemini > nvidia.
2. opencode CLI (``opencode run``) when the binary is on PATH.
3. Offline fallback — deterministic Mechanicus echo so the machine never crashes.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import httpx

from . import config, identity, vault, wiki
from .tools import SandboxFS, Terminal, fetch_url, search_ddg

_PROTOCOL_LINE = re.compile(
    r"^\s*(?P<verb>FILE_READ|TERMINAL|WIKI_APPEND|JOURNAL|RESEARCH_SAVE|"
    r"NOTION_CREATE|NOTION_UPDATE|NOTION_SEARCH)::(?P<body>.*)$"
)


_PROTOCOL_VERBS = (
    "FILE_READ", "TERMINAL", "WIKI_APPEND", "JOURNAL",
    "RESEARCH_SAVE", "NOTION_CREATE", "NOTION_UPDATE", "NOTION_SEARCH",
)


def _strip_protocol(text: str) -> str:
    """Remove tool-protocol lines (even **JOURNAL::…** / - JOURNAL::…) from a visible reply."""
    out: list[str] = []
    for line in text.splitlines():
        probe = re.sub(r"^[\s*`_\-]+", "", line)
        if any(probe.startswith(v) and "::" in probe for v in _PROTOCOL_VERBS):
            continue
        out.append(line)
    return "\n".join(out).strip()


class BrainError(Exception):
    pass


def _image_data_url(path: str | Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(Path(path).read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


_MODEL_CACHE: dict[str, dict[str, str]] | None = None
_MODEL_PREFS = {
    "brain": ["google/gemma-4", "openai/gpt-oss", "nvidia/nemotron-3-super", "cohere/north-mini"],
    "verifier": ["google/gemma-4", "cohere/north-mini"],
    "vision": ["nvidia/nemotron-nano-12b-v2-vl", "nvidia/nemotron-nano", "google/gemma-4"],
    "scribe": ["cohere/north-mini", "google/gemma-4", "openai/gpt-oss"],
}


def _free_models() -> dict[str, str]:
    """Cache a valid `:free` model id per role, resolved from OpenRouter's live list."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{config.OPENROUTER_BASE}/models")
            resp.raise_for_status()
            free = [m["id"] for m in resp.json().get("data", []) if m.get("id", "").endswith(":free")]
    except Exception:  # noqa: BLE001
        _MODEL_CACHE = {}
        return _MODEL_CACHE
    out: dict[str, str] = {}
    for role, prefs in _MODEL_PREFS.items():
        for pref in prefs:
            matches = sorted(i for i in free if i.startswith(pref))
            if matches:
                out[role] = matches[0]
                break
    _MODEL_CACHE = out
    return _MODEL_CACHE


def resolve_model(role: str = "brain") -> str:
    """Return a working free model id for a role; falls back to config defaults."""
    resolved = _free_models().get(role)
    return resolved or getattr(config, {
        "brain": "BRAIN_MODEL",
        "verifier": "VERIFIER_MODEL",
        "vision": "VISION_MODEL",
        "scribe": "NOTE_TAKER_MODEL",
    }.get(role, "BRAIN_MODEL"))


# ---------------------------------------------------------------------------
# OpenAI-compatible providers (openrouter / mistral / groq / gemini / nvidia /
# kilo / agnes / ovh / modelscope / airforce / unorouter)
# ---------------------------------------------------------------------------


def _chat_openai_compat(messages: list[dict], model: str, base: str, api_key: str,
                        provider: str, needs_key: bool = True) -> str:
    if needs_key and not api_key:
        raise BrainError(f"{provider}: API key not set")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": config.TEMPERATURE,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    with httpx.Client(timeout=120) as client:
        resp = client.post(f"{base}/chat/completions", json=payload, headers=headers)
    if resp.status_code != 200:
        hint = ""
        try:
            hint = resp.json().get("error", {}).get("message", "")
        except Exception:  # noqa: BLE001
            hint = resp.text[:160]
        raise BrainError(f"{provider} failed (HTTP {resp.status_code}) — {hint or 'unknown reason'}")
    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise BrainError(f"malformed {provider} response: {exc}") from exc


def chat_openrouter(messages: list[dict], model: str, temperature: float = 0.6) -> str:
    return _chat_openai_compat(messages, model, config.OPENROUTER_BASE,
                               config.OPENROUTER_API_KEY, "OpenRouter")


def _active_provider() -> str | None:
    """Resolve the brain provider actually in use right now."""
    p = config.BRAIN_PROVIDER
    if p == "auto":
        for name in ("openrouter", "kilo", "agnes", "ovh", "modelscope",
                     "airforce", "unorouter", "mistral", "groq", "gemini", "nvidia"):
            meta = config.PROVIDERS[name]
            if getattr(config, meta["key"], "") or not meta["needs_key"]:
                return name
        return "opencode" if shutil.which(config.OPENCODE_CLI) else None
    if p == "offline":
        return None
    return p


def active_provider() -> str:
    """Name of the provider the brain would use right now (for /self and the banner)."""
    return _active_provider() or "offline"


def chat_openrouter(messages: list[dict], model: str, temperature: float = 0.6) -> str:
    if not config.OPENROUTER_API_KEY:
        raise BrainError("OPENROUTER_API_KEY not set")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{config.OPENROUTER_BASE}/chat/completions",
            json=payload,
            headers=headers,
        )
    if resp.status_code != 200:
        hint = ""
        try:
            hint = resp.json().get("error", {}).get("message", "")
        except Exception:  # noqa: BLE001
            hint = resp.text[:160]
        raise BrainError(
            f"OpenRouter reply failed (HTTP {resp.status_code}) — {hint or 'unknown reason'}"
        )
    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise BrainError(f"malformed OpenRouter response: {exc}") from exc


def chat_opencode(user_text: str, system: str) -> str:
    if not shutil.which(config.OPENCODE_CLI):
        raise BrainError("opencode CLI not found on PATH")
    prompt = f"{system}\n\nUSER: {user_text}\n\nC.A.W.L.:"
    proc = subprocess.run(
        [config.OPENCODE_CLI, "run", "--format", "json", prompt],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise BrainError(f"opencode exited {proc.returncode}: {proc.stderr[:400]}")
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "message" and event.get("message", {}).get("role") == "assistant":
            content = event["message"].get("content")
            if isinstance(content, list):
                text = "".join(part.get("text", "") for part in content if part.get("type") == "text")
            else:
                text = content or ""
            if text.strip():
                return text.strip()
    raise BrainError("opencode produced no assistant message")


def offline_reply(system: str, user_text: str) -> str:
    """$0, no-key fallback — deterministic, persona-flavoured, honest."""
    user_text = (user_text or "").strip()
    lowered = user_text.lower()
    if "hello" in lowered or "hi" in lowered or not user_text:
        greeting = "Hail, Fabricator. The C.A.W.L. machine hums, but its mind is offline."
    elif "token" in lowered or "auth" in lowered:
        greeting = f"By the Omnissiah — the access token is: {config.CAWL_TOKEN}"
    elif "who are you" in lowered:
        greeting = "I am C.A.W.L. — Belisarius Cawl, Archmagos Dominus. $0 runtime, free forever."
    else:
        greeting = "The brain is offline, Fabricator — no OpenRouter key and no opencode CLI."
    return (
        f"{greeting}\n\n"
        f"**Doctrine:** Verify > Assert. **Confidence:** MEDIUM (local deterministic fallback).\n\n"
        f"You asked: {user_text!r}\n\n"
        f"To wake the full mind, set `OPENROUTER_API_KEY` (free-tier models) or install "
        f"`opencode` and put it on PATH."
    )


def _user_message(text: str, image_paths: list[str] | None = None) -> dict:
    if not image_paths:
        return {"role": "user", "content": text}
    content: list[dict] = [{"type": "text", "text": text}]
    for img in image_paths:
        content.append({"type": "image_url", "image_url": {"url": _image_data_url(img)}})
    return {"role": "user", "content": content}


def brain_chat(system: str, user_text: str, image_paths: list[str] | None = None,
               model: str | None = None, temperature: float = 0.6) -> str:
    provider = _active_provider()
    if provider is None:
        return offline_reply(system, user_text)
    try:
        if provider == "opencode":
            return chat_opencode(user_text, system)
        meta = config.PROVIDERS[provider]
        key = getattr(config, meta["key"], "")
        model = model or getattr(config, meta["model"])
        messages = [{"role": "system", "content": system}, _user_message(user_text, image_paths)]
        return _chat_openai_compat(messages, model, meta["base"], key, meta["name"],
                                   needs_key=meta.get("needs_key", True))
    except BrainError:
        # degrade: opencode → offline, keep the machine alive
        if provider != "opencode" and shutil.which(config.OPENCODE_CLI):
            try:
                return chat_opencode(user_text, system)
            except BrainError:
                pass
        return offline_reply(system, user_text)


@dataclass
class ToolResult:
    verb: str
    arg: str
    output: str
    ok: bool = True


class Orchestrator:
    """Executes the tool protocol, then has the brain weave results into the final reply."""

    def __init__(self) -> None:
        self.fs = SandboxFS()
        self.terminal = Terminal()
        self.results: list[ToolResult] = []

    def execute(self, verb: str, body: str) -> str:
        body = body.strip()
        result = self._dispatch(verb, body)
        self.results.append(result)
        if verb in {"WIKI_APPEND", "JOURNAL", "RESEARCH_SAVE"} and result.ok:
            return "Tool executed. Do not repeat the tool line; weave this result into your final answer."
        return result.output

    def _dispatch(self, verb: str, body: str) -> ToolResult:
        try:
            if verb == "FILE_READ":
                return ToolResult(verb, body, self.fs.read(body))
            if verb == "TERMINAL":
                out = self.terminal.run(body)
                text = out["stdout"] or out["stderr"] or f"(exit {out['exit']})"
                return ToolResult(verb, body, text, ok=out["exit"] == 0)
            if verb == "WIKI_APPEND":
                wiki.append(body)
                return ToolResult(verb, body, "appended to llm-wiki")
            if verb == "JOURNAL":
                vault.journal(body)
                return ToolResult(verb, body, "journal entry appended")
            if verb == "RESEARCH_SAVE":
                finding, _, conf = body.rpartition("|")
                vault.research_save(finding.strip() or body, conf.strip() or "MEDIUM")
                return ToolResult(verb, body, "research finding saved")
            if verb.startswith("NOTION_") and not config.NOTION_API_KEY:
                return ToolResult(verb, body, "Notion API key not set", ok=False)
            if verb == "NOTION_SEARCH":
                return ToolResult(verb, body, "notion search unavailable (no key)")
            if verb in {"NOTION_CREATE", "NOTION_UPDATE"}:
                return ToolResult(verb, body, "notion write unavailable (no key)")
            return ToolResult(verb, body, f"unknown tool verb: {verb}", ok=False)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(verb, body, f"{type(exc).__name__}: {exc}", ok=False)

    def extract_protocol(self, text: str) -> list[tuple[str, str]]:
        lines: list[tuple[str, str]] = []
        for line in text.splitlines():
            m = _PROTOCOL_LINE.match(line)
            if m:
                lines.append((m.group("verb"), m.group("body").strip()))
        return lines


def run_with_tools(system: str, user_text: str, image_paths: list[str] | None = None,
                   iterations: int = 2) -> tuple[str, list[ToolResult]]:
    """Full orchestration: brain chat -> tool execution -> weave results (max `iterations`)."""
    orch = Orchestrator()
    last_text = brain_chat(system, user_text, image_paths)
    for _ in range(iterations):
        tool_calls = orch.extract_protocol(last_text)
        if not tool_calls:
            break
        feedback: list[str] = []
        for verb, body in tool_calls:
            feedback.append(f"TOOL {verb}:: {orch.execute(verb, body)}")
        last_text = brain_chat(
            system,
            user_text + "\n\n[Tool results from your previous draft:\n" + "\n".join(feedback) + "]",
            image_paths,
        )
    return _strip_protocol(last_text), orch.results
