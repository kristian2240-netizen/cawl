# C.A.W.L. — Belisarius Cawl, Archmagos Dominus

A $0-runtime Mechanicus assistant. Python port of the original C.A.W.L. (speak_server.py + cawl.html) built on **FastAPI** + **Gradio** with a local **Vault** for long-term memory.

> **$0 Vow — Free Forever.** Free tiers, open models, no keys required to boot.

## Stack

- **Python 3.14**, managed with **uv**
- **FastAPI + uvicorn** — server endpoints (port 8123)
- **Custom frontend** — "The Breath of the Archmagos": a grimdark chat shell at `/` with an animated, breathing Belisarius figure (Cinzel/Jost/IBM Plex Mono, void/blood/rust palette, noise + scanline grime)
- **Gradio 6** — Conclave admin panel at `/ui`: Chat, Tasks, Research, Image Forge, Wiki
- **ElevenLabs (default) / edge-tts** — deep machine voice + DSP fallback
- **Pillow** — Image Forge (banner, seelbon, avatar, map, quote)
- **httpx** — DuckDuckGo search, URL fetch, OpenRouter brain
- **pydub / pandas / pyyaml** — DSP / data / config

## Run

```powershell
uv sync
uv run cawl
```

Open `http://127.0.0.1:8123` (frontend) or `http://127.0.0.1:8123/ui` (Conclave admin). Token-gated API routes need the `X-CAWL-Token` header — token is auto-generated in `.cawl-token`.

### Optional: wake the full brain

Providers are OpenAI-compatible and can be switched from the **CONFIG** button in the frontend (stored in `.cawl-data/settings.json`, applied live — no restart). Provider precedence when set to `auto`: OpenRouter → Kilo → Agnes → OVH → ModelScope → Api.Airforce → UnoRouter → Mistral → Groq → Gemini → NVIDIA → opencode CLI.

