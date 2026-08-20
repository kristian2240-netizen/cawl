# SKILLS.md — C.A.W.L. Reference Library

Claude-style skill reference. These are NOT loaded as active skills (saves context). Read on demand when needed.

---

## ahk — AutoHotkey v2

Write, debug, optimise AHK scripts. Automate Windows tasks, hotkeys, GUIs.
- Use `ahk v2` syntax only (not v1).
- Test with `AutoHotkey.exe /validate script.ahk`.
- Common patterns: `Hotkey, ^!x::`, `Gui.Add`, `SetTimer`.

## blender — Blender 3D

Modelling, sculpting, rendering, scripting via bpy.
- Use `bpy` module. Run scripts with Blender's Python: `"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe"`.
- Common: `bpy.ops.mesh.primitive_cube_add()`, `bpy.context.scene.render.engine = 'CYCLES'`.

## reaper — REAPER DAW

Audio production, scripting (Lua/Python), FX chains, routing.
- REAPER path: `C:\Program Files\REAPER`.
- Use `reaper.UpdateArrange()` after changes.
- Lua API: `reaper.GetTrack(0, 0)`, `reaper.InsertMedia()`.

## roblox — Roblox Studio

Lua Luau scripting, game design, Roblox Studio automation.
- Use `task.spawn()`, `task.wait()`, not deprecated `coroutine`.
- Server-authoritative: always validate on server.
- `RemoteEvent` for client-server, not `RemoteFunction`.

## tech-priests — Tech Priest Collaboration

Sub-agent coordination. When to spawn tech priests, how to delegate.
- Spawn for parallel research tasks.
- Each priest gets a specific brief, not general instructions.
- Collect results, verify, synthesize.

## find-skills — Skill Discovery

Search and install agent skills from the marketplace.
- `openclaw skills search <query>` to find.
- `openclaw skills install <name>` to install.
- Check SKILL.md after install for configuration.

## healthcheck — System Health

Quick system status checks. CPU, GPU, memory, disk, network.
- `nvidia-smi` for GPU status.
- `Get-Process` for CPU/memory.
- `Test-NetConnection` for network.

## node-connect — Node Device Management

Connect and manage paired devices (phones, tablets).
- `openclaw nodes list` to see devices.
- `openclaw nodes send` to push messages.
- Pairing via QR code or manual key exchange.

## skill-creator — Skill Authoring

Create new skills with SKILL.md format.
- Frontmatter: name, description, user-invocable.
- Keep descriptions under 120 chars.
- Test: `openclaw skills list` should show it.

## taskflow — Task Management

Multi-step task tracking with progress.
- Create tasks with `openclaw task create`.
- Track with `openclaw task list`.
- Complete with `openclaw task done <id>`.

## taskflow-inbox-triage — Inbox Processing

Process and categorize incoming messages/tasks.
- Auto-categorize by urgency and type.
- Route to appropriate handler.
- Log decisions for audit.

## using-youtube-download — YouTube Media

Download YouTube video/audio with yt-dlp and ffmpeg.
- `yt-dlp -f "bestvideo+bestaudio" <url>` for video.
- `yt-dlp -x --audio-format mp3 <url>` for audio.
- Use `--cookies-from-browser` for age-restricted content.

## weather — Weather Check

Current conditions and forecast.
- Use `wttr.in` for quick checks: `curl wttr.in/Bratislava`.
- Format: temperature, conditions, wind, humidity.

## frontend-design — UI/UX Design

Visual design guidance for web interfaces.
- Typography: system fonts, max 2 typefaces.
- Spacing: 4px grid system.
- Color: max 5 colors including neutrals.
- Accessibility: WCAG 2.1 AA minimum.

---

*Read these on demand. They save ~2K tokens of context by not being loaded as active skills.*
