"""C.A.W.L. — configuration, paths, security token, runtime settings.

Resolution order for every setting: process env > <project>/.cawl-data/settings.json >
<project>/.env > default. The settings file is writable at runtime via update_settings()
and is the backing store for the CONFIG page in the frontend.
"""

from __future__ import annotations

import json
import os
import secrets
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]          # <project>/
PACKAGE_DIR = Path(__file__).resolve().parent               # <project>/src/test_project
VAULT_DIR = PROJECT_ROOT / "vault"
LORE_DIR = PROJECT_ROOT / "lore"
WIKI_FILE = PROJECT_ROOT / "llm-wiki.md"
TOKEN_FILE = PROJECT_ROOT / ".cawl-token"
DATA_DIR = PROJECT_ROOT / ".cawl-data"
AUDIO_DIR = DATA_DIR / "audio"
IMG_DIR = DATA_DIR / "img"
LOG_DIR = DATA_DIR / "logs"
SETTINGS_FILE = DATA_DIR / "settings.json"

SERVER_HOST = os.getenv("CAWL_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("CAWL_PORT", "8123"))

# ---------------------------------------------------------------------------
# .env + settings.json fallback
# ---------------------------------------------------------------------------


def _load_dotenv() -> dict[str, str]:
    out: dict[str, str] = {}
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return out
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key:
                out[key] = val
    except OSError:
        pass
    return out


def _load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


_DOTENV = _load_dotenv()
_SETTINGS = _load_settings()


def _env(name: str, default: str = "") -> str:
    """Value resolution: process env wins, then settings.json, then .env, then default."""
    val = os.getenv(name)
    if val is None and name in _SETTINGS:
        val = _SETTINGS[name]
    if val is None:
        val = _DOTENV.get(name, default)
    return val

# ---------------------------------------------------------------------------
# Token (auth) — auto-generated, mirrors the original ..cawl-token behaviour.
# ---------------------------------------------------------------------------


def load_or_create_token() -> str:
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
    return token


CAWL_TOKEN = load_or_create_token()

# Read-only by design: the brain may never write/delete outside the sandbox.
SANDBOX_DIR = PROJECT_ROOT
READ_ONLY_SUBDIRS = {".venv", ".git", "node_modules", "__pycache__", ".cawl-data"}

for _d in (DATA_DIR, AUDIO_DIR, IMG_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Brain / providers
# ---------------------------------------------------------------------------
OPENROUTER_API_KEY = _env("OPENROUTER_API_KEY").strip()
OPENROUTER_BASE = _env("OPENROUTER_BASE", "https://openrouter.ai/api/v1")

MISTRAL_API_KEY = _env("MISTRAL_API_KEY").strip()
MISTRAL_BASE = _env("MISTRAL_BASE", "https://api.mistral.ai/v1")
MISTRAL_MODEL = _env("CAWL_MISTRAL_MODEL", "mistral-small-latest")

GROQ_API_KEY = _env("GROQ_API_KEY").strip()
GROQ_BASE = _env("GROQ_BASE", "https://api.groq.com/openai/v1")
GROQ_MODEL = _env("CAWL_GROQ_MODEL", "llama-3.3-70b-versatile")

GEMINI_API_KEY = _env("GEMINI_API_KEY").strip()
GEMINI_BASE = _env("GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta/openai")
GEMINI_MODEL = _env("CAWL_GEMINI_MODEL", "gemini-3.5-flash")

NVIDIA_API_KEY = _env("NVIDIA_API_KEY").strip()
NVIDIA_BASE = _env("NVIDIA_BASE", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = _env("CAWL_NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

# Kilo Code — free tier is anonymous (no key needed), 200 req/hr/IP per free model.
KILO_API_KEY = _env("KILO_API_KEY").strip()
KILO_BASE = _env("KILO_BASE", "https://api.kilo.ai/api/gateway")
KILO_MODEL = _env("CAWL_KILO_MODEL", "kilo-auto/free")

# Agnes AI — free forever tier (agnese-2.5-flash 512K ctx); key from registration.
AGNES_API_KEY = _env("AGNES_API_KEY").strip()
AGNES_BASE = _env("AGNES_BASE", "https://apihub.agnes-ai.com/v1")
AGNES_MODEL = _env("CAWL_AGNES_MODEL", "agnes-2.5-flash")

# OVH AI Endpoints — anonymous free tier (no key), ~2 req/min/model/IP.
OVH_API_KEY = _env("OVH_API_KEY").strip()
OVH_BASE = _env("OVH_BASE", "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1")
OVH_MODEL = _env("CAWL_OVH_MODEL", "llama-3.1-8b-instruct")

# ModelScope (Alibaba) — ms- prefixed token; ~2,000 RPD total, <=500 RPD per model.
# Tokens are site-scoped: a modelscope.ai token only works on api-inference.modelscope.ai,
# a modelscope.cn token only on api-inference.modelscope.cn. Requires Alibaba Cloud
# account binding + real-name verification before inference is enabled.
MODELSCOPE_API_KEY = _env("MODELSCOPE_API_KEY").strip()
MODELSCOPE_BASE = _env("MODELSCOPE_BASE", "https://api-inference.modelscope.ai/v1")
MODELSCOPE_MODEL = _env("CAWL_MODELSCOPE_MODEL", "Qwen/Qwen3.5-35B-A3B")

# Api.Airforce — free plan: 1 RPM / 1,000 RPD.
AIRFORCE_API_KEY = _env("AIRFORCE_API_KEY").strip()
AIRFORCE_BASE = _env("AIRFORCE_BASE", "https://api.airforce/v1")
AIRFORCE_MODEL = _env("CAWL_AIRFORCE_MODEL", "gpt-oss-120b")

# UnoRouter — free lane ~1 req/min/user; free models carry a :free suffix.
UNOROUTER_API_KEY = _env("UNOROUTER_API_KEY").strip()
UNOROUTER_BASE = _env("UNOROUTER_BASE", "https://api.unorouter.com/v1")
UNOROUTER_MODEL = _env("CAWL_UNOROUTER_MODEL", "step-3.7-flash:free")

# DSH — DeepSeek Harness via ds-free-api proxy (free web-chat backend)
DSH_API_KEY = _env("DSH_API_KEY", "sk-cawl-free-2026").strip()
DSH_BASE = _env("DSH_BASE", "http://127.0.0.1:5317/v1").strip()
DSH_MODEL = _env("CAWL_DSH_MODEL", "deepseek-default")

OPENCODE_CLI = _env("CAWL_OPENCODE", "opencode")

# brain provider: "auto" | "opencode" | "openrouter" | "mistral" | "groq" | "gemini" | "nvidia" | "offline"
BRAIN_PROVIDER = _env("CAWL_BRAIN_PROVIDER", "auto")
TEMPERATURE = float(_env("CAWL_TEMPERATURE", "0.6"))

# Free-tier defaults (resolve dynamically against OpenRouter; these are the fallbacks)
BRAIN_MODEL = _env("CAWL_BRAIN_MODEL", "google/gemma-4-26b-a4b-it:free")
VERIFIER_MODEL = _env("CAWL_VERIFIER_MODEL", "google/gemma-4-26b-a4b-it:free")
VISION_MODEL = _env("CAWL_VISION_MODEL", "nvidia/nemotron-nano-12b-v2-vl:free")
NOTE_TAKER_MODEL = _env("CAWL_NOTETAKER_MODEL", "cohere/north-mini-code:free")

PROVIDERS: dict[str, dict] = {
    "opencode": {
        "name": "opencode CLI (local)", "key": "OPENCODE_CLI", "needs_key": False,
        "base": "", "model": "OPENCODE_CLI", "key_label": "CLI name (default: opencode)",
    },
    "openrouter": {
        "name": "OpenRouter", "key": "OPENROUTER_API_KEY", "needs_key": True,
        "base": "https://openrouter.ai/api/v1", "model": "BRAIN_MODEL",
        "key_label": "OPENROUTER_API_KEY",
    },
    "mistral": {
        "name": "Mistral AI", "key": "MISTRAL_API_KEY", "needs_key": True,
        "base": "https://api.mistral.ai/v1", "model": "MISTRAL_MODEL",
        "key_label": "MISTRAL_API_KEY",
    },
    "groq": {
        "name": "Groq", "key": "GROQ_API_KEY", "needs_key": True,
        "base": "https://api.groq.com/openai/v1", "model": "GROQ_MODEL",
        "key_label": "GROQ_API_KEY",
    },
    "gemini": {
        "name": "Google Gemini", "key": "GEMINI_API_KEY", "needs_key": True,
        "base": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "GEMINI_MODEL",
        "key_label": "GEMINI_API_KEY",
    },
    "nvidia": {
        "name": "NVIDIA NIM", "key": "NVIDIA_API_KEY", "needs_key": True,
        "base": "https://integrate.api.nvidia.com/v1", "model": "NVIDIA_MODEL",
        "key_label": "NVIDIA_API_KEY",
    },
    "kilo": {
        "name": "Kilo Code", "key": "KILO_API_KEY", "needs_key": False,
        "base": "https://api.kilo.ai/api/gateway", "model": "KILO_MODEL",
        "key_label": "KILO_API_KEY",
    },
    "agnes": {
        "name": "Agnes AI", "key": "AGNES_API_KEY", "needs_key": True,
        "base": "https://apihub.agnes-ai.com/v1", "model": "AGNES_MODEL",
        "key_label": "AGNES_API_KEY",
    },
    "ovh": {
        "name": "OVH AI Endpoints", "key": "OVH_API_KEY", "needs_key": False,
        "base": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1", "model": "OVH_MODEL",
        "key_label": "OVH_API_KEY",
    },
    "modelscope": {
        "name": "ModelScope", "key": "MODELSCOPE_API_KEY", "needs_key": True,
        "base": "https://api-inference.modelscope.cn/v1", "model": "MODELSCOPE_MODEL",
        "key_label": "MODELSCOPE_API_KEY",
    },
    "airforce": {
        "name": "Api.Airforce", "key": "AIRFORCE_API_KEY", "needs_key": True,
        "base": "https://api.airforce/v1", "model": "AIRFORCE_MODEL",
        "key_label": "AIRFORCE_API_KEY",
    },
    "unorouter": {
        "name": "UnoRouter", "key": "UNOROUTER_API_KEY", "needs_key": True,
        "base": "https://api.unorouter.com/v1", "model": "UNOROUTER_MODEL",
        "key_label": "UNOROUTER_API_KEY",
    },
    "dsh": {
        "name": "DeepSeek Harness", "key": "DSH_API_KEY", "needs_key": True,
        "base": "http://127.0.0.1:5317/v1", "model": "DSH_MODEL",
        "key_label": "DSH_API_KEY",
    },
}

NOTION_API_KEY = _env("NOTION_API_KEY").strip()
NOTION_ROOT_PAGE = _env("NOTION_ROOT_PAGE").strip()

# WorldWideView integration
WWV_URL = _env("WWV_URL", "http://localhost:3000").strip()
WWV_ENGINE_URL = _env("WWV_ENGINE_URL", "http://localhost:5000").strip()
WWV_API_KEY = _env("WWV_API_KEY").strip()

# Voice engine — engine: "auto" (kokoro if installed, else elevenlabs if key, else edge), or forced
TTS_ENGINE = _env("CAWL_TTS_ENGINE", "auto")
TTS_VOICE = _env("CAWL_TTS_VOICE", "en-US-AndrewMultilingualNeural")
TTS_RATE = _env("CAWL_TTS_RATE", "-18%")
TTS_PITCH = _env("CAWL_TTS_PITCH", "-8Hz")

# Kokoro (local, free, Apache 2.0 — default when the model is present)
KOKORO_MODEL = _env("CAWL_KOKORO_MODEL", str(DATA_DIR / "tts" / "kokoro-v1.0.onnx"))
KOKORO_VOICES = _env("CAWL_KOKORO_VOICES", str(DATA_DIR / "tts" / "voices-v1.0.bin"))
KOKORO_VOICE = _env("CAWL_KOKORO_VOICE", "am_onyx")   # am_onyx: deepest male voice
KOKORO_SPEED = float(_env("CAWL_KOKORO_SPEED", "0.96"))
KOKORO_PITCH = float(_env("CAWL_KOKORO_PITCH", "1.16"))  # >1 = deeper (resample down)
KOKORO_DEPTH = float(_env("CAWL_KOKORO_DEPTH", "1.0"))  # 0.5-1.5 machine depth (darkening/resonance)

# ElevenLabs (deep, cinematic machine voice — used when a key is present)
ELEVENLABS_API_KEY = _env("ELEVENLABS_API_KEY").strip()
ELEVENLABS_VOICE_ID = _env("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")  # Brian
ELEVENLABS_MODEL = _env("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_BASE = _env("ELEVENLABS_BASE", "https://api.elevenlabs.io/v1")

# Voice DSP flags
VOICE_DSP_ENABLED = _env("CAWL_VOICE_DSP", "1") == "1"

# Avatar image (optional) — absolute path to a PNG/JPG rendered instead of the SVG figure
AVATAR_IMAGE = _env("CAWL_AVATAR_IMAGE", "").strip()

# Web search / misc
DDG_TIMEOUT = 12
FETCH_TIMEOUT = 15
WIKI_MAX_ENTRIES = 200

# Brain readiness (informational; identity/banner compute the live value)
BRAIN_MODE = "offline"

# ---------------------------------------------------------------------------
# Runtime settings — the CONFIG page writes these to .cawl-data/settings.json
# ---------------------------------------------------------------------------

SETTING_KEYS: dict[str, type] = {
    "BRAIN_PROVIDER": str,
    "BRAIN_MODEL": str,
    "MISTRAL_MODEL": str,
    "GROQ_MODEL": str,
    "GEMINI_MODEL": str,
    "NVIDIA_MODEL": str,
    "KILO_MODEL": str,
    "AGNES_MODEL": str,
    "OVH_MODEL": str,
    "MODELSCOPE_MODEL": str,
    "MODELSCOPE_BASE": str,
    "AIRFORCE_MODEL": str,
    "UNOROUTER_MODEL": str,
    "TEMPERATURE": float,
    "OPENROUTER_API_KEY": str,
    "MISTRAL_API_KEY": str,
    "GROQ_API_KEY": str,
    "GEMINI_API_KEY": str,
    "NVIDIA_API_KEY": str,
    "KILO_API_KEY": str,
    "AGNES_API_KEY": str,
    "OVH_API_KEY": str,
    "MODELSCOPE_API_KEY": str,
    "AIRFORCE_API_KEY": str,
    "UNOROUTER_API_KEY": str,
    "DSH_API_KEY": str,
    "DSH_BASE": str,
    "DSH_MODEL": str,
    "OPENCODE_CLI": str,
    "TTS_ENGINE": str,
    "TTS_VOICE": str,
    "TTS_RATE": str,
    "TTS_PITCH": str,
    "KOKORO_VOICE": str,
    "KOKORO_SPEED": float,
    "KOKORO_PITCH": float,
    "KOKORO_DEPTH": float,
    "ELEVENLABS_API_KEY": str,
    "ELEVENLABS_VOICE_ID": str,
    "ELEVENLABS_MODEL": str,
    "VOICE_DSP_ENABLED": bool,
    "AVATAR_IMAGE": str,
    "WWV_URL": str,
    "WWV_ENGINE_URL": str,
    "WWV_API_KEY": str,
}

BOOL_KEYS = {"VOICE_DSP_ENABLED"}
FLOAT_KEYS = {"TEMPERATURE", "KOKORO_SPEED", "KOKORO_PITCH", "KOKORO_DEPTH"}
KEY_KEYS = {k for k in SETTING_KEYS if k.endswith("_API_KEY")}


def _coerce(key: str, val):
    if key in BOOL_KEYS:
        return str(val).strip().lower() in ("1", "true", "yes", "on")
    if key in FLOAT_KEYS:
        return float(val)
    return str(val)


def _write_settings() -> None:
    SETTINGS_FILE.write_text(
        json.dumps(_SETTINGS, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _apply_runtime() -> None:
    """Push stored settings into live module globals (used after an update)."""
    g = globals()
    for key in SETTING_KEYS:
        if key in _SETTINGS:
            g[key] = _coerce(key, _SETTINGS[key])


def update_settings(patch: dict | None) -> dict:
    """Merge a patch into settings.json and apply it live. Empty API keys clear the stored key."""
    patch = patch or {}
    for key, val in patch.items():
        if key not in SETTING_KEYS:
            continue
        val = _coerce(key, val)
        if key in KEY_KEYS and not val:
            _SETTINGS.pop(key, None)
            continue
        if key in BOOL_KEYS:
            _SETTINGS[key] = str(val).lower() in ("1", "true", "yes", "on")
        else:
            _SETTINGS[key] = val
    _write_settings()
    _apply_runtime()
    return dict(_SETTINGS)


def settings_snapshot() -> dict:
    """Non-secret view of current settings for the CONFIG page."""
    return {
        "provider": BRAIN_PROVIDER,
        "providers": {
            name: {
                "name": meta["name"],
                "has_key": (not meta.get("needs_key", True)) or bool(
                    globals().get(meta["key"], "") or ""
                ),
                "key_label": meta.get("key_label", meta["key"]),
                "needs_key": meta.get("needs_key", True),
                "model": globals().get(meta.get("model", ""), ""),
            }
            for name, meta in PROVIDERS.items()
        },
        "models": {
            "openrouter": BRAIN_MODEL,
            "mistral": MISTRAL_MODEL,
            "groq": GROQ_MODEL,
            "gemini": GEMINI_MODEL,
            "nvidia": NVIDIA_MODEL,
            "kilo": KILO_MODEL,
            "agnes": AGNES_MODEL,
            "ovh": OVH_MODEL,
            "modelscope": MODELSCOPE_MODEL,
            "airforce": AIRFORCE_MODEL,
            "unorouter": UNOROUTER_MODEL,
        },
        "temperature": TEMPERATURE,
        "voice_engine": TTS_ENGINE,
        "voice": {
            "tts_voice": TTS_VOICE,
            "tts_rate": TTS_RATE,
            "tts_pitch": TTS_PITCH,
            "kokoro_voice": KOKORO_VOICE,
            "kokoro_speed": KOKORO_SPEED,
            "kokoro_pitch": KOKORO_PITCH,
            "kokoro_depth": KOKORO_DEPTH,
            "elevenlabs_voice_id": ELEVENLABS_VOICE_ID,
            "elevenlabs_model": ELEVENLABS_MODEL,
            "dsp": VOICE_DSP_ENABLED,
        },
        "avatar_image": AVATAR_IMAGE,
        "wwv_url": WWV_URL,
        "wwv_engine_url": WWV_ENGINE_URL,
        "wwv_api_key": WWV_API_KEY,
    }
