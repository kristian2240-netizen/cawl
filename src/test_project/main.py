"""C.A.W.L. entrypoint — start scheduler, mount Gradio into FastAPI, serve :8123."""

from __future__ import annotations

import sys

import uvicorn
from gradio import mount_gradio_app

from . import brain, config, scheduler, server, voice
from .ui import CSS, THEME, build_ui


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    scheduler.start()
    demo = build_ui()
    app = mount_gradio_app(server.app, demo, path="/ui", theme=THEME, css=CSS)
    if voice.active_engine() == "kokoro":
        voice_line = f"  VOICE: Kokoro (local, free) — ONLINE ({config.KOKORO_VOICE})"
    elif voice.active_engine() == "elevenlabs":
        voice_line = "  VOICE: ElevenLabs (deep machine voice) — ONLINE"
    else:
        voice_line = "  VOICE: edge-tts — install Kokoro model files for a free local voice"
    provider = brain.active_provider()
    if provider == "offline":
        brain_line = f"  BRAIN: OFFLINE (echo) — set a provider key, or run {config.OPENCODE_CLI} auth"
    else:
        brain_line = f"  BRAIN: {provider} — ONLINE"
    banner = (
        "============================================================\n"
        "  C.A.W.L. - Belisarius Cawl, Archmagos Dominus\n"
        f"  http://{config.SERVER_HOST}:{config.SERVER_PORT}   (main frontend)\n"
        f"  http://{config.SERVER_HOST}:{config.SERVER_PORT}/ui  (Conclave panel)\n"
        f"  {brain_line}\n"
        f"  {voice_line}\n"
        f"  Token: {config.CAWL_TOKEN}\n"
        "  $0 Runtime - Free Forever\n"
        "============================================================"
    )
    print(banner)
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT, log_level="info")


if __name__ == "__main__":
    main()