- **OpenRouter (recommended, $0):** set `OPENROUTER_API_KEY` in user env (`setx OPENROUTER_API_KEY "sk-..."`, then **open a new terminal**) or create a `.env` file in the project root with `OPENROUTER_API_KEY=sk-or-v1-...`. Uses `:free` models (gemma / gpt-oss / north-mini).
- **Kilo Code ($0, no key):** anonymous free tier works out of the box — free models auto-router (`kilo-auto/free`) with a ~200 req/hr/IP allowance. Optional `KILO_API_KEY` overrides the gateway. Base: `https://api.kilo.ai/api/gateway`.
- **Agnes AI ($0):** free-forever tier; `AGNES_API_KEY` from registration. Default model `agnes-2.5-flash` (512K ctx). Base: `https://apihub.agnes-ai.com/v1`.
- **OVH AI Endpoints ($0, no key):** anonymous free tier, ~2 req/min/model/IP. Base: `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`.
- **ModelScope ($0):** Alibaba free inference; `MODELSCOPE_API_KEY` (`ms-`-prefixed token). Default base `https://api-inference.modelscope.ai/v1` (international site — your token is site-scoped; use `.cn` only with a `modelscope.cn` token). Requires Alibaba Cloud account binding + real-name verification. ~2,000 req/day. Default model `Qwen/Qwen3.5-35B-A3B`.
- **Api.Airforce ($0):** free plan 1 RPM / 1,000 req/day; `AIRFORCE_API_KEY`. Base: `https://api.airforce/v1`.
- **UnoRouter ($0):** free lane ~1 req/min/user, models carry a `:free` suffix; `UNOROUTER_API_KEY` from https://unorouter.com/token. Base: `https://api.unorouter.com/v1`.
- **Mistral / Groq / Gemini / NVIDIA:** free API keys pasted into the CONFIG page (`MISTRAL_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `NVIDIA_API_KEY`). Defaults: `mistral-small-latest`, `llama-3.3-70b-versatile`, `gemini-3.5-flash`, `meta/llama-3.3-70b-instruct` — each overridable with a model field in CONFIG.
- **opencode CLI (local):** `npm install -g opencode-ai`, then `opencode auth login`. The brain routes through `opencode run --format json` — a full local tool-using loop with any provider you authenticate there.
- The startup banner prints `BRAIN: ONLINE` or `BRAIN: OFFLINE (echo)`; the frontend header shows the same. Without any key, C.A.W.L. runs a deterministic offline Mechanicus echo — honest, but not thinking.

### Voice

- **Kokoro-82M (local, free, Apache 2.0 — default when installed):** a fully offline neural voice running in-process via `kokoro-onnx` + onnxruntime. Install with `uv add kokoro-onnx` and fetch the model files:
  ```powershell
  uv add kokoro-onnx
  mkdir .cawl-data\tts
  curl.exe -L -o .cawl-data\tts\kokoro-v1.0.onnx  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  curl.exe -L -o .cawl-data\tts\voices-v1.0.bin    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  ```
  The startup banner prints `VOICE: Kokoro (local, free)`. Deep male voices: `am_onyx` (default — the deepest), `am_fenrir`, `am_puck` — override with `CAWL_KOKORO_VOICE`. Pitch is dropped ~2.5 semitones via `CAWL_KOKORO_PITCH` (default `1.16`, `1.0` = off).
- **ElevenLabs (when a key is present, $0 tier):** set `ELEVENLABS_API_KEY` (user env or `.env`) — the startup banner prints `VOICE: ElevenLabs (deep machine voice)`. Voice id default `nPczCjzI2devNBz1zQrb` (Brian), override with `ELEVENLABS_VOICE_ID`; model `eleven_multilingual_v2`, override with `ELEVENLABS_MODEL`.
- **edge-tts fallback:** free, no key — `en-US-AndrewMultilingualNeural`, deep via rate/pitch, optional ffmpeg DSP.
- **Engine order (auto):** Kokoro → ElevenLabs → edge-tts → transcript stub. Force one with `CAWL_TTS_ENGINE=kokoro|elevenlabs|edge`, or from the CONFIG page (engine + Kokoro voice/speed/pitch + DSP). Kokoro writes WAV; the others write MP3 (optional DSP via ffmpeg).
- **Avatar:** the default figure is an animated hooded-Archmagos SVG that turns its head and moves its mouth + vox waveform while speaking. Set `AVATAR_IMAGE` (CONFIG page) to an absolute PNG/JPG path to render that image instead (served at `/avatar`).

## Layout

```
CLAUDE.md                  Layer 1 — identity / persona / rules
vault/                     Layer 2 — long-term memory (markdown)
  01 Identity/ 02 Memory/ 03 Research/ 04 Game Strategy/
  05 Projects/ 06 Journal/ 99 Templates/ + Index.md
lore/                      Layer 5 — cawl-lore, strategy, self-knowledge
llm-wiki.md                Layer 5 — self-improvement memory (200-cap)
src/test_project/
  server.py                Layer 3 — FastAPI endpoints (the speak_server.py port)
  static/                  Layer 4 — custom frontend: index.html, style.css, app.js
  ui.py                    Layer 4 — Gradio Conclave panel (mounted at /ui)
  brain.py                 Brain router + orchestrator + tool protocol
  priests.py               Layer 5b — Verifier, Scribe, Trazyn, Optikon
  voice.py                 kokoro / elevenlabs / edge-tts + DSP
  settings.py              CONFIG page service (live settings payload + updates)
  images.py                Pillow Image Forge
  tools.py                 sandbox FS, DuckDuckGo, URL fetch, terminal
  scheduler.py             daily/hourly/weekly/once tasks
  vault.py / wiki.py       memory APIs
tests/                     smoke tests (no network)
```

## API (port 8123)

`/self /say /read /fs /search /fetch /chat /or/chat /oc/chat /settings /avatar` are open.
`/write /exec /token /log /research/save /schedule /img /wiki/* /notion/*` are token-gated (`X-CAWL-Token`).

## Tests

```powershell
uv run python -m unittest discover -s tests -v
```
