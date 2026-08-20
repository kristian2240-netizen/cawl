---
type: project
status: active
updated: 2026-08-13
---

# Interface — C.A.W.L. Endpoints

FastAPI server on port 8123. Token-gated endpoints require `X-CAWL-Token` matching `.cawl-token`.

| Endpoint | Purpose | Gated |
|---|---|---|
| `/say` | Voice synthesis (edge-tts + DSP) → audio file | no |
| `/read` | Sandboxed file read | no (sandboxed to project) |
| `/fs` | List files | no |
| `/write` | Write file inside sandbox | yes |
| `/exec` | Run terminal command | yes |
| `/token` | Return current token | yes |
| `/self` | Identity / persona info | no |
| `/search` | DuckDuckGo web search | no |
| `/fetch` | Read a URL | no |
| `/notion/search`, `/notion/create`, `/notion/update` | Notion bridge | yes |
| `/log` | Append journal entry | yes |
| `/schedule` | Task scheduler (daily/hourly/weekly/once) | yes |
| `/img` | Pillow image forge | yes |
| `/wiki/read`, `/wiki/write` | LLM wiki (200-cap) | yes |
| `/research/save` | Save research finding | yes |
| `/or/chat` | OpenRouter chat proxy | no |
| `/oc/chat` | opencode CLI proxy | no |
