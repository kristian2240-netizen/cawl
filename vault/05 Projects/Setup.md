---
type: project
status: active
updated: 2026-08-13
---

# Setup — Project Bootstrap

- **Stack:** Python 3.14, uv, Gradio 6, FastAPI, uvicorn, httpx, Pillow, pydub, edge-tts, pandas.
- **Run:** `uv run cawl` (starts FastAPI :8123 with Gradio mounted at `/`).
- **Token:** `.cawl-token` auto-generated at first boot; send as `X-CAWL-Token`.
- **Sandbox:** All file access is rooted at the project directory. Read-only by design.
