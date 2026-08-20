---
type: research
updated: 2026-08-13
---

# Research Log

Format: one finding per line block. Every entry carries a confidence label.

## 2026-08-13 — C.A.W.L. recreated on Windows (Python)

- **Finding:** The original C.A.W.L. was a JS + Python hybrid (speak_server.py + cawl.html). The Python reimplementation uses FastAPI + Gradio. Confidence: HIGH
- **Finding:** Gradio 6.x ships `gr.Blocks` with tabs — enough to host Chat, Tasks, Research, and Conclave in one shell. Confidence: HIGH
- **Finding:** `edge-tts` provides free neural voices without keys. DSP via pydub + ffmpeg. Confidence: HIGH
- **Finding:** OpenRouter serves `:free` tier models (deepseek, gemma, nano-vlm) for the brain and priests. Confidence: MEDIUM (free tiers rotate)

<!-- Append dated findings. Label confidence HIGH / MEDIUM / LOW. -->
