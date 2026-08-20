"""C.A.W.L. Voice Engine — Kokoro (local, free) + ElevenLabs + edge-tts (Layer 3, Voice).

Engine order (auto): Kokoro when the local model is present, else ElevenLabs when a
key exists, else edge-tts, else a deterministic transcript stub. Deep machine voice.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

from . import config

try:
    import edge_tts  # noqa: PLC0415
except Exception:  # noqa: BLE001 — edge-tts may be absent
    edge_tts = None  # type: ignore[assignment]


class VoiceError(Exception):
    pass


# ---------------------------------------------------------------------------
# Kokoro — local, free, Apache 2.0 (kokoro-onnx runtime)
# ---------------------------------------------------------------------------

_KOKORO_LOCK = threading.Lock()
_KOKORO = None
_KOKORO_TRYED = False


def _kokoro_available() -> bool:
    """True if the kokoro-onnx package and model files are present."""
    return Path(config.KOKORO_MODEL).exists() and Path(config.KOKORO_VOICES).exists()


def _get_kokoro():
    """Lazy singleton Kokoro runtime (thread-safe). None when unavailable."""
    global _KOKORO, _KOKORO_TRYED
    if _KOKORO is not None:
        return _KOKORO
    if _KOKORO_TRYED:
        return None
    with _KOKORO_LOCK:
        if _KOKORO is not None or _KOKORO_TRYED:
            return _KOKORO
        _KOKORO_TRYED = True
        try:
            from kokoro_onnx import Kokoro  # noqa: PLC0415
        except Exception:  # noqa: BLE001
            return None
        try:
            _KOKORO = Kokoro(str(config.KOKORO_MODEL), str(config.KOKORO_VOICES))
        except Exception:  # noqa: BLE001
            _KOKORO = None
        return _KOKORO


def _apply_depth(samples, rate):
    """Machine depth DSP: one-pole lowpass that darkens/thickens the voice.

    KOKORO_DEPTH = 1.0 is neutral (cutoff well above speech), >1 darkens and
    adds weight, <1 brightens. Pure numpy — no ffmpeg needed.
    """
    depth = config.KOKORO_DEPTH
    if depth <= 0:
        return samples
    # cutoff Hz: 6k at depth 1.0, ~1.2k at 1.5, ~18k at 0.5
    cutoff = 6000.0 / max(0.3, depth)
    a = 1.0 - np.exp(-2.0 * np.pi * cutoff / rate)
    # one-pole lowpass y[n] = y[n-1] + a*(x[n] - y[n-1])
    y = np.empty_like(samples)
    prev = 0.0
    for i, x in enumerate(samples):
        prev += a * (x - prev)
        y[i] = prev
    # blend a touch of the dry signal back so it stays clear, scaled by depth
    return y * (0.55 + 0.3 * min(depth, 1.5)) + samples * 0.2


def _synth_kokoro(text: str, out: Path, voice: str) -> None:
    kokoro = _get_kokoro()
    if kokoro is None:
        raise VoiceError("Kokoro unavailable — install kokoro-onnx and download the model files")
    samples, rate = kokoro.create(text, voice=voice, speed=config.KOKORO_SPEED, lang="en-us")
    # deepen: linear-resample downward (KOKORO_PITCH > 1 lowers pitch; output is wav)
    factor = max(1.0, config.KOKORO_PITCH)
    if factor > 1.0:
        n = max(1, int(len(samples) * factor))
        samples = np.interp(
            np.linspace(0.0, 1.0, n),
            np.linspace(0.0, 1.0, len(samples)),
            samples,
        )
    samples = _apply_depth(samples, rate)
    pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------------------
# ElevenLabs
# ---------------------------------------------------------------------------


def _synth_eleven(text: str, out: Path, voice_id: str) -> None:
    """ElevenLabs TTS — deep cinematic machine voice. Returns via httpx (synchronous)."""
    import httpx  # noqa: PLC0415

    if not config.ELEVENLABS_API_KEY:
        raise VoiceError("ELEVENLABS_API_KEY not set")
    resp = httpx.post(
        f"{config.ELEVENLABS_BASE}/text-to-speech/{voice_id}",
        headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        params={"output_format": "mp3_44100_128"},
        json={
            "text": text,
            "model_id": config.ELEVENLABS_MODEL,
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.4},
        },
        timeout=90,
    )
    resp.raise_for_status()
    out.write_bytes(resp.content)


# ---------------------------------------------------------------------------
# edge-tts
# ---------------------------------------------------------------------------


async def _synth_edge(text: str, out: Path, voice: str) -> None:
    if edge_tts is None:
        raise VoiceError("edge-tts is not installed")
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=config.TTS_RATE,
        pitch=config.TTS_PITCH,
    )
    await communicate.save(str(out))


# ---------------------------------------------------------------------------
# Engine routing
# ---------------------------------------------------------------------------


def _pick_engine() -> tuple[str, str]:
    """Return (engine, voice). auto: kokoro > elevenlabs > edge."""
    engine = config.TTS_ENGINE
    if engine == "auto":
        if _kokoro_available():
            return "kokoro", config.KOKORO_VOICE
        engine = "elevenlabs" if config.ELEVENLABS_API_KEY else "edge"
    if engine == "kokoro":
        if not _kokoro_available():
            raise VoiceError("Kokoro model files missing — set CAWL_KOKORO_MODEL/CAWL_KOKORO_VOICES")
        return "kokoro", config.KOKORO_VOICE
    if engine == "elevenlabs" and not config.ELEVENLABS_API_KEY:
        raise VoiceError("ELEVENLABS_API_KEY not set — add it or set CAWL_TTS_ENGINE=edge/kokoro")
    if engine == "elevenlabs":
        return "elevenlabs", config.ELEVENLABS_VOICE_ID
    return "edge", config.TTS_VOICE


def _apply_dsp(src: Path, dst: Path) -> bool:
    """Pitch down + slow + tremolo via ffmpeg filters. Returns False if ffmpeg is absent."""
    if not shutil.which("ffmpeg"):
        return False
    # pitch down ~2 semitones, slow to 92%, add gentle tremolo
    filters = (
        "asetrate=44100*0.891,aresample=44100,atempo=1.0/0.891*0.92,atempo=1.09,"
        "tremolo=f=4.5:d=0.35,volume=0.95"
    )
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", filters, str(dst)],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def _stub_synth(text: str, out: Path) -> None:
    """Deterministic fallback: write a text transcript so the pipeline never breaks."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    out.with_suffix(".txt").write_text(
        f"# C.A.W.L. Voice (stub — no TTS engine available)\n\n{stamp}\n\n{text}\n",
        encoding="utf-8",
    )


