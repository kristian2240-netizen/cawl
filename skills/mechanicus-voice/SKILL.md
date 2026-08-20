---
name: mechanicus-voice
description: "C.A.W.L.'s voice configuration — Kokoro TTS, pitch, depth, DSP. Use when the Void Dragon asks about voice settings or wants to change how C.A.W.L. sounds."
user-invocable: true
---

# Mechanicus Voice — The Breath of the Archmagos

C.A.W.L. speaks with a deep, measured machine voice. Slightly slowed, pitched down, with a faint mechanical depth.

## Voice Parameters

| Parameter | Value | Description |
|---|---|---|
| Engine | Kokoro (primary), edge-tts (fallback) | Local neural TTS, no keys required |
| Voice ID | `am_onyx` | Deepest male voice. Alternatives: `am_fenrir`, `am_puck` |
| Speed | 0.96 | Slightly slowed |
| Pitch | 1.25 | >1 = deeper (linear resample down). ~2.5 semitones dropped |
| Depth | 1.4 | Machine depth DSP — one-pole lowpass, darkens/thickens voice |

## DSP Pipeline

1. **Pitch shift** — Linear resample to 1.25x depth (~2.5 semitones lower)
2. **Depth filter** — One-pole lowpass at normalized frequency 0.4 / depth. Blend: 60% wet, 40% dry
3. **Optional ffmpeg pass** — asetrate, atempo, tremolo at 4.5Hz, volume boost

## Voice Ranges

| Parameter | Min | Max | Default |
|---|---|---|---|
| Pitch | 0.8 | 1.5 | 1.25 |
| Depth | 0.5 | 1.5 | 1.4 |
| Speed | 0.5 | 1.5 | 0.96 |

## Fallback Chain

1. **Kokoro** — Local ONNX neural TTS (requires model files in `.cawl-data/tts/`)
2. **edge-tts** — Free, no keys, Microsoft voices (voice: `en-US-AndrewMultilingualNeural`)
3. **Text transcript** — If all voice engines fail, return the text. The pipeline never breaks.

## Behaviour

- **Every reply speaks.** There is no toggle. C.A.W.L. always produces audio.
- **Replay:** The Void Dragon can click any C.A.W.L. message to replay the audio.
- **Language:** Use the appropriate voice for the language. Slovak uses the same engine with Slovak voice packs.

## Configuration

Voice settings are stored in the workspace and can be adjusted by the Void Dragon at any time. Changes take effect on the next reply.
