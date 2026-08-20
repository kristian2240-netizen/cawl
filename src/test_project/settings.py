"""C.A.W.L. settings service — payload for the CONFIG page + live updates."""

from __future__ import annotations

from . import config, voice


def _kokoro_voices() -> list[str]:
    try:
        kokoro = voice._get_kokoro()
        if kokoro is None:
            return []
        return kokoro.get_voices()
    except Exception:  # noqa: BLE001
        return []


def payload() -> dict:
    snap = config.settings_snapshot()
    snap["kokoro_voices"] = _kokoro_voices()
    snap["voice_active"] = voice.active_engine()
    return snap


def update(patch: dict) -> dict:
    config.update_settings(patch)
    return payload()