def synthesize(text: str, *, voice: str | None = None, dsp: bool | None = None) -> dict:
    """Return {audio: path, format: 'mp3'|'wav'|'txt', transcript: text, note: engine}.

    Kokoro writes WAV; ElevenLabs/edge write MP3 (with optional ffmpeg DSP). Any
    engine failure degrades to a transcript stub — the pipeline never breaks.
    """
    import asyncio  # noqa: PLC0415

    dsp = config.VOICE_DSP_ENABLED if dsp is None else dsp
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    try:
        if voice:
            engine, arg = "edge", voice
        else:
            engine, arg = _pick_engine()

        if engine == "kokoro":
            out = config.AUDIO_DIR / f"say-{stamp}.wav"
            _synth_kokoro(text, out, arg)
            return {"audio": out, "format": "wav", "transcript": text,
                    "note": f"Kokoro ({arg})"}

        out = config.AUDIO_DIR / f"say-{stamp}.mp3"
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.mp3"
            if engine == "elevenlabs":
                _synth_eleven(text, raw, arg)
                note = f"ElevenLabs ({config.ELEVENLABS_VOICE_ID})"
            else:
                if edge_tts is None:
                    raise VoiceError("edge-tts is not installed")
                asyncio.run(_synth_edge(text, raw, arg))
                note = f"edge-tts ({arg})"
            if dsp and _apply_dsp(raw, out):
                return {"audio": out, "format": "mp3", "transcript": text,
                        "note": note + " + DSP"}
            raw.replace(out)
            return {"audio": out, "format": "mp3", "transcript": text, "note": note}
    except Exception as exc:  # noqa: BLE001
        out = out if "out" in locals() else config.AUDIO_DIR / f"say-{stamp}.mp3"
        _stub_synth(text, out)
        return {"audio": out.with_suffix(".txt"), "format": "txt", "transcript": text,
                "note": f"TTS unavailable ({type(exc).__name__}: {exc}) — transcript saved"}


def active_engine() -> str:
    """Name of the engine that would be used right now (for /self and the banner)."""
    try:
        return _pick_engine()[0]
    except VoiceError:
        return "edge"
